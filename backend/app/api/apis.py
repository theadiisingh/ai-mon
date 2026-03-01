"""
API endpoints management routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.dependencies import get_db, get_current_active_user
from app.schemas.api_schema import (
    ApiEndpointCreate,
    ApiEndpointResponse,
    ApiEndpointUpdate,
    ApiEndpointListResponse
)
from app.services.api_service import ApiService
from app.schemas.user_schema import UserResponse

router = APIRouter()


@router.post("/", response_model=ApiEndpointResponse, status_code=status.HTTP_201_CREATED)
async def create_endpoint(
    endpoint_data: ApiEndpointCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new API endpoint for monitoring."""
    api_service = ApiService(db)
    
    endpoint = await api_service.create_endpoint(
        endpoint_data=endpoint_data,
        user_id=current_user.id
    )
    
    return endpoint


@router.get("/", response_model=ApiEndpointListResponse)
async def list_endpoints(
    page: int = 1,
    page_size: int = 20,
    is_active: bool = None,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all API endpoints for the current user."""
    api_service = ApiService(db)
    
    endpoints, total = await api_service.list_endpoints(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        is_active=is_active
    )
    
    return ApiEndpointListResponse(
        items=endpoints,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{endpoint_id}", response_model=ApiEndpointResponse)
async def get_endpoint(
    endpoint_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific API endpoint."""
    api_service = ApiService(db)
    
    endpoint = await api_service.get_endpoint(
        endpoint_id=endpoint_id,
        user_id=current_user.id
    )
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found"
        )
    
    return endpoint


@router.put("/{endpoint_id}", response_model=ApiEndpointResponse)
async def update_endpoint(
    endpoint_id: int,
    endpoint_update: ApiEndpointUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an API endpoint."""
    api_service = ApiService(db)
    
    endpoint = await api_service.update_endpoint(
        endpoint_id=endpoint_id,
        user_id=current_user.id,
        endpoint_data=endpoint_update
    )
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found"
        )
    
    return endpoint


@router.delete("/{endpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_endpoint(
    endpoint_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an API endpoint."""
    api_service = ApiService(db)
    
    success = await api_service.delete_endpoint(
        endpoint_id=endpoint_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found"
        )
    
    return None


@router.post("/{endpoint_id}/toggle", response_model=ApiEndpointResponse)
async def toggle_endpoint(
    endpoint_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle an API endpoint's active status."""
    api_service = ApiService(db)
    
    endpoint = await api_service.toggle_endpoint_status(
        endpoint_id=endpoint_id,
        user_id=current_user.id
    )
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found"
        )
    
    return endpoint


@router.post("/{endpoint_id}/pause", response_model=ApiEndpointResponse)
async def pause_endpoint(
    endpoint_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Pause monitoring for an endpoint."""
    api_service = ApiService(db)
    
    endpoint = await api_service.pause_endpoint(
        endpoint_id=endpoint_id,
        user_id=current_user.id
    )
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found"
        )
    
    return endpoint


@router.post("/{endpoint_id}/resume", response_model=ApiEndpointResponse)
async def resume_endpoint(
    endpoint_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Resume monitoring for an endpoint."""
    api_service = ApiService(db)
    
    endpoint = await api_service.resume_endpoint(
        endpoint_id=endpoint_id,
        user_id=current_user.id
    )
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found"
        )
    
    return endpoint


@router.post("/{endpoint_id}/check", status_code=status.HTTP_200_OK)
async def trigger_manual_check(
    endpoint_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger a manual health check for an endpoint."""
    from app.monitoring_engine.health_checker import HealthChecker
    
    api_service = ApiService(db)
    
    endpoint = await api_service.get_endpoint(
        endpoint_id=endpoint_id,
        user_id=current_user.id
    )
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found"
        )
    
    # Perform health check
    checker = HealthChecker(db)
    try:
        log, _ = await checker.check_endpoint(endpoint)
        return {"message": "Health check completed", "log_id": log.id}
    finally:
        await checker.close()
