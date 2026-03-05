"""
API Endpoint Pydantic schemas for request/response validation.
"""
import json
import ipaddress
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from app.core.config import settings


# Define HttpMethod here to avoid circular imports
class HttpMethod(str, enum.Enum):
    """HTTP methods supported for monitoring."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


# SSRF Protection - Block private IP ranges and localhost
def validate_url_for_ssrf(url: str) -> str:
    """Validate URL to prevent SSRF attacks by blocking private/internal IPs."""
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    hostname = parsed.hostname
    
    if not hostname:
        raise ValueError("Invalid URL: no hostname provided")
    
    # Block localhost variants
    localhost_names = ('localhost', '127.0.0.1', '::1', '0.0.0.0')
    if hostname.lower() in localhost_names or hostname == '::':
        raise ValueError("URL cannot point to localhost or internal addresses")
    
    # Block private IP ranges
    try:
        ip = ipaddress.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)
        
        # Block private addresses (192.168.x.x, 10.x.x.x, 172.16-31.x.x)
        if ip_obj.is_private:
            raise ValueError("URL cannot point to private network addresses")
        
        # Block loopback
        if ip_obj.is_loopback:
            raise ValueError("URL cannot point to loopback addresses")
        
        # Block link-local
        if ip_obj.is_link_local:
            raise ValueError("URL cannot point to link-local addresses")
        
        # Block multicast
        if ip_obj.is_multicast:
            raise ValueError("URL cannot point to multicast addresses")
        
        # Block reserved addresses
        if ip_obj.is_reserved:
            raise ValueError("URL cannot point to reserved addresses")
            
    except ipaddress.AddressValueError:
        # DNS resolution failed - could be an invalid hostname
        # Allow it but warn
        pass
    
    return url


class ApiEndpointBase(BaseModel):
    """Base API endpoint schema."""
    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., max_length=2048)
    method: HttpMethod = HttpMethod.GET
    headers: Optional[Dict[str, str]] = None
    body: Optional[Any] = None
    expected_status_code: int = Field(default=200, ge=100, le=599)
    timeout_seconds: int = Field(
        default=settings.max_timeout_seconds, 
        ge=1, 
        le=settings.max_timeout_seconds
    )
    interval_seconds: int = Field(
        default=settings.min_interval_seconds,
        ge=settings.min_interval_seconds, 
        le=settings.max_interval_seconds
    )


class ApiEndpointCreate(ApiEndpointBase):
    """Schema for creating a new API endpoint."""
    
    @model_validator(mode='after')
    def validate_url(self):
        """Validate URL to prevent SSRF attacks."""
        validate_url_for_ssrf(self.url)
        return self


class ApiEndpointUpdate(BaseModel):
    """Schema for updating an API endpoint."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = Field(None, max_length=2048)
    method: Optional[HttpMethod] = None
    headers: Optional[Dict[str, str]] = None
    body: Optional[Any] = None
    expected_status_code: Optional[int] = Field(None, ge=100, le=599)
    timeout_seconds: Optional[int] = Field(None, ge=1, le=settings.max_timeout_seconds)
    interval_seconds: Optional[int] = Field(None, ge=settings.min_interval_seconds, le=settings.max_interval_seconds)
    is_active: Optional[bool] = None
    is_paused: Optional[bool] = None
    
    @model_validator(mode='after')
    def validate_url_if_provided(self):
        """Validate URL if provided in update."""
        if self.url:
            validate_url_for_ssrf(self.url)
        return self


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

