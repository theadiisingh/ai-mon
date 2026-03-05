"""
Application configuration module.
Loads settings from environment variables using pydantic-settings.
"""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=None,  # Don't load from .env file to avoid validation errors
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "AI MON"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # Environment detection
    # Set ENVIRONMENT=production to disable dev features
    # If not set, defaults to 'development' when debug=True, 'production' otherwise
    environment: str = ""

    # Database - Using SQLite for easier setup
    database_url: str = "sqlite+aiosqlite:///./aimon.db"

    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # AI/LLM
    openai_api_key: str = ""
    ai_model: str = "gpt-4"
    ai_max_tokens: int = 1000
    ai_temperature: float = 0.7

    # Monitoring
    monitoring_interval_seconds: int = 60
    max_retries: int = 3
    request_timeout_seconds: int = 30

    # Rate Limiting
    rate_limit_login_attempts: int = 5  # Login attempts per minute
    rate_limit_login_window: int = 60  # Window in seconds

    # Endpoint Limits
    max_endpoints_per_user: int = 100  # Maximum endpoints per user
    min_interval_seconds: int = 60  # Minimum monitoring interval
    max_interval_seconds: int = 3600  # Maximum monitoring interval
    max_timeout_seconds: int = 30  # Maximum timeout for health checks

    # AI Limits
    max_ai_insights_per_day: int = 10  # Max AI insights per user per day

    # Log Retention
    log_retention_days: int = 30  # Days to keep monitoring logs

    # Response Body Limits
    max_response_body_length: int = 10000  # Max characters to store

    # Health Check Concurrency
    max_concurrent_checks: int = 100  # Maximum concurrent health checks

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "ai-mon@example.com"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"

    @property
    def is_development(self) -> bool:
        """Determine if the application is running in development mode."""
        if self.environment:
            # Explicit environment setting takes priority
            return self.environment.lower() in ("development", "dev")
        # Default: development if debug is True, production otherwise
        return self.debug

    @property
    def is_production(self) -> bool:
        """Determine if the application is running in production mode."""
        if self.environment:
            return self.environment.lower() in ("production", "prod")
        return not self.debug

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string and return unique list."""
        # Parse explicitly configured origins
        origins = [origin.strip() for origin in self.cors_origins.split(",")]
        
        # Add explicit localhost origins for development (avoid duplicates using set)
        # These work with allow_credentials=True
        explicit_origins = [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8000",
        ]
        
        # Combine all origins and use set to remove duplicates, then convert back to list
        all_origins = origins + explicit_origins
        unique_origins = list(set(all_origins))
        
        return unique_origins

    @model_validator(mode='after')
    def validate_production_settings(self):
        """Validate production settings."""
        # In production, warn about default secret key
        if self.is_production:
            import warnings
            
            if self.secret_key == "your-secret-key-change-in-production":
                warnings.warn(
                    "WARNING: Using default secret_key in production! "
                    "Set SECRET_KEY environment variable for security."
                )
            
            if self.debug:
                warnings.warn(
                    "WARNING: Debug mode is enabled in production! "
                    "Set debug=False or ENVIRONMENT=production for security."
                )
        
        return self


# Simple approach - just use defaults for testing
settings = Settings()
