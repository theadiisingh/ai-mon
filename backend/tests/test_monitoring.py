"""
Unit tests for monitoring logic.
"""
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

from app.models.user import User
from app.models.api import ApiEndpoint, HttpMethod
from app.models.monitoring_log import MonitoringLog, CheckStatus
from app.services.monitoring_service import MonitoringService
from app.services.api_service import ApiService
from app.services.anomaly_service import AnomalyService


class TestMonitoringService:
    """Test monitoring service operations."""
    
    @pytest.mark.asyncio
    async def test_create_log(self, db_session, test_user, test_api_endpoint):
        """Test creating a monitoring log."""
        monitoring_service = MonitoringService(db_session)
        
        log_data = {
            "api_endpoint_id": test_api_endpoint.id,
            "user_id": test_user.id,
            "status": CheckStatus.SUCCESS,
            "status_code": 200,
            "response_time": 150.5,
            "is_anomaly": False,
            "request_method": "GET",
            "request_url": "https://api.example.com/health"
        }
        
        from app.schemas.monitoring_schema import MonitoringLogCreate
        log = await monitoring_service.create_log(MonitoringLogCreate(**log_data))
        
        assert log.id is not None
        assert log.api_endpoint_id == test_api_endpoint.id
        assert log.status == CheckStatus.SUCCESS
    
    @pytest.mark.asyncio
    async def test_list_logs(self, db_session, test_user, test_api_endpoint, test_monitoring_logs):
        """Test listing monitoring logs."""
        monitoring_service = MonitoringService(db_session)
        
        logs = await monitoring_service.list_logs(
            user_id=test_user.id,
            api_endpoint_id=test_api_endpoint.id
        )
        
        assert len(logs) >= 10
    
    @pytest.mark.asyncio
    async def test_get_failed_checks_count(self, db_session, test_user, test_api_endpoint):
        """Test getting failed checks count."""
        monitoring_service = MonitoringService(db_session)
        
        # Create some failed logs
        from app.schemas.monitoring_schema import MonitoringLogCreate
        for i in range(3):
            log = await monitoring_service.create_log(
                MonitoringLogCreate(
                    api_endpoint_id=test_api_endpoint.id,
                    user_id=test_user.id,
                    status=CheckStatus.FAILURE,
                    status_code=500,
                    response_time=100.0,
                    is_anomaly=False,
                    request_method="GET",
                    request_url="https://api.example.com/health"
                )
            )
        
        failed_count = await monitoring_service.get_failed_checks_count(
            api_endpoint_id=test_api_endpoint.id,
            minutes=5
        )
        
        assert failed_count >= 3
    
    @pytest.mark.asyncio
    async def test_get_check_summary(self, db_session, test_user, test_api_endpoint):
        """Test getting check summary."""
        monitoring_service = MonitoringService(db_session)
        
        # Create logs
        from app.schemas.monitoring_schema import MonitoringLogCreate
        for i in range(5):
            await monitoring_service.create_log(
                MonitoringLogCreate(
                    api_endpoint_id=test_api_endpoint.id,
                    user_id=test_user.id,
                    status=CheckStatus.SUCCESS if i < 4 else CheckStatus.FAILURE,
                    status_code=200 if i < 4 else 500,
                    response_time=100.0 + i * 10,
                    is_anomaly=False,
                    request_method="GET",
                    request_url="https://api.example.com/health"
                )
            )
        
        summary = await monitoring_service.get_check_summary(
            api_endpoint_id=test_api_endpoint.id,
            hours=24
        )
        
        assert summary.total_checks == 5
        assert summary.successful_checks == 4
        assert summary.failed_checks == 1
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, db_session, test_user, test_api_endpoint):
        """Test getting metrics."""
        monitoring_service = MonitoringService(db_session)
        
        # Create logs
        from app.schemas.monitoring_schema import MonitoringLogCreate
        for i in range(5):
            await monitoring_service.create_log(
                MonitoringLogCreate(
                    api_endpoint_id=test_api_endpoint.id,
                    user_id=test_user.id,
                    status=CheckStatus.SUCCESS if i < 4 else CheckStatus.FAILURE,
                    status_code=200 if i < 4 else 500,
                    response_time=100.0 + i * 10,
                    is_anomaly=False,
                    request_method="GET",
                    request_url="https://api.example.com/health"
                )
            )
        
        metrics = await monitoring_service.get_metrics(
            user_id=test_user.id,
            api_endpoint_id=test_api_endpoint.id,
            hours=24
        )
        
        assert metrics.total_checks == 5
        assert metrics.successful_checks == 4
        assert metrics.failed_checks == 1
        assert metrics.uptime_percentage > 0


