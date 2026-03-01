"""
Health checker for monitoring API endpoints.
"""
import json
import asyncio
import httpx
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api import ApiEndpoint, HttpMethod
from app.models.monitoring_log import MonitoringLog, CheckStatus
from app.schemas.monitoring_schema import MonitoringLogCreate
from app.services.api_service import ApiService
from app.services.monitoring_service import MonitoringService
from app.services.anomaly_service import AnomalyService
from app.services.ai_service import AIService
from app.core.config import settings
from loguru import logger


class HealthChecker:
    """Service for performing health checks on API endpoints."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_service = ApiService(db)
        self.monitoring_service = MonitoringService(db)
        self.anomaly_service = AnomalyService(db)
        self.ai_service = AIService(db)
        self.http_client: Optional[httpx.AsyncClient] = None
    
    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                follow_redirects=True,
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
            )
        return self.http_client
    
    async def close(self):
        """Close HTTP client."""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None
    
    async def check_endpoint(self, endpoint: ApiEndpoint) -> Tuple[MonitoringLog, bool]:
        """
        Perform a health check on an API endpoint.
        
        Returns:
            Tuple of (MonitoringLog, should_trigger_ai_analysis)
        """
        start_time = datetime.utcnow()
        
        try:
            # Prepare request
            headers = json.loads(endpoint.headers) if endpoint.headers else {}
            body = json.loads(endpoint.body) if endpoint.body else None
            
            # Make HTTP request
            client = await self.get_client()
            
            response = await client.request(
                method=endpoint.method.value,
                url=endpoint.url,
                headers=headers,
                json=body if endpoint.method in [HttpMethod.POST, HttpMethod.PUT, HttpMethod.PATCH] else None,
                timeout=endpoint.timeout_seconds
            )
            
            # Calculate response time
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000  # Convert to ms
            
            # Determine status
            status_code = response.status_code
            is_success = status_code == endpoint.expected_status_code
            
            status = CheckStatus.SUCCESS if is_success else CheckStatus.FAILURE
            
            # Truncate response body for storage
            response_body = None
            if not is_success:
                try:
                    response_body = response.text[:5000]  # Store first 5000 chars
                except Exception:
                    pass
            
            # Check for anomaly
            is_anomaly = False
            anomaly_score = None
            
            if is_success:
                is_anomaly, anomaly_score = await self.anomaly_service.check_response_time_anomaly(
                    api_endpoint_id=endpoint.id,
                    current_response_time=response_time
                )
            
            # Create monitoring log
            log_data = MonitoringLogCreate(
                api_endpoint_id=endpoint.id,
                user_id=endpoint.user_id,
                status=status,
                status_code=status_code,
                response_time=response_time,
                error_message=None if is_success else f"Expected {endpoint.expected_status_code}, got {status_code}",
                is_anomaly=is_anomaly,
                anomaly_score=anomaly_score,
                request_method=endpoint.method.value,
                request_url=endpoint.url
            )
            
            log = await self.monitoring_service.create_log(log_data)
            
            # Update endpoint stats
            await self.api_service.update_endpoint_stats(
                endpoint_id=endpoint.id,
                status_code=status_code,
                response_time=response_time,
                is_success=is_success
            )
            
            # Check if we should trigger AI analysis
            should_trigger_ai = False
            if not is_success:
                failed_count = await self.monitoring_service.get_failed_checks_count(
                    api_endpoint_id=endpoint.id,
                    minutes=5
                )
                if failed_count >= 3:
                    should_trigger_ai = True
            
            logger.info(
                f"Health check completed for {endpoint.name}: "
                f"status={status.value}, status_code={status_code}, "
                f"response_time={response_time:.2f}ms"
            )
            
            return log, should_trigger_ai
        
        except httpx.TimeoutException as e:
            # Handle timeout
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            log_data = MonitoringLogCreate(
                api_endpoint_id=endpoint.id,
                user_id=endpoint.user_id,
                status=CheckStatus.TIMEOUT,
                status_code=None,
                response_time=response_time,
                error_message=f"Request timeout after {endpoint.timeout_seconds}s",
                is_anomaly=False,
                request_method=endpoint.method.value,
                request_url=endpoint.url
            )
            
            log = await self.monitoring_service.create_log(log_data)
            
            # Update endpoint stats
            await self.api_service.update_endpoint_stats(
                endpoint_id=endpoint.id,
                status_code=None,
                response_time=response_time,
                is_success=False
            )
            
            logger.warning(f"Timeout for endpoint {endpoint.name}: {e}")
            
            # Check if we should trigger AI analysis
            failed_count = await self.monitoring_service.get_failed_checks_count(
                api_endpoint_id=endpoint.id,
                minutes=5
            )
            should_trigger_ai = failed_count >= 3
            
            return log, should_trigger_ai
        
        except httpx.RequestError as e:
            # Handle other request errors
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            log_data = MonitoringLogCreate(
                api_endpoint_id=endpoint.id,
                user_id=endpoint.user_id,
                status=CheckStatus.ERROR,
                status_code=None,
                response_time=response_time,
                error_message=str(e),
                is_anomaly=False,
                request_method=endpoint.method.value,
                request_url=endpoint.url
            )
            
            log = await self.monitoring_service.create_log(log_data)
            
            # Update endpoint stats
            await self.api_service.update_endpoint_stats(
                endpoint_id=endpoint.id,
                status_code=None,
                response_time=response_time,
                is_success=False
            )
            
            logger.error(f"Error checking endpoint {endpoint.name}: {e}")
            
            # Check if we should trigger AI analysis
            failed_count = await self.monitoring_service.get_failed_checks_count(
                api_endpoint_id=endpoint.id,
                minutes=5
            )
            should_trigger_ai = failed_count >= 3
            
            return log, should_trigger_ai
    
    async def check_all_active_endpoints(self) -> Dict[str, Any]:
        """Check all active API endpoints."""
        from app.services.user_service import UserService
        from app.services.email_service import EmailService
        
        endpoints = await self.api_service.get_active_endpoints()
        
        results = {
            "total": len(endpoints),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Track previous status for email alerts
        previous_status = {}
        
        for endpoint in endpoints:
            try:
                log, should_trigger_ai = await self.check_endpoint(endpoint)
                
                if log.status == CheckStatus.SUCCESS:
                    results["successful"] += 1
                    
                    # Check if endpoint recovered (was failing before)
                    prev_status = previous_status.get(endpoint.id)
                    if prev_status and prev_status != CheckStatus.SUCCESS:
                        # Endpoint recovered - send recovery email
                        user_service = UserService(self.db)
                        user = await user_service.get_user_by_id(endpoint.user_id)
                        if user:
                            email_service = EmailService()
                            await email_service.send_api_recovered_notification(
                                to_email=user.email,
                                api_name=endpoint.name,
                                api_url=endpoint.url,
                                downtime_minutes=5  # Approximate
                            )
                else:
                    results["failed"] += 1
                    
                    # Check for consecutive failures for email alert
                    failed_count = await self.monitoring_service.get_failed_checks_count(
                        api_endpoint_id=endpoint.id,
                        minutes=10
                    )
                    
                    # Send email alert on consecutive failures (3+ failures)
                    if failed_count >= 3:
                        user_service = UserService(self.db)
                        user = await user_service.get_user_by_id(endpoint.user_id)
                        if user:
                            email_service = EmailService()
                            await email_service.send_api_down_notification(
                                to_email=user.email,
                                api_name=endpoint.name,
                                api_url=endpoint.url,
                                error_message=log.error_message or "Multiple failures detected",
                                failure_count=failed_count
                            )
                
                # Store previous status
                previous_status[endpoint.id] = log.status
                
                # Trigger AI analysis if needed
                if should_trigger_ai:
                    await self.ai_service.check_and_trigger_analysis(
                        api_endpoint_id=endpoint.id,
                        user_id=endpoint.user_id
                    )
            
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "endpoint_id": endpoint.id,
                    "error": str(e)
                })
                logger.error(f"Failed to check endpoint {endpoint.id}: {e}")
        
        return results


async def run_health_check(db_session_factory):
    """Run health check for all active endpoints."""
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        checker = HealthChecker(db)
        try:
            results = await checker.check_all_active_endpoints()
            logger.info(f"Health check completed: {results}")
            return results
        finally:
            await checker.close()
