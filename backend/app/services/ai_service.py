"""
AI service for generating insights and analyzing monitoring data.
"""
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monitoring_log import MonitoringLog, CheckStatus
from app.models.ai_insight import AIInsight, InsightType, SeverityLevel
from app.schemas.ai_schema import AIAnalysisRequest, AIAnalysisResponse
from app.services.monitoring_service import MonitoringService
from app.ai.llm_client import LLMClient
from app.ai.prompt_templates import (
    get_failure_analysis_prompt,
    get_anomaly_analysis_prompt,
    get_performance_degradation_prompt
)


class AIService:
    """Service for AI-powered analysis and insights."""
    
    # Number of consecutive failures to trigger AI analysis (lowered for testing)
    FAILURE_THRESHOLD = 1
    # Maximum logs to send to AI for analysis
    MAX_LOGS_FOR_ANALYSIS = 20
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.monitoring_service = MonitoringService(db)
        self.llm_client = LLMClient()
    
    async def analyze_failures(
        self,
        api_endpoint_id: int,
        user_id: int,
        log_ids: Optional[List[int]] = None,
        hours: int = 24
    ) -> Optional[AIAnalysisResponse]:
        """Analyze recent failures and generate insights."""
        # Get logs for analysis
        if log_ids:
            # Get specific logs
            from sqlalchemy import select
            result = await self.db.execute(
                select(MonitoringLog).where(
                    MonitoringLog.id.in_(log_ids),
                    MonitoringLog.api_endpoint_id == api_endpoint_id
                )
            )
            logs = list(result.scalars().all())
        else:
            # Get recent logs with failures
            logs = await self.monitoring_service.get_logs_for_analysis(
                api_endpoint_id=api_endpoint_id,
                hours=hours,
                limit=self.MAX_LOGS_FOR_ANALYSIS
            )
        
        if not logs:
            # Even if no logs, create a general insight about the endpoint
            return await self._create_general_insight(api_endpoint_id, user_id, hours)
        
        # Filter to only failure logs
        failure_logs = [
            log for log in logs 
            if log.status in [CheckStatus.FAILURE, CheckStatus.ERROR, CheckStatus.TIMEOUT]
        ]
        
        # If no failures, analyze all logs for general performance insights
        if len(failure_logs) < self.FAILURE_THRESHOLD:
            # Analyze the endpoint even without failures for general insights
            return await self._create_general_insight_from_logs(api_endpoint_id, user_id, logs, hours)
        
        # Generate prompt
        prompt = get_failure_analysis_prompt(failure_logs)
        
        # Get AI response
        ai_response = await self.llm_client.generate(prompt)
        
        if not ai_response:
            # Create a fallback insight without AI
            return await self._create_fallback_insight(api_endpoint_id, user_id, failure_logs)
        
        # Parse AI response - handle both dict (mock) and string (real API)
        if isinstance(ai_response, dict):
            analysis = ai_response
        else:
            try:
                analysis = json.loads(ai_response)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                analysis = self._extract_json_from_response(ai_response)
        
        if not analysis:
            return await self._create_fallback_insight(api_endpoint_id, user_id, failure_logs)
        
        # Determine severity
        severity = self._determine_severity(len(failure_logs), len(logs))
        
        # Create AI insight
        insight = await self._create_insight(
            api_endpoint_id=api_endpoint_id,
            user_id=user_id,
            insight_type=InsightType.FAILURE_ANALYSIS,
            severity=severity,
            title=analysis.get("summary", "Failure Analysis")[:500],
            summary=analysis.get("summary", ""),
            possible_causes=analysis.get("possible_causes", []),
            suggested_steps=analysis.get("suggested_steps", []),
            related_logs_summary=self._summarize_logs(failure_logs),
            triggered_by_log_id=failure_logs[0].id if failure_logs else None,
            confidence_score=analysis.get("confidence", 0.5),
            model_used=self.llm_client.model_name,
            tokens_used=ai_response.get("tokens_used", 0) if isinstance(ai_response, dict) else 0
        )
        
        return AIAnalysisResponse(
            summary=analysis.get("summary", ""),
            possible_causes=analysis.get("possible_causes", []),
            suggested_steps=analysis.get("suggested_steps", []),
            confidence_score=analysis.get("confidence", 0.5),
            model_used=self.llm_client.model_name,
            tokens_used=ai_response.get("tokens_used", 0) if isinstance(ai_response, dict) else 0
        )
    
    async def _create_general_insight(
        self,
        api_endpoint_id: int,
        user_id: int,
        hours: int
    ) -> Optional[AIAnalysisResponse]:
        """Create a general insight even without logs."""
        insight = await self._create_insight(
            api_endpoint_id=api_endpoint_id,
            user_id=user_id,
            insight_type=InsightType.FAILURE_ANALYSIS,
            severity=SeverityLevel.LOW,
            title="Endpoint Monitored",
            summary=f"This endpoint has been under monitoring for the past {hours} hours. No failures detected. Keep monitoring to establish a baseline.",
            possible_causes=[],
            suggested_steps=[
                "Continue monitoring to establish performance baseline",
                "Review response times for optimization opportunities",
                "Set up alerts for any anomalies"
            ],
            related_logs_summary="No logs available yet",
            triggered_by_log_id=None,
            confidence_score=1.0,
            model_used="system",
            tokens_used=0
        )
        
        return AIAnalysisResponse(
            summary=insight.summary,
            possible_causes=[],
            suggested_steps=insight.suggested_steps.split('\n') if insight.suggested_steps else [],
            confidence_score=1.0,
            model_used="system",
            tokens_used=0
        )
    
    async def _create_general_insight_from_logs(
        self,
        api_endpoint_id: int,
        user_id: int,
        logs: List[MonitoringLog],
        hours: int
    ) -> Optional[AIAnalysisResponse]:
        """Create a general performance insight from successful logs."""
        if not logs:
            return await self._create_general_insight(api_endpoint_id, user_id, hours)
        
        # Calculate basic stats
        response_times = [log.response_time for log in logs if log.response_time]
        avg_response = sum(response_times) / len(response_times) if response_times else 0
        min_response = min(response_times) if response_times else 0
        max_response = max(response_times) if response_times else 0
        
        success_count = sum(1 for log in logs if log.status == CheckStatus.SUCCESS)
        total_count = len(logs)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        insight = await self._create_insight(
            api_endpoint_id=api_endpoint_id,
            user_id=user_id,
            insight_type=InsightType.FAILURE_ANALYSIS,
            severity=SeverityLevel.LOW,
            title="Performance Analysis Complete",
            summary=f"Analysis of {total_count} checks over {hours} hours: {success_rate:.1f}% success rate with avg response time {avg_response:.2f}ms",
            possible_causes=[
                "Normal operation - no issues detected",
                "Endpoint is responding within expected parameters"
            ],
            suggested_steps=[
                f"Average response time: {avg_response:.2f}ms",
                f"Min response time: {min_response:.2f}ms",
                f"Max response time: {max_response:.2f}ms",
                "Continue monitoring for any changes in patterns"
            ],
            related_logs_summary=self._summarize_logs(logs[:5]),
            triggered_by_log_id=logs[0].id if logs else None,
            confidence_score=0.9,
            model_used="system",
            tokens_used=0
        )
        
        return AIAnalysisResponse(
            summary=insight.summary,
            possible_causes=["Normal operation - no issues detected"],
            suggested_steps=[
                f"Average response time: {avg_response:.2f}ms",
                f"Min response time: {min_response:.2f}ms", 
                f"Max response time: {max_response:.2f}ms"
            ],
            confidence_score=0.9,
            model_used="system",
            tokens_used=0
        )
    
    async def _create_fallback_insight(
        self,
        api_endpoint_id: int,
        user_id: int,
        failure_logs: List[MonitoringLog]
    ) -> Optional[AIAnalysisResponse]:
        """Create a fallback insight without AI response."""
        # Get common error patterns
        error_messages = [log.error_message for log in failure_logs if log.error_message]
        status_codes = [log.status_code for log in failure_logs if log.status_code]
        
        summary = f"Detected {len(failure_logs)} failed checks. "
        if status_codes:
            most_common_status = max(set(status_codes), key=status_codes.count)
            summary += f"Most common status code: {most_common_status}. "
        if error_messages:
            summary += f"Sample error: {error_messages[0][:100]}"
        
        insight = await self._create_insight(
            api_endpoint_id=api_endpoint_id,
            user_id=user_id,
            insight_type=InsightType.FAILURE_ANALYSIS,
            severity=SeverityLevel.HIGH,
            title="Failures Detected",
            summary=summary,
            possible_causes=[
                "Service temporarily unavailable",
                "Rate limiting applied",
                "Network connectivity issues",
                "Invalid request parameters"
            ],
            suggested_steps=[
                "Check service status",
                "Verify API credentials",
                "Review rate limits",
                "Check network connectivity"
            ],
            related_logs_summary=self._summarize_logs(failure_logs[:5]),
            triggered_by_log_id=failure_logs[0].id if failure_logs else None,
            confidence_score=0.7,
            model_used="system",
            tokens_used=0
        )
        
        return AIAnalysisResponse(
            summary=insight.summary,
            possible_causes=insight.possible_causes.split(',') if insight.possible_causes else [],
            suggested_steps=insight.suggested_steps.split('\n') if insight.suggested_steps else [],
            confidence_score=0.7,
            model_used="system",
            tokens_used=0
        )
    
    async def analyze_anomaly(
        self,
        api_endpoint_id: int,
        user_id: int,
        anomaly_logs: List[MonitoringLog]
    ) -> Optional[AIAnalysisResponse]:
        """Analyze detected anomalies."""
        if not anomaly_logs:
            return None
        
        # Generate prompt
        prompt = get_anomaly_analysis_prompt(anomaly_logs)
        
        # Get AI response
        ai_response = await self.llm_client.generate(prompt)
        
        if not ai_response:
            return None
        
        # Parse AI response - handle both dict (mock) and string (real API)
        if isinstance(ai_response, dict):
            analysis = ai_response
        else:
            try:
                analysis = json.loads(ai_response)
            except json.JSONDecodeError:
                analysis = self._extract_json_from_response(ai_response)
        
        if not analysis:
            return None
        
        # Determine severity
        severity = SeverityLevel.MEDIUM
        
        # Create AI insight
        insight = await self._create_insight(
            api_endpoint_id=api_endpoint_id,
            user_id=user_id,
            insight_type=InsightType.ANOMALY_DETECTION,
            severity=severity,
            title=analysis.get("summary", "Anomaly Detected")[:500],
            summary=analysis.get("summary", ""),
            possible_causes=analysis.get("possible_causes", []),
            suggested_steps=analysis.get("suggested_steps", []),
            related_logs_summary=self._summarize_logs(anomaly_logs),
            triggered_by_log_id=anomaly_logs[0].id if anomaly_logs else None,
            confidence_score=analysis.get("confidence", 0.5),
            model_used=self.llm_client.model_name,
            tokens_used=ai_response.get("tokens_used", 0) if isinstance(ai_response, dict) else 0
        )
        
        return AIAnalysisResponse(
            summary=analysis.get("summary", ""),
            possible_causes=analysis.get("possible_causes", []),
            suggested_steps=analysis.get("suggested_steps", []),
            confidence_score=analysis.get("confidence", 0.5),
            model_used=self.llm_client.model_name,
            tokens_used=ai_response.get("tokens_used", 0) if isinstance(ai_response, dict) else 0
        )
    
    async def check_and_trigger_analysis(
        self,
        api_endpoint_id: int,
        user_id: int
    ) -> Optional[AIInsight]:
        """Check if AI analysis should be triggered based on failure count."""
        # Get count of recent failures
        failed_count = await self.monitoring_service.get_failed_checks_count(
            api_endpoint_id=api_endpoint_id,
            minutes=10
        )
        
        if failed_count >= self.FAILURE_THRESHOLD:
            # Trigger AI analysis
            result = await self.analyze_failures(
                api_endpoint_id=api_endpoint_id,
                user_id=user_id,
                hours=1
            )
            
            if result:
                # Get the created insight
                from sqlalchemy import select
                result = await self.db.execute(
                    select(AIInsight)
                    .where(
                        AIInsight.api_endpoint_id == api_endpoint_id,
                        AIInsight.user_id == user_id
                    )
                    .order_by(AIInsight.created_at.desc())
                    .limit(1)
                )
                return result.scalar_one_or_none()
        
        return None
    
    async def _create_insight(
        self,
        api_endpoint_id: int,
        user_id: int,
        insight_type: InsightType,
        severity: SeverityLevel,
        title: str,
        summary: str,
        possible_causes: Optional[List[str]] = None,
        suggested_steps: Optional[List[str]] = None,
        related_logs_summary: Optional[str] = None,
        triggered_by_log_id: Optional[int] = None,
        confidence_score: Optional[float] = None,
        model_used: Optional[str] = None,
        tokens_used: Optional[int] = None
    ) -> AIInsight:
        """Create an AI insight in the database."""
        insight = AIInsight(
            api_endpoint_id=api_endpoint_id,
            user_id=user_id,
            insight_type=insight_type,
            severity=severity,
            title=title,
            summary=summary,
            possible_causes=json.dumps(possible_causes) if possible_causes else None,
            suggested_steps=json.dumps(suggested_steps) if suggested_steps else None,
            related_logs_summary=related_logs_summary,
            triggered_by_log_id=triggered_by_log_id,
            confidence_score=confidence_score,
            model_used=model_used,
            tokens_used=tokens_used
        )
        
        self.db.add(insight)
        await self.db.flush()
        await self.db.refresh(insight)
        
        return insight
    
    # Public alias for create_insight (used by tests)
    async def create_insight(
        self,
        api_endpoint_id: int,
        user_id: int,
        insight_type: InsightType,
        title: str,
        summary: str,
        possible_causes: Optional[List[str]] = None,
        suggested_steps: Optional[List[str]] = None,
        confidence_score: Optional[float] = None,
        model_used: Optional[str] = None
    ) -> AIInsight:
        """Public method alias for creating AI insight."""
        return await self._create_insight(
            api_endpoint_id=api_endpoint_id,
            user_id=user_id,
            insight_type=insight_type,
            severity=SeverityLevel.MEDIUM,
            title=title,
            summary=summary,
            possible_causes=possible_causes,
            suggested_steps=suggested_steps,
            confidence_score=confidence_score,
            model_used=model_used
        )
    
    def _determine_severity(self, failure_count: int, total_count: int) -> SeverityLevel:
        """Determine severity based on failure count and ratio."""
        failure_ratio = failure_count / total_count if total_count > 0 else 0
        
        if failure_ratio >= 0.8 or failure_count >= 10:
            return SeverityLevel.CRITICAL
        elif failure_ratio >= 0.5 or failure_count >= 5:
            return SeverityLevel.HIGH
        elif failure_ratio >= 0.3 or failure_count >= 3:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW
    
    def _summarize_logs(self, logs: List[MonitoringLog]) -> str:
        """Summarize logs for AI context."""
        summary_parts = []
        
        for log in logs[:10]:  # Limit to 10 logs
            part = f"[{log.checked_at.isoformat() if log.checked_at else 'N/A'}] {log.status.value}"
            if log.status_code:
                part += f" - Status: {log.status_code}"
            if log.response_time:
                part += f" - Time: {log.response_time:.2f}ms"
            if log.error_message:
                part += f" - Error: {log.error_message[:100]}"
            summary_parts.append(part)
        
        return "\n".join(summary_parts)
    
    def _extract_json_from_response(self, response: str) -> Optional[dict]:
        """Extract JSON from AI response that might contain extra text."""
        import re
        
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        return None
