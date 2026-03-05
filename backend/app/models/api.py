"""
API Endpoint database model.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, Enum as SQLEnum, Index, ForeignKey
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class HttpMethod(str, enum.Enum):
    """HTTP methods supported for monitoring."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ApiEndpoint(Base):
    """API endpoint model for monitored APIs."""
    
    __tablename__ = "api_endpoints"
    __table_args__ = (
        # Composite index for user queries with active status
        Index('ix_api_endpoints_user_id_is_active', 'user_id', 'is_active'),
        # Composite index for monitoring queries
        Index('ix_api_endpoints_is_active_paused', 'is_active', 'is_paused'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(String(2048), nullable=False)
    method = Column(SQLEnum(HttpMethod), default=HttpMethod.GET)
    headers = Column(Text, nullable=True)  # JSON string for headers
    body = Column(Text, nullable=True)  # JSON string for request body
    expected_status_code = Column(Integer, default=200)
    timeout_seconds = Column(Integer, default=30)
    interval_seconds = Column(Integer, default=60)  # Monitoring interval
    is_active = Column(Boolean, default=True)
    is_paused = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Explicit status field - stores actual health check result (UP, DOWN, or None for unknown)
    status = Column(String(10), nullable=True)  # "UP", "DOWN", or None (unknown/not yet checked)
    
    # Computed fields (updated by monitoring)
    last_status_code = Column(Integer, nullable=True)
    last_response_time = Column(Float, nullable=True)  # in milliseconds
    last_checked_at = Column(DateTime, nullable=True)
    uptime_percentage = Column(Float, default=100.0)
    total_checks = Column(Integer, default=0)
    successful_checks = Column(Integer, default=0)
    failed_checks = Column(Integer, default=0)
    
    # Relationships
    owner = relationship("User", back_populates="api_endpoints")
    monitoring_logs = relationship(
        "MonitoringLog", 
        back_populates="api_endpoint", 
        cascade="all, delete-orphan"
    )
    ai_insights = relationship(
        "AIInsight", 
        back_populates="api_endpoint", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<ApiEndpoint(id={self.id}, name={self.name}, url={self.url})>"
