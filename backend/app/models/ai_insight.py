"""
AI Insight database model.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Float, Boolean
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class InsightType(str, enum.Enum):
    """Type of AI insight."""
    ANOMALY_DETECTION = "anomaly_detection"
    FAILURE_ANALYSIS = "failure_analysis"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    ROOT_CAUSE = "root_cause"
    SUGGESTION = "suggestion"


class SeverityLevel(str, enum.Enum):
    """Severity level of the insight."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AIInsight(Base):
    """AI Insight model for storing AI-generated analysis."""
    
    __tablename__ = "ai_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    api_endpoint_id = Column(Integer, ForeignKey("api_endpoints.id"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    
    # Insight details
    insight_type = Column(SQLEnum(InsightType), default=InsightType.FAILURE_ANALYSIS)
    severity = Column(SQLEnum(SeverityLevel), default=SeverityLevel.MEDIUM)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)  # AI-generated summary
    
    # Detailed information
    possible_causes = Column(Text, nullable=True)  # JSON array of causes
    suggested_steps = Column(Text, nullable=True)  # JSON array of debugging steps
    
    # Related data
    triggered_by_log_id = Column(Integer, ForeignKey("monitoring_logs.id"), nullable=True)
    related_logs_summary = Column(Text, nullable=True)  # Summary of logs sent to AI
    
    # Confidence and metadata
    confidence_score = Column(Float, nullable=True)  # AI confidence 0-1
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    
    # Status
    is_read = Column(String(20), default="unread")  # unread, read, dismissed
    is_resolved = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    api_endpoint = relationship("ApiEndpoint", back_populates="ai_insights")
    user = relationship("User", back_populates="ai_insights")
    triggered_by_log = relationship("MonitoringLog", foreign_keys=[triggered_by_log_id])
    
    def __repr__(self):
        return f"<AIInsight(id={self.id}, api_endpoint_id={self.api_endpoint_id}, insight_type={self.insight_type})>"
