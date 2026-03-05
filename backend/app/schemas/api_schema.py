"""
API Endpoint Pydantic schemas for request/response validation.
"""
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, HttpUrl, ConfigDict, field_validator

from app.models.api import HttpMethod


class ApiEndpointBase(BaseModel):
    """Base API endpoint schema."""
    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., max_length=2048)
    method: HttpMethod = HttpMethod.GET
    headers: Optional[Dict[str, str]] = None
    body: Optional[Any] = None
    expected_status_code: int = Field(default=200, ge=100, le=599)
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    interval_seconds: int = Field(default=60, ge=10, le=3600)


class ApiEndpointCreate(ApiEndpointBase):
    """Schema for creating a new API endpoint."""
    pass


class ApiEndpointUpdate(BaseModel):
    """Schema for updating an API endpoint."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = Field(None, max_length=2048)
    method: Optional[HttpMethod] = None
    headers: Optional[Dict[str, str]] = None
    body: Optional[Any] = None
    expected_status_code: Optional[int] = Field(None, ge=100, le=599)
    timeout_seconds: Optional[int] = Field(None, ge=1, le=300)
    interval_seconds: Optional[int] = Field(None, ge=10, le=3600)
    is_active: Optional[bool] = None
    is_paused: Optional[bool] = None


class ApiEndpointResponse(ApiEndpointBase):
    """Schema for API endpoint response."""
    id: int
    user_id: int
    is_active: bool
    is_paused: bool
    status: Optional[str] = None  # "UP" or "DOWN" - explicit health status
    last_status_code: Optional[int] = None
    last_response_time: Optional[float] = None
    avg_response_time: Optional[float] = None
    last_checked_at: Optional[datetime] = None
    uptime_percentage: float
    total_checks: int
    successful_checks: int
    failed_checks: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('headers', mode='before')
    @classmethod
    def parse_headers(cls, v):
        """Parse headers from JSON string if needed."""
        if v is None:
            return None
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return None
    
    @field_validator('body', mode='before')
    @classmethod
    def parse_body(cls, v):
        """Parse body from JSON string if needed."""
        if v is None:
            return None
        if isinstance(v, (dict, list, str, int, float, bool)):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return v
        return v


class ApiEndpointListResponse(BaseModel):
    """Schema for API endpoint list response."""
    total: int
    page: int
    page_size: int
    items: List[ApiEndpointResponse]


class ApiEndpointStats(BaseModel):
    """Schema for API endpoint statistics."""
    uptime_percentage: float
    avg_response_time: float
    total_checks: int
    successful_checks: int
    failed_checks: int
    last_24h_checks: int
    last_24h_failures: int
    current_streak: int
    longest_uptime_streak: int
    longest_downtime_streak: int
