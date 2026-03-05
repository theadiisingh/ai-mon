"""
Metrics API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timedelta

from app.core.dependencies import get_db
from app.core.security import get_current_user_optional
from app.schemas.monitoring_schema import MetricsResponse, UptimeResponse, TimeSeriesData
from app.services.monitoring_service import MonitoringService
from app.services.api_service import ApiService
from app.schemas.user_schema import UserResponse
from app.core.config import settings

router = APIRouter()


@router.get("/overview", response_model=MetricsResponse)
async def get_metrics_overview(
    api_endpoint_id: Optional[int] = None,
    hours: int = Query(default=24, ge=1, le=168),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Get metrics overview for user's endpoints."""
    # In development mode without auth, use a default user_id (1) for demo
    user_id = current_user.id if current_user else 1
    
    monitoring_service = MonitoringService(db)
    
    metrics_data = await monitoring_service.get_metrics(
        user_id=user_id,
        api_endpoint_id=api_endpoint_id,
        hours=hours
    )
    
    return metrics_data


@router.get("/uptime", response_model=UptimeResponse)
async def get_uptime_metrics(
    api_endpoint_id: Optional[int] = None,
    days: int = Query(default=7, ge=1, le=30),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Get uptime metrics for user's endpoints."""
    # In development mode without auth, use a default user_id (1) for demo
    user_id = current_user.id if current_user else 1
    
    monitoring_service = MonitoringService(db)
    
    uptime_data = await monitoring_service.get_uptime_metrics(
        user_id=user_id,
        api_endpoint_id=api_endpoint_id,
        days=days
    )
    
    return uptime_data


@router.get("/response-time")
async def get_response_time_series(
    api_endpoint_id: int,
    hours: int = Query(default=24, ge=1, le=168),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Get response time time series data for an endpoint."""
    # In development mode without auth, use a default user_id (1) for demo
    user_id = current_user.id if current_user else 1
    
    api_service = ApiService(db)
    endpoint = await api_service.get_endpoint(api_endpoint_id, user_id)
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found"
        )
    
    monitoring_service = MonitoringService(db)
    
    time_series = await monitoring_service.get_response_time_series(
        api_endpoint_id=api_endpoint_id,
        hours=hours
    )
    
    return time_series


@router.get("/status-codes")
async def get_status_code_distribution(
    api_endpoint_id: Optional[int] = None,
    hours: int = Query(default=24, ge=1, le=168),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Get status code distribution for user's endpoints."""
    # In development mode without auth, use a default user_id (1) for demo
    user_id = current_user.id if current_user else 1
    
    monitoring_service = MonitoringService(db)
    
    distribution = await monitoring_service.get_status_code_distribution(
        user_id=user_id,
        api_endpoint_id=api_endpoint_id,
        hours=hours
    )
    
    return distribution


@router.get("/error-rate")
async def get_error_rate(
    api_endpoint_id: Optional[int] = None,
    hours: int = Query(default=24, ge=1, le=168),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Get error rate metrics for user's endpoints."""
    # In development mode without auth, use a default user_id (1) for demo
    user_id = current_user.id if current_user else 1
    
    monitoring_service = MonitoringService(db)
    
    error_rate = await monitoring_service.get_error_rate(
        user_id=user_id,
        api_endpoint_id=api_endpoint_id,
        hours=hours
    )
    
    return error_rate


@router.get("/health-check/status")
async def get_monitoring_status(
    current_user: Optional[UserResponse] = Depends(get_current_user_optional)
):
    """Get the current monitoring system status."""
    from app.monitoring_engine.task_manager import get_task_manager
    
    task_manager = get_task_manager()
    status_info = task_manager.get_status()
    
    return status_info
