"""
Monitoring Log database model.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class CheckStatus(str, enum.Enum):
    """Status of a monitoring check."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"


class MonitoringLog(Base):
    """Monitoring log model for storing check results."""
    
    __tablename__ = "monitoring_logs"
    __table_args__ = (
        # Composite indexes for common queries
        Index('ix_monitoring_logs_endpoint_checked', 'api_endpoint_id', 'checked_at'),
        Index('ix_monitoring_logs_user_endpoint', 'user_id', 'api_endpoint_id'),
        Index('ix_monitoring_logs_status_checked', 'status', 'checked_at'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    api_endpoint_id = Column(Integer, ForeignKey("api_endpoints.id"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    
    # Check details
    status = Column(SQLEnum(CheckStatus), default=CheckStatus.SUCCESS)
    status_code = Column(Integer, nullable=True)
    response_time = Column(Float, nullable=True)  # in milliseconds
    error_message = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)  # Truncated response for debugging
    
    # Timestamp
    checked_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Anomaly detection
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float, nullable=True)
    
    # Request/Response details
    request_method = Column(String(10), nullable=True)
    request_url = Column(String(2048), nullable=True)
    
    # Relationships
    api_endpoint = relationship("ApiEndpoint", back_populates="monitoring_logs")
    user = relationship("User", back_populates="monitoring_logs")
    
    def __repr__(self):
        return f"<MonitoringLog(id={self.id}, api_endpoint_id={self.api_endpoint_id}, status={self.status})>"
