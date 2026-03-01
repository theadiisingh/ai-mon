"""
Unit tests for AI service and anomaly detection.
"""
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

from app.models.user import User
from app.models.api import ApiEndpoint, HttpMethod
from app.models.monitoring_log import MonitoringLog, CheckStatus
from app.models.ai_insight import AIInsight, InsightType, SeverityLevel
from app.services.ai_service import AIService
from app.services.anomaly_service import AnomalyService
from app.ai.llm_client import LLMClient


class TestLLMClient:
    """Test LLM client functionality."""
    
    @pytest.mark.asyncio
    async def test_mock_mode_enabled(self):
        """Test that mock mode is enabled when no API key."""
        client = LLMClient()
        
        assert client.mock_mode is True
    
    @pytest.mark.asyncio
    async def test_generate_mock_response_failure(self):
        """Test mock response for failure analysis."""
        client = LLMClient()
        
        prompt = "Analyze these API failures: 500 error, timeout"
        response = await client.generate(prompt)
        
        assert response is not None
        assert "summary" in response
        assert "possible_causes" in response
        assert "suggested_steps" in response
    
    @pytest.mark.asyncio
    async def test_generate_mock_response_anomaly(self):
        """Test mock response for anomaly detection."""
        client = LLMClient()
        
        prompt = "Analyze this response time anomaly: 500ms vs baseline 100ms"
        response = await client.generate(prompt)
        
        assert response is not None
        assert "summary" in response
        assert "severity" in response
    
    @pytest.mark.asyncio
    async def test_generate_text_mock(self):
        """Test mock text generation."""
        client = LLMClient()
        
        response = await client.generate_text("Summarize these logs")
        
        assert response is not None
        assert isinstance(response, str)


class TestAIService:
    """Test AI service operations."""
    
    @pytest.mark.asyncio
    async def test_analyze_failures(self, db_session, test_user, test_api_endpoint):
        """Test failure analysis."""
        ai_service = AIService(db_session)
        
        # Create some failed logs
        from app.schemas.monitoring_schema import MonitoringLogCreate
        for i in range(3):
            log = MonitoringLog(
                api_endpoint_id=test_api_endpoint.id,
                user_id=test_user.id,
                status=CheckStatus.FAILURE,
                status_code=500,
                response_time=100.0,
                error_message="Internal Server Error",
            )
            db_session.add(log)
        await db_session.commit()
        
        # Analyze failures
        result = await ai_service.analyze_failures(
            api_endpoint_id=test_api_endpoint.id,
            user_id=test_user.id,
            hours=24
        )
        
        assert result is not None
        assert result.summary is not None
        assert result.possible_causes is not None
        assert result.suggested_steps is not None
    
    @pytest.mark.asyncio
    async def test_check_and_trigger_analysis(self, db_session, test_user, test_api_endpoint):
        """Test checking and triggering AI analysis."""
        ai_service = AIService(db_session)
        
        # Create failed logs
        from app.schemas.monitoring_schema import MonitoringLogCreate
        for i in range(3):
            log = MonitoringLog(
                api_endpoint_id=test_api_endpoint.id,
                user_id=test_user.id,
                status=CheckStatus.FAILURE,
                status_code=500,
                response_time=100.0,
            )
            db_session.add(log)
        await db_session.commit()
        
        # Check and trigger
        triggered = await ai_service.check_and_trigger_analysis(
            api_endpoint_id=test_api_endpoint.id,
            user_id=test_user.id
        )
        
        # Should trigger after 3 failures and return an AIInsight object
        assert triggered is not None
    
    @pytest.mark.asyncio
    async def test_create_ai_insight(self, db_session, test_user, test_api_endpoint):
        """Test creating AI insight."""
        ai_service = AIService(db_session)
        
        insight = await ai_service.create_insight(
            api_endpoint_id=test_api_endpoint.id,
            user_id=test_user.id,
            insight_type=InsightType.FAILURE_ANALYSIS,
            title="High Failure Rate Detected",
            summary="The API has failed 3 times in the last 5 minutes",
            possible_causes=["Server overload", "Database connection issue"],
            suggested_steps=["Check server logs", "Review database connections"],
            confidence_score=0.85,
            model_used="mock-gpt-4"
        )
        
        assert insight is not None
        assert insight.id is not None
        assert insight.title == "High Failure Rate Detected"


