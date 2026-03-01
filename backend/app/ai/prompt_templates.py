"""
Prompt templates for AI analysis.
"""
from typing import List
import json

from app.models.monitoring_log import MonitoringLog


def get_failure_analysis_prompt(logs: List[MonitoringLog]) -> str:
    """Generate prompt for failure analysis."""
    log_summary = []
    
    for log in logs:
        entry = {
            "timestamp": log.checked_at.isoformat(),
            "status": log.status.value,
            "status_code": log.status_code,
            "response_time_ms": log.response_time,
            "error": log.error_message
        }
        log_summary.append(entry)
    
    logs_json = json.dumps(log_summary, indent=2)
    
    prompt = f"""You are an expert at debugging API failures. Analyze the following monitoring logs and provide a detailed failure analysis.

## Monitoring Logs:
{logs_json}

## Task:
Analyze these logs and provide a JSON response with the following structure:
{{
    "summary": "A brief summary of what's happening (1-2 sentences)",
    "possible_causes": [
        "List of possible root causes of the failures"
    ],
    "suggested_steps": [
        "Step-by-step debugging instructions"
    ],
    "confidence": 0.0-1.0 indicating how confident you are in this analysis
}}

Be specific and actionable in your suggestions. Consider factors like:
- Error patterns and trends
- Response times
- Status codes
- Error messages

Provide only the JSON response, no additional text."""
    
    return prompt


def get_anomaly_analysis_prompt(logs: List[MonitoringLog]) -> str:
    """Generate prompt for anomaly analysis."""
    log_summary = []
    
    for log in logs:
        entry = {
            "timestamp": log.checked_at.isoformat(),
            "response_time_ms": log.response_time,
            "status": log.status.value,
            "anomaly_score": log.anomaly_score
        }
        log_summary.append(entry)
    
    logs_json = json.dumps(log_summary, indent=2)
    
    prompt = f"""You are an expert at detecting anomalies in API performance. Analyze the following monitoring logs and identify unusual patterns.

## Monitoring Logs:
{logs_json}

## Task:
Analyze these logs and provide a JSON response with the following structure:
{{
    "summary": "A brief summary of the anomaly detected (1-2 sentences)",
    "possible_causes": [
        "List of possible causes of the anomalous behavior"
    ],
    "suggested_steps": [
        "Step-by-step investigation steps"
    ],
    "confidence": 0.0-1.0 indicating how confident you are in this analysis
}}

Consider factors like:
- Unusual response time spikes
- Deviation from normal patterns
- Statistical outliers

Provide only the JSON response, no additional text."""
    
    return prompt


def get_performance_degradation_prompt(
    current_stats: dict,
    historical_stats: dict
) -> str:
    """Generate prompt for performance degradation analysis."""
    prompt = f"""You are an expert at analyzing API performance. Compare the current performance metrics with historical data and identify degradation.

## Current Performance (last 24 hours):
{json.dumps(current_stats, indent=2)}

## Historical Performance (previous 7 days):
{json.dumps(historical_stats, indent=2)}

## Task:
Analyze these metrics and provide a JSON response with the following structure:
{{
    "summary": "A brief summary of the performance degradation (1-2 sentences)",
    "possible_causes": [
        "List of possible causes of the degradation"
    ],
    "suggested_steps": [
        "Step-by-step optimization recommendations"
    ],
    "confidence": 0.0-1.0 indicating how confident you are in this analysis
}}

Consider factors like:
- Changes in response times
- Changes in error rates
- Traffic patterns
- Infrastructure issues

Provide only the JSON response, no additional text."""
    
    return prompt


def get_root_cause_analysis_prompt(logs: List[MonitoringLog], error_pattern: str) -> str:
    """Generate prompt for root cause analysis."""
    log_summary = []
    
    for log in logs:
        entry = {
            "timestamp": log.checked_at.isoformat(),
            "status": log.status.value,
            "status_code": log.status_code,
            "response_time_ms": log.response_time,
            "error": log.error_message,
            "response_body": log.response_body[:500] if log.response_body else None
        }
        log_summary.append(entry)
    
    logs_json = json.dumps(log_summary, indent=2)
    
    prompt = f"""You are an expert at finding root causes of API issues. Based on the error pattern: "{error_pattern}", analyze these logs.

## Monitoring Logs:
{logs_json}

## Task:
Provide a JSON response with the following structure:
{{
    "root_cause": "Most likely root cause of the issue",
    "evidence": "Supporting evidence from the logs",
    "verification_steps": [
        "Steps to verify this is the root cause"
    ],
    "fix_suggestions": [
        "Suggested fixes"
    ],
    "confidence": 0.0-1.0 indicating how confident you are in this analysis
}}

Provide only the JSON response, no additional text."""
    
    return prompt
