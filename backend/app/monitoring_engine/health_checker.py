"""
Health checker for monitoring API endpoints with retry and error isolation.
"""
import json
import asyncio
import httpx
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.api import ApiEndpoint, HttpMethod
from app.models.monitoring_log import MonitoringLog, CheckStatus
from app.schemas.monitoring_schema import MonitoringLogCreate
from app.services.api_service import ApiService
from app.services.monitoring_service import MonitoringService
from app.services.anomaly_service import AnomalyService
from app.services.ai_service import AIService
from app.core.config import settings


# Global HTTP client for monitoring (singleton)
_global_http_client: Optional[httpx.AsyncClient] = None


async def get_global_http_client() -> httpx.AsyncClient:
    """Get or create the global HTTP client with connection pooling."""
    global _global_http_client
    if _global_http_client is None:
        _global_http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100
            )
        )
        logger.info("Global HTTP client created for monitoring")
    return _global_http_client


async def close_global_http_client():
    """Close the global HTTP client."""
    global _global_http_client
    if _global_http_client is not None:
        await _global_http_client.aclose()
        _global_http_client = None
        logger.info("Global HTTP client closed")


class HealthChecker:
    """
    Service for performing health checks on API endpoints.
    Includes retry logic with exponential backoff and error isolation.
    """
    
    def __init__(self, db: AsyncSession, http_client: Optional[httpx.AsyncClient] = None):
        self.db = db
        self.api_service = ApiService(db)
        self.monitoring_service = MonitoringService(db)
        self.anomaly_service = AnomalyService(db)
        self.ai_service = AIService(db)
        self.http_client = http_client
    
    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self.http_client is not None:
            return self.http_client
        return await get_global_http_client()
    
    async def close(self):
        """Close HTTP client (only if not using global)."""
        if self.http_client is not None:
            await self.http_client.aclose()
            self.http_client = None
    
    async def _retry_request(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        headers: dict,
        json_body: Optional[dict],
        timeout: int,
        endpoint_name: str
    ) -> Tuple[Optional[httpx.Response], Optional[str]]:
        """Execute HTTP request with retry logic and exponential backoff."""
        max_retries = settings.max_retries
        base_delay = 1.0
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_body,
                    timeout=timeout
                )
                return response, None
            except (httpx.TimeoutException, httpx.RequestError) as e:
                last_error = f"Attempt {attempt + 1}/{max_retries}: {str(e)}"
                logger.warning(f"Retry for {endpoint_name}: {last_error}")
            
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
        
        return None, last_error
    
    async def check_endpoint(self, endpoint: ApiEndpoint) -> Tuple[MonitoringLog, bool]:
        """Perform a health check on an API endpoint with retry and error isolation."""
        start_time = datetime.utcnow()
        
        try:
            headers = json.loads(endpoint.headers) if endpoint.headers else {}
            body = json.loads(endpoint.body) if endpoint.body else None
            json_body = body if endpoint.method in [HttpMethod.POST, HttpMethod.PUT, HttpMethod.PATCH] else None
            
            client = await self.get_client()
            response, error_msg = await self._retry_request(
                client=client,
                method=endpoint.method.value,
                url=endpoint.url,
                headers=headers,
                json_body=json_body,
                timeout=endpoint.timeout_seconds,
                endpoint_name=endpoint.name
            )
            
            if response is None:
                end_time = datetime.utcnow()
                response_time = (end_time - start_time).total_seconds() * 1000
                
                log_data = MonitoringLogCreate(
                    api_endpoint_id=endpoint.id,
                    user_id=endpoint.user_id,
                    status=CheckStatus.TIMEOUT,
                    status_code=None,
                    response_time=response_time,
                    error_message=error_msg or "Max retries exceeded",
                    is_anomaly=False,
                    request_method=endpoint.method.value,
                    request_url=endpoint.url
                )
                
                log = await self.monitoring_service.create_log(log_data)
                
                await self.api_service.update_endpoint_stats(
                    endpoint_id=endpoint.id,
                    status_code=None,
                    response_time=response_time,
                    is_success=False
                )
                
                failed_count = await self.monitoring_service.get_failed_checks_count(
                    api_endpoint_id=endpoint.id,
                    minutes=5
                )
                
                return log, failed_count >= 3
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            status_code = response.status_code
            is_success = status_code == endpoint.expected_status_code
            status = CheckStatus.SUCCESS if is_success else CheckStatus.FAILURE
            
            is_anomaly = False
            anomaly_score = None
            
            if is_success:
                is_anomaly, anomaly_score = await self.anomaly_service.check_response_time_anomaly(
                    api_endpoint_id=endpoint.id,
                    current_response_time=response_time
                )
            
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
            
            await self.api_service.update_endpoint_stats(
                endpoint_id=endpoint.id,
                status_code=status_code,
                response_time=response_time,
                is_success=is_success
            )
            
            should_trigger_ai = False
            if not is_success:
                failed_count = await self.monitoring_service.get_failed_checks_count(
                    api_endpoint_id=endpoint.id,
                    minutes=5
                )
                if failed_count >= 3:
                    should_trigger_ai = True
            
            logger.info(f"Health check: {endpoint.name} - {status.value} - {response_time:.2f}ms")
            
            return log, should_trigger_ai
        
        except Exception as e:
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            logger.error(f"Error checking {endpoint.name}: {e}")
            
            log_data = MonitoringLogCreate(
                api_endpoint_id=endpoint.id,
                user_id=endpoint.user_id,
                status=CheckStatus.ERROR,
                status_code=None,
                response_time=response_time,
                error_message=str(e)[:500],
                is_anomaly=False,
                request_method=endpoint.method.value,
                request_url=endpoint.url
            )
            
            log = await self.monitoring_service.create_log(log_data)
            
            await self.api_service.update_endpoint_stats(
                endpoint_id=endpoint.id,
                status_code=None,
                response_time=response_time,
                is_success=False
            )
            
            return log, False
    
    async def check_all_active_endpoints(self) -> Dict[str, Any]:
        """Check all active API endpoints with error isolation."""
        from app.services.user_service import UserService
        from app.services.email_service import EmailService
        
        endpoints = await self.api_service.get_active_endpoints()
        
        results = {
            "total": len(endpoints),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        previous_status = {}
        
        for endpoint in endpoints:
            try:
                log, should_trigger_ai = await self.check_endpoint(endpoint)
                
                if log.status == CheckStatus.SUCCESS:
                    results["successful"] += 1
                    prev_status = previous_status.get(endpoint.id)
                    if prev_status and prev_status != CheckStatus.SUCCESS:
                        try:
                            user_service = UserService(self.db)
                            user = await user_service.get_user_by_id(endpoint.user_id)
                            if user:
                                email_service = EmailService()
                                await email_service.send_api_recovered_notification(
                                    to_email=user.email,
                                    api_name=endpoint.name,
                                    api_url=endpoint.url,
                                    downtime_minutes=5
                                )
                        except Exception as e:
                            logger.warning(f"Recovery email failed: {e}")
                else:
                    results["failed"] += 1
                    try:
                        failed_count = await self.monitoring_service.get_failed_checks_count(
                            api_endpoint_id=endpoint.id,
                            minutes=10
                        )
                        if failed_count >= 3:
                            user_service = UserService(self.db)
                            user = await user_service.get_user_by_id(endpoint.user_id)
                            if user:
                                email_service = EmailService()
                                await email_service.send_api_down_notification(
                                    to_email=user.email,
                                    api_name=endpoint.name,
                                    api_url=endpoint.url,
                                    error_message=log.error_message or "Multiple failures",
                                    failure_count=failed_count
                                )
                    except Exception as e:
                        logger.warning(f"Down notification failed: {e}")
                
                previous_status[endpoint.id] = log.status
                
                if should_trigger_ai:
                    try:
                        await self.ai_service.check_and_trigger_analysis(
                            api_endpoint_id=endpoint.id,
                            user_id=endpoint.user_id
                        )
                    except Exception as e:
                        logger.warning(f"AI analysis trigger failed: {e}")
            
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "endpoint_id": endpoint.id,
                    "endpoint_name": endpoint.name,
                    "error": str(e)
                })
                logger.error(f"Failed endpoint check {endpoint.id}: {e}")
        
        return results


