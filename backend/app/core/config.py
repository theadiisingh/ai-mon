"""
Application configuration module.
Loads settings from environment variables using pydantic-settings.
"""
import os
import secrets
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=None,  # Don't load from .env file - use environment variables directly
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields
    )

    # App
    app_name: str = "AI MON"
    app_version: str = "1.0.0"
    debug: bool = False  # Default to False for security - override with DEBUG=true for development
    host: str = "0.0.0.0"
    port: int = 8000

    # Environment detection
    # Set ENVIRONMENT=production to disable dev features
    # Set ENVIRONMENT=development to enable dev features
    # If not set, defaults based on debug setting
    environment: str = ""

    # Vercel deployment detection
    vercel: bool = False
    vercel_url: str = ""

    # Database - Using SQLite for easier setup
    database_url: str = "sqlite+aiosqlite:///./aimon.db"

    # JWT - Use stable key for development, override with env var in production
    secret_key: str = "dev-secret-key-change-in-production-12345678"
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

    def __init__(self, **kwargs):
        """Initialize settings with Vercel detection."""
        # Auto-detect Vercel environment
        if os.environ.get("VERCEL", "").lower() == "true":
            kwargs["vercel"] = True
            kwargs["vercel_url"] = os.environ.get("VERCEL_URL", "")
            # Auto-set production mode on Vercel
            if not kwargs.get("environment"):
                kwargs["environment"] = "production"
            if "debug" not in kwargs:
                kwargs["debug"] = False
        
        super().__init__(**kwargs)

    @property
    def is_vercel(self) -> bool:
        """Check if running on Vercel."""
        return self.vercel or os.environ.get("VERCEL", "").lower() == "true"

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
        # Also consider Vercel production
        if self.is_vercel:
            return True
        return not self.debug

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string and return unique list."""
        origins = [origin.strip() for origin in self.cors_origins.split(",")]
        
        # In development, add localhost origins
        if self.is_development:
            explicit_origins = [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://localhost:8000",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:8000",
            ]
            all_origins = origins + explicit_origins
        else:
            # In production, only use explicitly configured origins
            all_origins = origins
        
        # Also add Vercel URL if available
        if self.vercel_url:
            all_origins.append(f"https://{self.vercel_url}")
        
        return list(set(all_origins))

    @model_validator(mode='after')
    def validate_production_settings(self):
        """Validate production settings."""
        # In production, validate critical settings
        if self.is_production:
            import warnings
            
            # Check for default/insecure secret key (both old and new patterns)
            if (self.secret_key == "your-secret-key-change-in-production" or 
                self.secret_key == "dev-secret-key-change-in-production-12345678" or 
                len(self.secret_key) < 32):
                warnings.warn(
                    "WARNING: Using insecure secret_key in production! "
                    "Set a strong SECRET_KEY environment variable (min 32 chars). "
                    "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
                )
            
            # Warn about debug mode
            if self.debug:
                warnings.warn(
                    "WARNING: Debug mode is enabled in production! "
                    "Set DEBUG=false or ENVIRONMENT=production for security."
                )
            
            # Warn if using SQLite in production
            if "sqlite" in self.database_url.lower():
                warnings.warn(
                    "WARNING: Using SQLite in production is not recommended. "
                    "Consider using PostgreSQL for production deployments."
                )
        
        return self


# Initialize settings
settings = Settings()
