"""AI Insight Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.models.ai_insight import InsightType, SeverityLevel


class AIInsightBase(BaseModel):
    """Base AI insight schema."""
    insight_type: InsightType = InsightType.FAILURE_ANALYSIS
    severity: SeverityLevel = SeverityLevel.MEDIUM
    title: str = Field(..., min_length=1, max_length=500)


class AIInsightCreate(AIInsightBase):
    """Schema for creating an AI insight."""
    api_endpoint_id: int
    user_id: int
    summary: str
    possible_causes: Optional[List[str]] = None
    suggested_steps: Optional[List[str]] = None
    triggered_by_log_id: Optional[int] = None
    related_logs_summary: Optional[str] = None
    confidence_score: Optional[float] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    
    model_config = ConfigDict(protected_namespaces=())


class AIInsightUpdate(BaseModel):
    """Schema for updating an AI insight."""
    is_read: Optional[str] = None  # unread, read, dismissed
    is_resolved: Optional[bool] = None
    severity: Optional[SeverityLevel] = None


class AIInsightResponse(AIInsightBase):
    """Schema for AI insight response."""
    id: int
    api_endpoint_id: int
    user_id: int
    summary: str
    possible_causes: Optional[str] = None  # JSON string
    suggested_steps: Optional[str] = None  # JSON string
    triggered_by_log_id: Optional[int] = None
    related_logs_summary: Optional[str] = None
    confidence_score: Optional[float] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    is_read: str
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class AIInsightListResponse(BaseModel):
    """Schema for AI insight list response."""
    total: int
    page: int
    page_size: int
    items: List[AIInsightResponse]


class AIAnalysisRequest(BaseModel):
    """Schema for requesting AI analysis."""
    api_endpoint_id: int
    log_ids: Optional[List[int]] = None
    time_range_hours: int = Field(default=24, ge=1, le=168)
    analysis_type: InsightType = InsightType.FAILURE_ANALYSIS
    
    model_config = ConfigDict(protected_namespaces=())


class AIAnalysisResponse(BaseModel):
    """Schema for AI analysis response."""
    summary: str = ""
    possible_causes: List[str] = Field(default_factory=list)
    suggested_steps: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0
    model_used: str = "system"
    tokens_used: int = 0
    
    model_config = ConfigDict(protected_namespaces=())
