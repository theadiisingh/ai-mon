"""
Monitoring service for managing monitoring logs and checks.
"""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monitoring_log import MonitoringLog, CheckStatus
from app.models.api import ApiEndpoint
from app.schemas.monitoring_schema import MonitoringLogCreate, CheckSummary


class MonitoringService:
    """Service for monitoring log operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_log(self, log_data: MonitoringLogCreate) -> MonitoringLog:
        """Create a new monitoring log entry."""
        db_log = MonitoringLog(
            api_endpoint_id=log_data.api_endpoint_id,
            user_id=log_data.user_id,
            status=log_data.status,
            status_code=log_data.status_code,
            response_time=log_data.response_time,
            error_message=log_data.error_message,
            is_anomaly=log_data.is_anomaly,
            anomaly_score=log_data.anomaly_score,
            request_method=log_data.request_method,
            request_url=log_data.request_url,
        )
        
        self.db.add(db_log)
        await self.db.flush()
        await self.db.refresh(db_log)
        
        # Update endpoint stats after creating the log
        from app.services.api_service import ApiService
        api_service = ApiService(self.db)
        is_success = log_data.status == CheckStatus.SUCCESS
        await api_service.update_endpoint_stats(
            endpoint_id=log_data.api_endpoint_id,
            status_code=log_data.status_code,
            response_time=log_data.response_time,
            is_success=is_success
        )
        
        return db_log
    
    async def get_log_by_id(
        self, 
        log_id: int, 
        user_id: int
    ) -> Optional[MonitoringLog]:
        """Get a monitoring log by ID."""
        result = await self.db.execute(
            select(MonitoringLog).where(
                MonitoringLog.id == log_id,
                MonitoringLog.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def list_logs(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        api_endpoint_id: Optional[int] = None,
        status: Optional[CheckStatus] = None,
        is_anomaly: Optional[bool] = None,
    ) -> List[MonitoringLog]:
        """List monitoring logs for a user."""
        query = select(MonitoringLog).where(MonitoringLog.user_id == user_id)
        
        if api_endpoint_id is not None:
            query = query.where(MonitoringLog.api_endpoint_id == api_endpoint_id)
        
        if status is not None:
            query = query.where(MonitoringLog.status == status)
        
        if is_anomaly is not None:
            query = query.where(MonitoringLog.is_anomaly == is_anomaly)
        
        query = query.offset(skip).limit(limit).order_by(MonitoringLog.checked_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_logs(
        self,
        user_id: int,
        api_endpoint_id: Optional[int] = None,
        status: Optional[CheckStatus] = None,
    ) -> int:
        """Count monitoring logs for a user."""
        query = select(func.count(MonitoringLog.id)).where(
            MonitoringLog.user_id == user_id
        )
        
        if api_endpoint_id is not None:
            query = query.where(MonitoringLog.api_endpoint_id == api_endpoint_id)
        
        if status is not None:
            query = query.where(MonitoringLog.status == status)
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def get_recent_logs(
        self,
        api_endpoint_id: int,
        limit: int = 10
    ) -> List[MonitoringLog]:
        """Get recent logs for an API endpoint."""
        result = await self.db.execute(
            select(MonitoringLog)
            .where(MonitoringLog.api_endpoint_id == api_endpoint_id)
            .order_by(MonitoringLog.checked_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_logs_for_analysis(
        self,
        api_endpoint_id: int,
        hours: int = 24,
        limit: int = 50
    ) -> List[MonitoringLog]:
        """Get logs for AI analysis."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.db.execute(
            select(MonitoringLog)
            .where(
                and_(
                    MonitoringLog.api_endpoint_id == api_endpoint_id,
                    MonitoringLog.checked_at >= cutoff_time
                )
            )
            .order_by(MonitoringLog.checked_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_check_summary(
        self,
        api_endpoint_id: int,
        hours: int = 24
    ) -> CheckSummary:
        """Get check summary for a time period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.db.execute(
            select(MonitoringLog).where(
                and_(
                    MonitoringLog.api_endpoint_id == api_endpoint_id,
                    MonitoringLog.checked_at >= cutoff_time
                )
            )
        )
        logs = list(result.scalars().all())
        
        if not logs:
            return CheckSummary(
                total_checks=0,
                successful_checks=0,
                failed_checks=0,
                timeout_checks=0,
                error_checks=0,
                avg_response_time=0.0,
                uptime_percentage=100.0,
                anomaly_count=0
            )
        
        successful = [l for l in logs if l.status == CheckStatus.SUCCESS]
        failed = [l for l in logs if l.status == CheckStatus.FAILURE]
        timeouts = [l for l in logs if l.status == CheckStatus.TIMEOUT]
        errors = [l for l in logs if l.status == CheckStatus.ERROR]
        anomalies = [l for l in logs if l.is_anomaly]
        
        response_times = [l.response_time for l in logs if l.response_time is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else None
        max_response_time = max(response_times) if response_times else None
        
        uptime = len(successful) / len(logs) * 100 if logs else 100.0
        
        return CheckSummary(
            total_checks=len(logs),
            successful_checks=len(successful),
            failed_checks=len(failed),
            timeout_checks=len(timeouts),
            error_checks=len(errors),
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            uptime_percentage=uptime,
            anomaly_count=len(anomalies)
        )
    
    async def get_failed_checks_count(
        self,
        api_endpoint_id: int,
        minutes: int = 5
    ) -> int:
        """Get count of consecutive failed checks in the last N minutes."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        result = await self.db.execute(
            select(func.count(MonitoringLog.id)).where(
                and_(
                    MonitoringLog.api_endpoint_id == api_endpoint_id,
                    MonitoringLog.checked_at >= cutoff_time,
                    MonitoringLog.status.in_([CheckStatus.FAILURE, CheckStatus.ERROR, CheckStatus.TIMEOUT])
                )
            )
        )
        return result.scalar() or 0
    
    async def mark_logs_as_anomaly(
        self,
        log_ids: List[int],
        anomaly_score: float
    ) -> bool:
        """Mark logs as anomalies."""
        result = await self.db.execute(
            select(MonitoringLog).where(MonitoringLog.id.in_(log_ids))
        )
        logs = result.scalars().all()
        
        for log in logs:
            log.is_anomaly = True
            log.anomaly_score = anomaly_score
        
        await self.db.flush()
        return True
    
    async def delete_old_logs(self, days: int = 30) -> int:
        """Delete logs older than specified days."""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(MonitoringLog).where(MonitoringLog.checked_at < cutoff_time)
        )
        logs = result.scalars().all()
        
        count = len(logs)
        
        for log in logs:
            await self.db.delete(log)
        
        await self.db.flush()
        return count
    
    async def get_logs(
        self,
        user_id: int,
        api_endpoint_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 50,
        status_filter: Optional[str] = None
    ) -> tuple[List[MonitoringLog], int]:
        """Get monitoring logs with pagination."""
        query = select(MonitoringLog).where(MonitoringLog.user_id == user_id)
        
        if api_endpoint_id is not None:
            query = query.where(MonitoringLog.api_endpoint_id == api_endpoint_id)
        
        if status_filter:
            try:
                status = CheckStatus(status_filter)
                query = query.where(MonitoringLog.status == status)
            except ValueError:
                pass  # Ignore invalid status filter
        
        # Get total count
        count_query = select(func.count(MonitoringLog.id)).where(
            MonitoringLog.user_id == user_id
        )
        if api_endpoint_id is not None:
            count_query = count_query.where(MonitoringLog.api_endpoint_id == api_endpoint_id)
        if status_filter:
            try:
                status = CheckStatus(status_filter)
                count_query = count_query.where(MonitoringLog.status == status)
            except ValueError:
                pass
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated results
        skip = (page - 1) * page_size
        query = query.offset(skip).limit(page_size).order_by(MonitoringLog.checked_at.desc())
        
        result = await self.db.execute(query)
        logs = list(result.scalars().all())
        
        return logs, total
    
    async def get_log(
        self,
        log_id: int,
        user_id: int
    ) -> Optional[MonitoringLog]:
        """Get a specific monitoring log."""
        result = await self.db.execute(
            select(MonitoringLog).where(
                MonitoringLog.id == log_id,
                MonitoringLog.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_metrics(
        self,
        user_id: int,
        api_endpoint_id: Optional[int] = None,
        hours: int = 24
    ) -> dict:
        """Get metrics overview."""
        from app.schemas.monitoring_schema import MetricsResponse
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(MonitoringLog).where(
            MonitoringLog.user_id == user_id,
            MonitoringLog.checked_at >= cutoff_time
        )
        
        if api_endpoint_id is not None:
            query = query.where(MonitoringLog.api_endpoint_id == api_endpoint_id)
        
        result = await self.db.execute(query)
        logs = list(result.scalars().all())
        
        if not logs:
            return MetricsResponse(
                total_checks=0,
                successful_checks=0,
                failed_checks=0,
                uptime_percentage=100.0,
                avg_response_time=0.0,
                error_rate=0.0,
                avg_response_time_p95=0.0,
                anomaly_count=0
            )
        
        successful = [l for l in logs if l.status == CheckStatus.SUCCESS]
        failed = [l for l in logs if l.status in [CheckStatus.FAILURE, CheckStatus.ERROR, CheckStatus.TIMEOUT]]
        anomalies = [l for l in logs if l.is_anomaly]
        
        response_times = [l.response_time for l in logs if l.response_time is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Calculate P95
        sorted_times = sorted(response_times) if response_times else []
        p95_index = int(len(sorted_times) * 0.95) if sorted_times else 0
        avg_response_time_p95 = sorted_times[p95_index] if sorted_times else 0
        
        uptime = len(successful) / len(logs) * 100 if logs else 100.0
        error_rate = len(failed) / len(logs) * 100 if logs else 0.0
        
        return MetricsResponse(
            total_checks=len(logs),
            successful_checks=len(successful),
            failed_checks=len(failed),
            uptime_percentage=uptime,
            avg_response_time=avg_response_time,
            error_rate=error_rate,
            avg_response_time_p95=avg_response_time_p95,
            anomaly_count=len(anomalies)
        )
    
    async def get_uptime_metrics(
        self,
        user_id: int,
        api_endpoint_id: Optional[int] = None,
        days: int = 7
    ) -> dict:
        """Get uptime metrics for a time period."""
        from app.schemas.monitoring_schema import UptimeResponse
        
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        query = select(MonitoringLog).where(
            MonitoringLog.user_id == user_id,
            MonitoringLog.checked_at >= cutoff_time
        )
        
        if api_endpoint_id is not None:
            query = query.where(MonitoringLog.api_endpoint_id == api_endpoint_id)
        
        result = await self.db.execute(query)
        logs = list(result.scalars().all())
        
        if not logs:
            return UptimeResponse(
                uptime_percentage=100.0,
                total_downtime_minutes=0,
                total_checks=0,
                successful_checks=0,
                failed_checks=0,
                downtime_periods=[]
            )
        
        successful = [l for l in logs if l.status == CheckStatus.SUCCESS]
        failed = [l for l in logs if l.status in [CheckStatus.FAILURE, CheckStatus.ERROR, CheckStatus.TIMEOUT]]
        
        uptime = len(successful) / len(logs) * 100 if logs else 100.0
        
        # For simplicity, estimate downtime (this is a basic implementation)
        # In production, you'd calculate actual downtime periods
        total_downtime_minutes = len(failed) * (60 / max(len(logs) / days, 1))
        
        return UptimeResponse(
            uptime_percentage=uptime,
            total_downtime_minutes=total_downtime_minutes,
            total_checks=len(logs),
            successful_checks=len(successful),
            failed_checks=len(failed),
            downtime_periods=[]
        )
    
    async def get_response_time_series(
        self,
        api_endpoint_id: int,
        hours: int = 24
    ) -> dict:
        """Get response time time series data."""
        from app.schemas.monitoring_schema import TimeSeriesData
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.db.execute(
            select(MonitoringLog)
            .where(
                MonitoringLog.api_endpoint_id == api_endpoint_id,
                MonitoringLog.checked_at >= cutoff_time,
                MonitoringLog.response_time.isnot(None),
                MonitoringLog.status == CheckStatus.SUCCESS
            )
            .order_by(MonitoringLog.checked_at.asc())
        )
        logs = list(result.scalars().all())
        
        data_points = [
            {
                "timestamp": log.checked_at.isoformat(),
                "value": log.response_time
            }
            for log in logs
        ]
        
        return TimeSeriesData(
            data=data_points,
            start_time=cutoff_time,
            end_time=datetime.utcnow(),
            interval_minutes=5
        )
    
    async def get_status_code_distribution(
        self,
        user_id: int,
        api_endpoint_id: Optional[int] = None,
        hours: int = 24
    ) -> dict:
        """Get status code distribution."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(MonitoringLog).where(
            MonitoringLog.user_id == user_id,
            MonitoringLog.checked_at >= cutoff_time,
            MonitoringLog.status_code.isnot(None)
        )
        
        if api_endpoint_id is not None:
            query = query.where(MonitoringLog.api_endpoint_id == api_endpoint_id)
        
        result = await self.db.execute(query)
        logs = list(result.scalars().all())
        
        distribution = {}
        for log in logs:
            code = str(log.status_code)
            distribution[code] = distribution.get(code, 0) + 1
        
        return {
            "distribution": distribution,
            "total": len(logs)
        }
    
    async def get_error_rate(
        self,
        user_id: int,
        api_endpoint_id: Optional[int] = None,
        hours: int = 24
    ) -> dict:
        """Get error rate metrics."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(MonitoringLog).where(
            MonitoringLog.user_id == user_id,
            MonitoringLog.checked_at >= cutoff_time
        )
        
        if api_endpoint_id is not None:
            query = query.where(MonitoringLog.api_endpoint_id == api_endpoint_id)
        
        result = await self.db.execute(query)
        logs = list(result.scalars().all())
        
        if not logs:
            return {
                "error_rate": 0.0,
                "total_checks": 0,
                "failed_checks": 0
            }
        
        failed = [l for l in logs if l.status in [CheckStatus.FAILURE, CheckStatus.ERROR, CheckStatus.TIMEOUT]]
        error_rate = len(failed) / len(logs) * 100
        
        return {
            "error_rate": error_rate,
            "total_checks": len(logs),
            "failed_checks": len(failed)
        }
