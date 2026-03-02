"""
AI MON - Smart API Monitoring & Auto Debug Tool
Main application entry point with production-ready features.
"""
import asyncio
import signal
from contextlib import asynccontextmanager
from typing import Any, Dict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from app.core.config import settings
from app.core.database import init_db, close_db, check_db_health
from app.api.router import api_router
from app.monitoring_engine.task_manager import get_task_manager
from app.utils.logger import log


# Configure loguru to use our logger
logger.configure(**{
    "handlers": [
        {
            "sink": sys.stdout,
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            "level": "DEBUG" if settings.debug else "INFO",
        }
    ]
})


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and graceful shutdown.
    """
    # Startup
    log.info("=" * 50)
    log.info("Starting AI MON application...")
    log.info(f"Environment: {'Development' if settings.debug else 'Production'}")
    log.info("=" * 50)
    
    # Initialize database
    try:
        await init_db()
        log.info("Database initialized successfully")
    except Exception as e:
        log.error(f"Failed to initialize database: {e}")
        raise
    
    # Start monitoring scheduler
    task_manager = get_task_manager()
    try:
        await task_manager.start_monitoring()
        log.info("Monitoring scheduler started")
    except Exception as e:
        log.error(f"Failed to start monitoring scheduler: {e}")
        # Don't crash - monitoring can be restarted later
    
    # Store task manager reference for graceful shutdown
    app.state.task_manager = task_manager
    
    yield
    
    # Shutdown
    log.info("=" * 50)
    log.info("Initiating graceful shutdown...")
    log.info("=" * 50)
    
    # Stop monitoring scheduler
    try:
        await task_manager.stop_monitoring()
        log.info("Monitoring scheduler stopped")
    except Exception as e:
        log.error(f"Error stopping monitoring: {e}")
    
    # Close database connections
    try:
        await close_db()
        log.info("Database connections closed")
    except Exception as e:
        log.error(f"Error closing database: {e}")
    
    log.info("Graceful shutdown complete")
    log.info("=" * 50)


# Create FastAPI application with production optimizations
app = FastAPI(
    title=settings.app_name,
    description="Smart API Monitoring & Auto Debug Tool - Real-time API monitoring with AI-powered insights",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
    default_response_class=JSONResponse,
)

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

# Include API router
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Smart API Monitoring & Auto Debug Tool",
        "docs": "/docs" if settings.debug else None,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """
    Enhanced health check endpoint.
    Returns detailed status of all system components.
    """
    # Check database
    db_healthy = await check_db_health()
    
    # Check monitoring status
    monitoring_status = "unknown"
    try:
        task_manager = get_task_manager()
        monitoring_status = "running" if task_manager.is_running else "stopped"
    except Exception:
        monitoring_status = "error"
    
    overall_healthy = db_healthy
    
    return {
        "status": "healthy" if overall_healthy else "degraded",
        "version": settings.app_version,
        "components": {
            "database": "healthy" if db_healthy else "unhealthy",
            "monitoring": monitoring_status,
        }
    }


@app.get("/health/live")
async def liveness_check():
    """Simple liveness check for container orchestration."""
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness_check():
    """Readiness check - verifies database connectivity."""
    db_healthy = await check_db_health()
    if not db_healthy:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": "database unavailable"}
        )
    return {"status": "ready"}


# Exception handlers for consistent error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions with proper error response."""
    log.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred" if settings.debug else "Please try again later",
            "path": str(request.url) if settings.debug else None,
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Production server configuration
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
        workers=1 if settings.debug else 4,
    )
