"""
Monitoring API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

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
from app.monitoring_engine.task_manager import get_task_manager
from app.monitoring_engine.health_checker import run_health_check, run_health_check_single_endpoint

router = APIRouter()


@router.post("/test-monitor")
async def test_monitor_endpoint(
    endpoint_id: Optional[int] = None,
    current_user: UserResponse = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Test endpoint to manually trigger a monitoring cycle."""
    try:
        if endpoint_id:
            result = await run_health_check_single_endpoint(endpoint_id)
            if "error" in result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
            return {"message": "Single endpoint check completed", "result": result}
        else:
            result = await run_health_check()
            return {"message": "Full monitoring cycle completed", "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Monitoring check failed: {str(e)}")


@router.get("/status")
async def get_monitoring_status(current_user: UserResponse = Depends(get_current_active_user)) -> Dict[str, Any]:
    """Get the current monitoring status."""
    task_manager = get_task_manager()
    status_info = task_manager.get_status()
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import select, func
    from app.models.api import ApiEndpoint
    from app.models.monitoring_log import MonitoringLog
    async with AsyncSessionLocal() as db:
        active_result = await db.execute(select(func.count(ApiEndpoint.id)).where(ApiEndpoint.is_active == True, ApiEndpoint.is_paused == False))
        active_count = active_result.scalar() or 0
        from datetime import datetime
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        logs_result = await db.execute(select(func.count(MonitoringLog.id)).where(MonitoringLog.checked_at >= today_start))
        logs_count = logs_result.scalar() or 0
    return {"monitoring_active": status_info["is_running"], "active_endpoints": active_count, "logs_today": logs_count, "jobs": status_info["jobs"]}


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
    
    endpoint = await api_service.get_endpoint(analysis_request.api_endpoint_id, current_user.id)
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found"
        )
    
    try:
        result = await ai_service.analyze_failures(
            api_endpoint_id=analysis_request.api_endpoint_id,
            user_id=current_user.id,
            log_ids=analysis_request.log_ids if analysis_request.log_ids else None,
            hours=analysis_request.time_range_hours
        )
        
        # Commit the insight to the database
        await db.commit()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough failure data for analysis"
            )
        
        return result
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/endpoints/{endpoint_id}/insights")
async def get_endpoint_insights(
    endpoint_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI insights for a specific endpoint."""
    from sqlalchemy import select
    from app.models.ai_insight import AIInsight
    
    # Verify endpoint exists and belongs to user
    api_service = ApiService(db)
    endpoint = await api_service.get_endpoint(endpoint_id, current_user.id)
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found"
        )
    
    # Get insights for this endpoint
    result = await db.execute(
        select(AIInsight)
        .where(
            AIInsight.api_endpoint_id == endpoint_id,
            AIInsight.user_id == current_user.id
        )
        .order_by(AIInsight.created_at.desc())
        .limit(20)
    )
    insights = list(result.scalars().all())
    
    return insights


@router.get("/endpoints/{endpoint_id}/latency-history")
async def get_latency_history(
    endpoint_id: int,
    hours: int = Query(default=24, ge=1, le=168),
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get latency history for a specific endpoint.
    
    Returns list of {time, latency} objects for charting.
    """
    from sqlalchemy import select
    from datetime import datetime, timedelta
    from app.models.monitoring_log import MonitoringLog, CheckStatus
    
    # Verify endpoint exists and belongs to user
    api_service = ApiService(db)
    endpoint = await api_service.get_endpoint(endpoint_id, current_user.id)
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found"
        )
    
    # Get latency data
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    result = await db.execute(
        select(MonitoringLog)
        .where(
            MonitoringLog.api_endpoint_id == endpoint_id,
            MonitoringLog.checked_at >= cutoff_time,
            MonitoringLog.response_time.isnot(None),
            MonitoringLog.status == CheckStatus.SUCCESS
        )
        .order_by(MonitoringLog.checked_at.asc())
    )
    logs = list(result.scalars().all())
    
    # Return in format: [{time: "...", latency: 512}, ...]
    return [
        {
            "time": log.checked_at.isoformat(),
            "latency": log.response_time
        }
        for log in logs
    ]