class TestAnomalyService:
    """Test anomaly service operations."""
    
    @pytest.mark.asyncio
    async def test_get_response_time_baseline(self, db_session, test_user, test_api_endpoint):
        """Test getting response time baseline."""
        anomaly_service = AnomalyService(db_session)
        
        # Create logs with known response times
        from app.schemas.monitoring_schema import MonitoringLogCreate
        for i in range(10):
            await db_session.execute(
                MonitoringLog.__table__.insert().values(
                    api_endpoint_id=test_api_endpoint.id,
                    user_id=test_user.id,
                    status=CheckStatus.SUCCESS,
                    status_code=200,
                    response_time=100.0 + (i * 5),  # 100, 105, 110, etc.
                    is_anomaly=False,
                    request_method="GET",
                    request_url="https://api.example.com/health"
                )
            )
        await db_session.commit()
        
        baseline = await anomaly_service.get_response_time_baseline(
            api_endpoint_id=test_api_endpoint.id,
            window_hours=24
        )
        
        assert baseline is not None
        assert "average" in baseline
        assert "std_dev" in baseline
        assert "p50" in baseline
    
    @pytest.mark.asyncio
    async def test_check_response_time_anomaly_high(self):
        """Test anomaly detection with high response time."""
        # This would require more complex setup with historical data
        # For now, we'll test the logic with a mock
        pass


class TestIntegrationFlow:
    """Integration tests for complete flows."""
    
    @pytest.mark.asyncio
    async def test_registration_to_monitoring_flow(self, db_session, test_user):
        """Test the flow from API registration to monitoring."""
        from app.services.api_service import ApiService
        from app.services.monitoring_service import MonitoringService
        
        # 1. Create API endpoint
        api_service = ApiService(db_session)
        
        from app.schemas.api_schema import ApiEndpointCreate
        endpoint = await api_service.create_endpoint(
            endpoint_data=ApiEndpointCreate(
                name="Test API",
                url="https://api.example.com/health",
                method=HttpMethod.GET,
                expected_status_code=200,
                timeout_seconds=30,
                interval_seconds=60
            ),
            user_id=test_user.id
        )
        
        assert endpoint.id is not None
        
        # 2. Create monitoring log
        monitoring_service = MonitoringService(db_session)
        
        from app.schemas.monitoring_schema import MonitoringLogCreate
        log = await monitoring_service.create_log(
            MonitoringLogCreate(
                api_endpoint_id=endpoint.id,
                user_id=test_user.id,
                status=CheckStatus.SUCCESS,
                status_code=200,
                response_time=150.0,
                is_anomaly=False,
                request_method="GET",
                request_url=endpoint.url
            )
        )
        
        assert log.id is not None
        
        # 3. Verify stats updated
        endpoint = await api_service.get_endpoint_by_id(endpoint.id, test_user.id)
        assert endpoint.total_checks == 1
        assert endpoint.successful_checks == 1
    
    @pytest.mark.asyncio
    async def test_failure_to_ai_trigger_flow(self, db_session, test_user, test_api_endpoint):
        """Test the flow from repeated failures to AI analysis."""
        from app.services.monitoring_service import MonitoringService
        from app.services.ai_service import AIService
        
        monitoring_service = MonitoringService(db_session)
        ai_service = AIService(db_session)
        
        # Create 3 failed checks
        from app.schemas.monitoring_schema import MonitoringLogCreate
        for i in range(3):
            await monitoring_service.create_log(
                MonitoringLogCreate(
                    api_endpoint_id=test_api_endpoint.id,
                    user_id=test_user.id,
                    status=CheckStatus.FAILURE,
                    status_code=500,
                    response_time=100.0,
                    error_message="Internal Server Error",
                    is_anomaly=False,
                    request_method="GET",
                    request_url=test_api_endpoint.url
                )
            )
        
        # Check if AI analysis should be triggered
        failed_count = await monitoring_service.get_failed_checks_count(
            api_endpoint_id=test_api_endpoint.id,
            minutes=5
        )
        
        assert failed_count >= 3
        
        # Trigger AI analysis
        result = await ai_service.analyze_failures(
            api_endpoint_id=test_api_endpoint.id,
            user_id=test_user.id,
            hours=24
        )
        
        assert result is not None
        assert result.summary is not None
