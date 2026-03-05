"""
Monitoring Pydantic schemas for request/response validation.
"""
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_serializer

from app.models.monitoring_log import CheckStatus


class MonitoringLogBase(BaseModel):
    """Base monitoring log schema."""
    status: CheckStatus
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    response_body: Optional[str] = None


class MonitoringLogResponse(MonitoringLogBase):
    """Schema for monitoring log response."""
    id: int
    api_endpoint_id: int
    user_id: int
    is_anomaly: bool
    anomaly_score: Optional[float] = None
    request_method: Optional[str] = None
    request_url: Optional[str] = None
    checked_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_serializer('checked_at')
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime as ISO 8601 string with UTC timezone."""
        # Ensure the datetime is timezone-aware (UTC)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


class MonitoringLogListResponse(BaseModel):
    """Schema for monitoring log list response."""
    total: int
    page: int
    page_size: int
    items: List[MonitoringLogResponse]


class MonitoringLogCreate(MonitoringLogBase):
    """Schema for creating a monitoring log."""
    api_endpoint_id: int
    user_id: int
    is_anomaly: bool = False
    anomaly_score: Optional[float] = None
    request_method: Optional[str] = None
    request_url: Optional[str] = None


class CheckHistoryFilter(BaseModel):
    """Filter parameters for check history."""
    api_endpoint_id: Optional[int] = None
    status: Optional[CheckStatus] = None
    is_anomaly: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CheckSummary(BaseModel):
    """Summary of checks for a time period."""
    total_checks: int
    successful_checks: int
    failed_checks: int
    timeout_checks: int
    error_checks: int
    avg_response_time: float
    min_response_time: Optional[float] = None
    max_response_time: Optional[float] = None
    uptime_percentage: float
    anomaly_count: int


class MetricsResponse(BaseModel):
    """Response schema for metrics overview."""
    total_checks: int
    successful_checks: int
    failed_checks: int
    uptime_percentage: float
    avg_response_time: float
    error_rate: float
    avg_response_time_p95: float
    anomaly_count: int


class UptimeResponse(BaseModel):
    """Response schema for uptime metrics."""
    uptime_percentage: float
    total_downtime_minutes: float
    total_checks: int
    successful_checks: int
    failed_checks: int
    downtime_periods: List[dict]


class TimeSeriesDataPoint(BaseModel):
    """Single data point in time series."""
    timestamp: str
    value: float


class TimeSeriesData(BaseModel):
    """Response schema for time series data."""
    data: List[TimeSeriesDataPoint]
    start_time: datetime
    end_time: datetime
    interval_minutes: int
    
    @field_serializer('start_time')
    def serialize_start_time(self, dt: datetime) -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    
    @field_serializer('end_time')
    def serialize_end_time(self, dt: datetime) -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


class AnomalyResponse(BaseModel):
    """Response schema for anomaly data."""
    log_id: int
    checked_at: datetime
    response_time: Optional[float]
    status_code: Optional[int]
    anomaly_score: float
    
    @field_serializer('checked_at')
    def serialize_checked_at(self, dt: datetime) -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


class DowntimePeriod(BaseModel):
    """Schema for downtime period."""
    start_time: datetime
    end_time: datetime
    duration_minutes: float
    error_message: Optional[str] = None
    
    @field_serializer('start_time')
    def serialize_start_time(self, dt: datetime) -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    
    @field_serializer('end_time')
    def serialize_end_time(self, dt: datetime) -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