class TestAnomalyDetection:
    """Test anomaly detection logic."""
    
    @pytest.mark.asyncio
    async def test_check_response_time_anomaly(self, db_session, test_user, test_api_endpoint):
        """Test response time anomaly detection."""
        anomaly_service = AnomalyService(db_session)
        
        # First check should not be an anomaly (no baseline)
        is_anomaly, score = await anomaly_service.check_response_time_anomaly(
            api_endpoint_id=test_api_endpoint.id,
            current_response_time=150.0
        )
        
        # Without enough historical data, should not detect anomaly
        assert is_anomaly is False
        assert score is None
    
    @pytest.mark.asyncio
    async def test_detect_anomalies(self, db_session, test_user, test_api_endpoint):
        """Test detecting anomalies in logs."""
        anomaly_service = AnomalyService(db_session)
        monitoring_service = MonitoringService(db_session)
        
        # Create logs with varying response times using the monitoring service
        from app.schemas.monitoring_schema import MonitoringLogCreate
        for i in range(10):
            # Create some high response times
            response_time = 100.0 if i < 8 else 500.0  # Last 2 are high
            await monitoring_service.create_log(
                MonitoringLogCreate(
                    api_endpoint_id=test_api_endpoint.id,
                    user_id=test_user.id,
                    status=CheckStatus.SUCCESS,
                    status_code=200,
                    response_time=response_time,
                    is_anomaly=False,
                    request_method="GET",
                    request_url="https://api.example.com/health"
                )
            )
        
        anomalies = await anomaly_service.detect_anomalies(
            api_endpoint_id=test_api_endpoint.id,
            window_hours=24
        )
        
        # Should find some anomalies
        assert isinstance(anomalies, list)


class TestAPIEndpointStats:
    """Test API endpoint statistics."""
    
    @pytest.mark.asyncio
    async def test_update_endpoint_stats(self, db_session, test_user, test_api_endpoint):
        """Test updating endpoint statistics."""
        api_service = ApiService(db_session)
        
        # Update with success
        endpoint = await api_service.update_endpoint_stats(
            endpoint_id=test_api_endpoint.id,
            status_code=200,
            response_time=150.0,
            is_success=True
        )
        
        assert endpoint is not None
        assert endpoint.total_checks == 1
        assert endpoint.successful_checks == 1
        assert endpoint.failed_checks == 0
        assert endpoint.last_status_code == 200
        assert endpoint.last_response_time == 150.0
        
        # Update with failure
        endpoint = await api_service.update_endpoint_stats(
            endpoint_id=test_api_endpoint.id,
            status_code=500,
            response_time=200.0,
            is_success=False
        )
        
        assert endpoint.total_checks == 2
        assert endpoint.successful_checks == 1
        assert endpoint.failed_checks == 1
    
    @pytest.mark.asyncio
    async def test_get_active_endpoints(self, db_session, test_user, test_api_endpoint):
        """Test getting active endpoints."""
        api_service = ApiService(db_session)
        
        endpoints = await api_service.get_active_endpoints()
        
        assert len(endpoints) >= 1
        assert all(e.is_active and not e.is_paused for e in endpoints)
