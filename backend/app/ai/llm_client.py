"""
LLM Client for AI-powered analysis.
"""
from typing import Optional, Dict, Any
import json
import random
from loguru import logger

from app.core.config import settings


class LLMClient:
    """Client for interacting with LLM APIs."""
    
    def __init__(self):
        self.client = None
        self.model_name = settings.ai_model
        self.max_tokens = settings.ai_max_tokens
        self.temperature = settings.ai_temperature
        self.mock_mode = not bool(settings.openai_api_key)
    
    def _get_client(self):
        """Get or create OpenAI client."""
        if self.mock_mode:
            return None
            
        if self.client is None:
            from openai import AsyncOpenAI
            if not settings.openai_api_key:
                self.mock_mode = True
                return None
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self.client
    
    def _generate_mock_response(self, prompt: str, response_format: str = "json") -> Dict[str, Any]:
        """Generate a mock response when API key is not configured."""
        # Generate mock AI analysis based on the prompt content
        if "failure" in prompt.lower() or "error" in prompt.lower():
            return {
                "summary": "Multiple failures detected. This could be caused by server overload, network issues, or API endpoint changes.",
                "possible_causes": [
                    "Server overload or high load",
                    "Network connectivity issues",
                    "API endpoint changes or deprecation",
                    "Authentication or authorization problems",
                    "Rate limiting"
                ],
                "suggested_steps": [
                    "Check server logs for errors",
                    "Verify API endpoint is still valid",
                    "Test network connectivity",
                    "Review recent deployment changes",
                    "Check rate limit configuration"
                ],
                "confidence": 0.75,
                "severity": "high"
            }
        elif "anomaly" in prompt.lower() or "response time" in prompt.lower():
            return {
                "summary": "Unusual response pattern detected. Response times have deviated significantly from the baseline.",
                "possible_causes": [
                    "Server resource constraints",
                    "Database query performance issues",
                    "Network latency spikes",
                    "Increased traffic volume",
                    "External service dependencies"
                ],
                "suggested_steps": [
                    "Monitor server CPU and memory usage",
                    "Review database query performance",
                    "Check network latency metrics",
                    "Analyze traffic patterns",
                    "Review external service status"
                ],
                "confidence": 0.65,
                "severity": "medium"
            }
        else:
            return {
                "summary": "Analysis completed. No significant issues detected at this time.",
                "possible_causes": [],
                "suggested_steps": [
                    "Continue monitoring",
                    "Review metrics periodically"
                ],
                "confidence": 0.5,
                "severity": "low"
            }
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[str] = "json"
    ) -> Optional[Dict[str, Any]]:
        """Generate a response from the LLM."""
        # Use mock mode if no API key
        if self.mock_mode:
            logger.info("Using mock mode for AI analysis (no API key configured)")
            return self._generate_mock_response(prompt, response_format)
        
        try:
            client = self._get_client()
            
            if client is None:
                return self._generate_mock_response(prompt, response_format)
            
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Make the API call
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"} if response_format == "json" else None
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                result = json.loads(content)
                result["tokens_used"] = response.usage.total_tokens if response.usage else 0
                return result
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse LLM response as JSON: {content}")
                return {"text": content, "tokens_used": response.usage.total_tokens if response.usage else 0}
        
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}. Falling back to mock mode.")
            return self._generate_mock_response(prompt, response_format)
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """Generate a text response from the LLM (non-JSON)."""
        # Use mock mode if no API key
        if self.mock_mode:
            mock_responses = [
                "The analysis indicates normal operation with no critical issues detected.",
                "Multiple error patterns suggest potential service degradation.",
                "Response time anomalies may indicate underlying infrastructure issues."
            ]
            return random.choice(mock_responses)
        
        try:
            client = self._get_client()
            
            if client is None:
                return random.choice([
                    "The analysis indicates normal operation with no critical issues detected.",
                    "Multiple error patterns suggest potential service degradation.",
                    "Response time anomalies may indicate underlying infrastructure issues."
                ])
            
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Make the API call
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
            return content
        
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return "Analysis temporarily unavailable. Please try again later."
    
    async def analyze_code(
        self,
        code: str,
        language: str = "python"
    ) -> Optional[Dict[str, Any]]:
        """Analyze code and provide insights."""
        prompt = f"""Analyze the following {language} code and provide insights about potential bugs, performance issues, or improvements:

```
{language}
{code}
```

Provide your analysis in JSON format with the following structure:
{{
    "issues": ["list of issues found"],
    "suggestions": ["list of suggestions"],
    "severity": "low/medium/high"
}}"""
        
        system_prompt = "You are an expert code reviewer. Analyze code carefully and provide detailed insights."
        
        return await self.generate(prompt, system_prompt=system_prompt)
    
    async def summarize_logs(
        self,
        logs: str,
        context: Optional[str] = None
    ) -> Optional[str]:
        """Summarize log entries."""
        prompt = f"""Summarize the following log entries{f': {context}' if context else ''}:

{logs}

Provide a concise summary of what happened and potential root causes."""
        
        system_prompt = "You are an expert at analyzing logs and identifying issues."
        
        return await self.generate_text(prompt, system_prompt=system_prompt)
