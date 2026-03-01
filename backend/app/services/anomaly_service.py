"""
Anomaly detection service for identifying abnormal API behavior.
"""
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from statistics import mean, stdev
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monitoring_log import MonitoringLog, CheckStatus
from app.models.api import ApiEndpoint


class AnomalyService:
    """Service for detecting anomalies in API monitoring data."""
    
    # Threshold for anomaly detection
    Z_SCORE_THRESHOLD = 2.5  # Standard deviations from mean
    MIN_SAMPLES_FOR_ANOMALY = 10  # Minimum logs needed for statistical analysis
    RESPONSE_TIME_SPIKE_MULTIPLIER = 3  # Multiple of average for response time spikes
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def detect_anomalies(
        self,
        api_endpoint_id: int,
        window_hours: int = 24
    ) -> List[Tuple[MonitoringLog, float]]:
        """Detect anomalies in monitoring logs using statistical analysis."""
        cutoff_time = datetime.utcnow() - timedelta(hours=window_hours)
        
        result = await self.db.execute(
            select(MonitoringLog)
            .where(
                MonitoringLog.api_endpoint_id == api_endpoint_id,
                MonitoringLog.checked_at >= cutoff_time,
                MonitoringLog.response_time.isnot(None)
            )
            .order_by(MonitoringLog.checked_at.desc())
            .limit(100)
        )
        
        logs = list(result.scalars().all())
        
        if len(logs) < self.MIN_SAMPLES_FOR_ANOMALY:
            return []
        
        # Extract response times
        response_times = [log.response_time for log in logs if log.response_time is not None]
        
        if len(response_times) < self.MIN_SAMPLES_FOR_ANOMALY:
            return []
        
        # Calculate statistics
        avg_response_time = mean(response_times)
        
        # Calculate standard deviation
        if len(response_times) > 1:
            std_dev = stdev(response_times)
        else:
            std_dev = 0
        
        # Detect anomalies using z-score
        anomalies = []
        
        for log in logs:
            if log.response_time is None:
                continue
            
            # Z-score based detection
            if std_dev > 0:
                z_score = (log.response_time - avg_response_time) / std_dev
            else:
                z_score = 0
            
            # Check if it's an anomaly (z-score exceeds threshold)
            if abs(z_score) > self.Z_SCORE_THRESHOLD:
                anomalies.append((log, z_score))
                # Mark the log as anomaly in the database
                log.is_anomaly = True
                log.anomaly_score = z_score
        
        if anomalies:
            await self.db.flush()
        
        return anomalies
    
    async def check_response_time_anomaly(
        self,
        api_endpoint_id: int,
        current_response_time: float
    ) -> Tuple[bool, Optional[float]]:
        """Check if a response time is anomalous based on historical data."""
        # Get recent response times (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        result = await self.db.execute(
            select(MonitoringLog)
            .where(
                MonitoringLog.api_endpoint_id == api_endpoint_id,
                MonitoringLog.checked_at >= cutoff_time,
                MonitoringLog.response_time.isnot(None),
                MonitoringLog.status == CheckStatus.SUCCESS
            )
            .order_by(MonitoringLog.checked_at.desc())
            .limit(50)
        )
        
        logs = list(result.scalars().all())
        
        if len(logs) < self.MIN_SAMPLES_FOR_ANOMALY:
            return False, None
        
        response_times = [log.response_time for log in logs if log.response_time is not None]
        
        if len(response_times) < self.MIN_SAMPLES_FOR_ANOMALY:
            return False, None
        
        avg_response_time = mean(response_times)
        
        if len(response_times) > 1:
            std_dev = stdev(response_times)
        else:
            std_dev = 0
        
        if std_dev > 0:
            z_score = (current_response_time - avg_response_time) / std_dev
        else:
            z_score = 0
        
        is_anomaly = abs(z_score) > self.Z_SCORE_THRESHOLD
        
        return is_anomaly, z_score if is_anomaly else None
    
    async def get_response_time_baseline(
        self,
        api_endpoint_id: int,
        window_hours: int = 24
    ) -> Optional[dict]:
        """Get response time baseline statistics for an endpoint."""
        cutoff_time = datetime.utcnow() - timedelta(hours=window_hours)
        
        result = await self.db.execute(
            select(MonitoringLog)
            .where(
                MonitoringLog.api_endpoint_id == api_endpoint_id,
                MonitoringLog.checked_at >= cutoff_time,
                MonitoringLog.response_time.isnot(None),
                MonitoringLog.status == CheckStatus.SUCCESS
            )
        )
        
        logs = list(result.scalars().all())
        
        if len(logs) < 5:
            return None
        
        response_times = [log.response_time for log in logs if log.response_time is not None]
        
        if not response_times:
            return None
        
        avg = mean(response_times)
        
        # Calculate min/max excluding outliers
        sorted_times = sorted(response_times)
        min_time = sorted_times[0]
        max_time = sorted_times[-1]
        
        return {
            "average": avg,
            "min": min_time,
            "max": max_time,
            "std_dev": stdev(response_times) if len(response_times) > 1 else 0,
            "sample_count": len(response_times),
            "p50": self._percentile(response_times, 50),
            "p95": self._percentile(response_times, 95),
            "p99": self._percentile(response_times, 99),
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of a list."""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        
        if index >= len(sorted_data):
            index = len(sorted_data) - 1
        
        return sorted_data[index]
    
    async def is_degradation(
        self,
        api_endpoint_id: int,
        current_avg: float,
        window_hours: int = 24
    ) -> bool:
        """Check if there's a performance degradation compared to historical data."""
        # Get historical baseline
        historical_cutoff = datetime.utcnow() - timedelta(hours=window_hours * 7)  # 7 days
        current_cutoff = datetime.utcnow() - timedelta(hours=window_hours)
        
        # Get historical data (older than window)
        result = await self.db.execute(
            select(MonitoringLog)
            .where(
                MonitoringLog.api_endpoint_id == api_endpoint_id,
                MonitoringLog.checked_at < historical_cutoff,
                MonitoringLog.checked_at >= historical_cutoff - timedelta(hours=window_hours),
                MonitoringLog.response_time.isnot(None),
                MonitoringLog.status == CheckStatus.SUCCESS
            )
        )
        historical_logs = list(result.scalars().all())
        
        if len(historical_logs) < 10:
            return False
        
        historical_times = [log.response_time for log in historical_logs if log.response_time]
        
        if not historical_times:
            return False
        
        historical_avg = mean(historical_times)
        
        # If current average is 50% higher than historical, it's degradation
        if historical_avg > 0:
            degradation_ratio = current_avg / historical_avg
            
            if degradation_ratio > 1.5:
                return True
        
        return False
