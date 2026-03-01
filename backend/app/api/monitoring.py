"""
Monitoring API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.dependencies import get_db, get_current_active_user
from app.schemas.monitoring_schema import (
    MonitoringLogResponse,
    MonitoringLogListResponse,
    AnomalyResponse
)
from app.schemas.ai_schema import AIAnalysisRequest, AIAnalysisResponse
from app.services.monitoring_service import MonitoringService
from app.services.anomaly_service import AnomalyService
from app.services.ai_service import AIService
from app.services.api_service import ApiService
from app.schemas.user_schema import UserResponse

router = APIRouter()


@router.get("/logs", response_model=MonitoringLogListResponse)
async def get_monitoring_logs(
    api_endpoint_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 50,
    status_filter: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get monitoring logs for user's endpoints."""
    monitoring_service = MonitoringService(db)
    
    logs, total = await monitoring_service.get_logs(
        user_id=current_user.id,
        api_endpoint_id=api_endpoint_id,
        page=page,
        page_size=page_size,
        status_filter=status_filter
    )
    
    return MonitoringLogListResponse(
        items=logs,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/logs/{log_id}", response_model=MonitoringLogResponse)
async def get_monitoring_log(
    log_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific monitoring log."""
    monitoring_service = MonitoringService(db)
    
    log = await monitoring_service.get_log(
        log_id=log_id,
        user_id=current_user.id
    )
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )
    
    return log


@router.get("/endpoints/{endpoint_id}/anomalies", response_model=List[AnomalyResponse])
async def get_endpoint_anomalies(
    endpoint_id: int,
    window_hours: int = Query(default=24, ge=1, le=168),
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get anomalies for a specific endpoint."""
    anomaly_service = AnomalyService(db)
    api_service = ApiService(db)
    
    endpoint = await api_service.get_endpoint(endpoint_id, current_user.id)
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found"
        )
    
    anomalies = await anomaly_service.detect_anomalies(
        api_endpoint_id=endpoint_id,
        window_hours=window_hours
    )
    
    return [
        AnomalyResponse(
            log_id=log.id,
            checked_at=log.checked_at,
            response_time=log.response_time,
            status_code=log.status_code,
            anomaly_score=score
        )
        for log, score in anomalies
    ]


@router.get("/endpoints/{endpoint_id}/baseline")
async def get_response_time_baseline(
    endpoint_id: int,
    window_hours: int = Query(default=24, ge=1, le=168),
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get response time baseline statistics for an endpoint."""
    anomaly_service = AnomalyService(db)
    api_service = ApiService(db)
    
    endpoint = await api_service.get_endpoint(endpoint_id, current_user.id)
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found"
        )
    
    baseline = await anomaly_service.get_response_time_baseline(
        api_endpoint_id=endpoint_id,
        window_hours=window_hours
    )
    
    if not baseline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enough data for baseline calculation"
        )
    
    return baseline


@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_endpoint(
    analysis_request: AIAnalysisRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger AI analysis for an endpoint."""
    ai_service = AIService(db)
    api_service = ApiService(db)
    
    endpoint = await api_service.get_endpoint(analysis_request.endpoint_id, current_user.id)
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found"
        )
    
    result = await ai_service.analyze_failures(
        api_endpoint_id=analysis_request.endpoint_id,
        user_id=current_user.id,
        log_ids=analysis_request.log_ids if analysis_request.log_ids else None,
        hours=analysis_request.hours
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough failure data for analysis"
        )
    
    return result