async def run_health_check():
    """Run health check for all active endpoints (used by scheduler)."""
    from app.core.database import AsyncSessionLocal
    
    logger.info("Starting health check cycle...")
    
    async with AsyncSessionLocal() as db:
        http_client = await get_global_http_client()
        checker = HealthChecker(db, http_client=http_client)
        try:
            results = await checker.check_all_active_endpoints()
            await db.commit()
            logger.info(
                f"Health check completed: total={results['total']}, "
                f"successful={results['successful']}, failed={results['failed']}"
            )
            return results
        except Exception as e:
            await db.rollback()
            logger.error(f"Health check cycle failed: {e}")
            raise


async def run_health_check_single_endpoint(endpoint_id: int):
    """Run health check for a single endpoint (for testing/manual trigger)."""
    from app.core.database import AsyncSessionLocal
    
    logger.info(f"Running single health check for endpoint {endpoint_id}...")
    
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        from app.models.api import ApiEndpoint
        
        http_client = await get_global_http_client()
        checker = HealthChecker(db, http_client=http_client)
        
        result = await db.execute(
            select(ApiEndpoint).where(ApiEndpoint.id == endpoint_id)
        )
        endpoint = result.scalar_one_or_none()
        
        if not endpoint:
            logger.warning(f"Endpoint {endpoint_id} not found")
            return {"error": "Endpoint not found"}
        
        try:
            log, should_trigger_ai = await checker.check_endpoint(endpoint)
            await db.commit()
            logger.info(
                f"Single health check for {endpoint.name}: "
                f"status={log.status.value}, status_code={log.status_code}, "
                f"response_time={log.response_time:.2f}ms"
            )
            return {
                "endpoint_id": endpoint.id,
                "endpoint_name": endpoint.name,
                "status": log.status.value,
                "status_code": log.status_code,
                "response_time_ms": log.response_time,
                "error_message": log.error_message
            }
        except Exception as e:
            logger.error(f"Single health check failed: {e}")
            await db.rollback()
            return {"error": str(e)}
