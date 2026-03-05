"""
Database configuration and session management with connection pooling.
"""
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.core.config import settings
from app.utils.logger import log


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Import all models to ensure they are registered
from app.models.user import User
from app.models.api import ApiEndpoint
from app.models.monitoring_log import MonitoringLog
from app.models.ai_insight import AIInsight


def _get_engine_kwargs() -> dict:
    """Get engine configuration based on database type."""
    kwargs = {
        "echo": settings.debug,
        "pool_pre_ping": True,  # Verify connections before use
    }
    
    # Configure pool settings for production
    if not settings.debug:
        kwargs["poolclass"] = AsyncAdaptedQueuePool
        kwargs["pool_size"] = 20
        kwargs["max_overflow"] = 30
        kwargs["pool_recycle"] = 3600  # Recycle connections after 1 hour
        kwargs["pool_timeout"] = 30
    else:
        # Use NullPool for development (easier for debugging)
        kwargs["poolclass"] = NullPool
    
    return kwargs


# Create async engine - handle different database types
database_url = settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
elif database_url.startswith("sqlite"):
    # SQLite-specific configuration
    kwargs = _get_engine_kwargs()
    kwargs.pop("poolclass", None)
    kwargs.pop("pool_size", None)
    kwargs.pop("max_overflow", None)
    kwargs.pop("pool_recycle", None)
    kwargs.pop("pool_timeout", None)
    kwargs.pop("pool_pre_ping", None)
    
    # Add SQLite-specific options
    engine = create_async_engine(
        database_url,
        **kwargs,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_async_engine(
        database_url,
        **_get_engine_kwargs()
    )

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    Uses async context manager for proper cleanup.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Initialize database tables."""
    log.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Run migrations for existing databases - add missing columns
    await run_migrations()
    
    log.info("Database tables initialized successfully")


async def run_migrations():
    """Run database migrations to add missing columns to existing tables."""
    from sqlalchemy import inspect
    
    async with engine.begin() as conn:
        await conn.run_sync(_run_sync_migrations)


def _run_sync_migrations(conn):
    """Synchronous migration helper."""
    from sqlalchemy import text
    
    # Check if status column exists in api_endpoints using raw SQL
    result = conn.execute(text("PRAGMA table_info(api_endpoints)"))
    columns = result.fetchall()
    column_names = [col[1] for col in columns]
    
    if 'status' not in column_names:
        log.info("Adding 'status' column to api_endpoints table...")
        conn.execute(text(
            "ALTER TABLE api_endpoints ADD COLUMN status VARCHAR(10)"
        ))
        log.info("'status' column added successfully")
    
    log.info("Database migrations completed")


async def close_db():
    """Close database connections gracefully."""
    log.info("Closing database connections...")
    await engine.dispose()
    log.info("Database connections closed")


async def check_db_health() -> bool:
    """Check database health by executing a simple query."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        log.error(f"Database health check failed: {e}")
        return False


@asynccontextmanager
async def get_db_context():
    """
    Context manager for database sessions.
    Use this for background tasks or when not using dependency injection.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
