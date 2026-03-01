"""
AI MON - Smart API Monitoring & Auto Debug Tool
Main application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.router import api_router
from app.monitoring_engine.task_manager import get_task_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting AI MON application...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Start monitoring scheduler
    task_manager = get_task_manager()
    await task_manager.start_monitoring()
    logger.info("Monitoring scheduler started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI MON application...")
    
    # Stop monitoring scheduler
    await task_manager.stop_monitoring()
    logger.info("Monitoring scheduler stopped")
    
    # Close database connections
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="AI MON - Smart API Monitoring",
    description="Real-time API monitoring with AI-powered debugging insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI MON - Smart API Monitoring",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
