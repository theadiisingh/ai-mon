"""
API Endpoint service for managing monitored APIs.
"""
from typing import Optional, List
import json
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api import ApiEndpoint, HttpMethod
from app.models.monitoring_log import MonitoringLog, CheckStatus
from app.schemas.api_schema import ApiEndpointCreate, ApiEndpointUpdate, ApiEndpointStats


class ApiService:
    """Service for API endpoint operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_endpoint_by_id(
        self, 
        endpoint_id: int, 
        user_id: int
    ) -> Optional[ApiEndpoint]:
        """Get an API endpoint by ID for a specific user."""
        result = await self.db.execute(
            select(ApiEndpoint).where(
                ApiEndpoint.id == endpoint_id,
                ApiEndpoint.user_id == user_id
            )
        )
        endpoint = result.scalar_one_or_none()
        
        # Calculate avg_response_time if endpoint exists
        if endpoint:
            endpoint.avg_response_time = await self._calculate_avg_response_time(endpoint.id)
        
        return endpoint
    
    async def create_endpoint(
        self, 
        endpoint_data: ApiEndpointCreate, 
        user_id: int
    ) -> ApiEndpoint:
        """Create a new API endpoint."""
        # Convert headers and body to JSON strings
        headers_json = json.dumps(endpoint_data.headers) if endpoint_data.headers else None
        body_json = json.dumps(endpoint_data.body) if endpoint_data.body else None
        
        db_endpoint = ApiEndpoint(
            user_id=user_id,
            name=endpoint_data.name,
            url=endpoint_data.url,
            method=endpoint_data.method,
            headers=headers_json,
            body=body_json,
            expected_status_code=endpoint_data.expected_status_code,
            timeout_seconds=endpoint_data.timeout_seconds,
            interval_seconds=endpoint_data.interval_seconds,
        )
        
        self.db.add(db_endpoint)
        await self.db.flush()
        await self.db.refresh(db_endpoint)
        
        return db_endpoint
    
    async def update_endpoint(
        self, 
        endpoint_id: int, 
        user_id: int, 
        endpoint_data: ApiEndpointUpdate
    ) -> Optional[ApiEndpoint]:
        """Update an API endpoint."""
        endpoint = await self.get_endpoint_by_id(endpoint_id, user_id)
        
        if not endpoint:
            return None
        
        # Update fields if provided
        update_data = endpoint_data.model_dump(exclude_unset=True)
        
        if "headers" in update_data:
            update_data["headers"] = json.dumps(update_data["headers"]) if update_data["headers"] else None
        
        if "body" in update_data:
            update_data["body"] = json.dumps(update_data["body"]) if update_data["body"] else None
        
        for field, value in update_data.items():
            setattr(endpoint, field, value)
        
        await self.db.flush()
        await self.db.refresh(endpoint)
        
        return endpoint
    
    async def delete_endpoint(
        self, 
        endpoint_id: int, 
        user_id: int
    ) -> bool:
        """Delete an API endpoint."""
        endpoint = await self.get_endpoint_by_id(endpoint_id, user_id)
        
        if not endpoint:
            return False
        
        await self.db.delete(endpoint)
        await self.db.flush()
        
        return True
    
    async def list_endpoints(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        is_active: Optional[bool] = None
    ) -> tuple[List[ApiEndpoint], int]:
        """List endpoints with pagination."""
        query = select(ApiEndpoint).where(ApiEndpoint.user_id == user_id)
        
        if is_active is not None:
            query = query.where(ApiEndpoint.is_active == is_active)
        
        # Get total count
        count_query = select(func.count(ApiEndpoint.id)).where(
            ApiEndpoint.user_id == user_id
        )
        if is_active is not None:
            count_query = count_query.where(ApiEndpoint.is_active == is_active)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated results
        skip = (page - 1) * page_size
        query = query.offset(skip).limit(page_size).order_by(ApiEndpoint.created_at.desc())
        
        result = await self.db.execute(query)
        endpoints = list(result.scalars().all())
        
        # Calculate avg_response_time for each endpoint (set as attribute for response)
        for endpoint in endpoints:
            endpoint.avg_response_time = await self._calculate_avg_response_time(endpoint.id)
        
        return endpoints, total
    
    async def _calculate_avg_response_time(self, endpoint_id: int) -> Optional[float]:
        """Calculate average response time for an endpoint."""
        result = await self.db.execute(
            select(func.avg(MonitoringLog.response_time))
            .where(
                MonitoringLog.api_endpoint_id == endpoint_id,
                MonitoringLog.status == CheckStatus.SUCCESS,
                MonitoringLog.response_time.isnot(None)
            )
        )
        avg = result.scalar()
        return float(avg) if avg else None
    
    async def count_endpoints(
        self, 
        user_id: int,
        is_active: Optional[bool] = None
    ) -> int:
        """Count API endpoints for a user."""
        query = select(func.count(ApiEndpoint.id)).where(ApiEndpoint.user_id == user_id)
        
        if is_active is not None:
            query = query.where(ApiEndpoint.is_active == is_active)
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def get_active_endpoints(self) -> List[ApiEndpoint]:
        """Get all active API endpoints for monitoring."""
        result = await self.db.execute(
            select(ApiEndpoint).where(
                ApiEndpoint.is_active == True,
                ApiEndpoint.is_paused == False
            )
        )
        return list(result.scalars().all())
    
    async def update_endpoint_stats(
        self,
        endpoint_id: int,
        status_code: Optional[int],
        response_time: Optional[float],
        is_success: bool
    ) -> Optional[ApiEndpoint]:
        """Update endpoint statistics after a check."""
        endpoint = await self.db.get(ApiEndpoint, endpoint_id)
        
        if not endpoint:
            return None
        
        endpoint.last_status_code = status_code
        endpoint.last_response_time = response_time
        endpoint.last_checked_at = func.now()
        endpoint.total_checks += 1
        
        if is_success:
            endpoint.successful_checks += 1
        else:
            endpoint.failed_checks += 1
        
        # Calculate uptime percentage
        if endpoint.total_checks > 0:
            endpoint.uptime_percentage = (endpoint.successful_checks / endpoint.total_checks) * 100
        
        await self.db.flush()
        await self.db.refresh(endpoint)
        
        return endpoint
    
    async def pause_endpoint(
        self,
        endpoint_id: int,
        user_id: int
    ) -> Optional[ApiEndpoint]:
        """Pause monitoring for an endpoint."""
        endpoint = await self.get_endpoint_by_id(endpoint_id, user_id)
        
        if not endpoint:
            return None
        
        endpoint.is_paused = True
        await self.db.flush()
        await self.db.refresh(endpoint)
        
        return endpoint
    
    async def resume_endpoint(
        self,
        endpoint_id: int,
        user_id: int
    ) -> Optional[ApiEndpoint]:
        """Resume monitoring for an endpoint."""
        endpoint = await self.get_endpoint_by_id(endpoint_id, user_id)
        
        if not endpoint:
            return None
        
        endpoint.is_paused = False
        await self.db.flush()
        await self.db.refresh(endpoint)
        
        return endpoint
    
    async def toggle_endpoint_status(
        self,
        endpoint_id: int,
        user_id: int
    ) -> Optional[ApiEndpoint]:
        """Toggle an endpoint's active status."""
        endpoint = await self.get_endpoint_by_id(endpoint_id, user_id)
        
        if not endpoint:
            return None
        
        endpoint.is_active = not endpoint.is_active
        await self.db.flush()
        await self.db.refresh(endpoint)
        
        return endpoint
    
    async def get_endpoint(
        self,
        endpoint_id: int,
        user_id: int
    ) -> Optional[ApiEndpoint]:
        """Get an endpoint by ID (alias for get_endpoint_by_id)."""
        return await self.get_endpoint_by_id(endpoint_id, user_id)
