"""
AI MON - Smart API Monitoring & Auto Debug Tool
Main application entry point with production-ready features.
"""
import asyncio
import signal
from contextlib import asynccontextmanager
from typing import Any, Dict
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from loguru import logger
import os

from app.core.config import settings
from app.core.database import init_db, close_db, check_db_health
from app.api.router import api_router
from app.monitoring_engine.task_manager import get_task_manager
from app.utils.logger import log
from app.core.websocket import get_websocket_manager


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

# Add CSP middleware with environment-aware configuration
# This should be added AFTER CORS but BEFORE routes
from app.middleware.csp import CSPMiddleware
app.add_middleware(CSPMiddleware)

# Middleware to log ALL incoming requests
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    log.info(f"[REQUEST] {request.method} {request.url.path}")
    response = await call_next(request)
    log.info(f"[RESPONSE] {request.method} {request.url.path} - Status: {response.status_code}")
    return response

# Include API router
app.include_router(api_router, prefix="/api")


# =============================================================================
# WEBSOCKET ENDPOINT - Real-time monitoring updates
# =============================================================================
# WebSocket endpoint for real-time monitoring updates
# Clients connect to receive instant notifications when health checks complete

@app.websocket("/ws/monitor-updates")
async def websocket_monitor_updates(websocket: WebSocket):
    """
    WebSocket endpoint for real-time monitoring updates.
    
    Clients connect to receive instant notifications when:
    - A health check completes
    - An endpoint status changes
    - New metrics are available
    
    The frontend listens for these events and triggers a refetch
    of the relevant data from the backend APIs.
    """
    # Accept the WebSocket connection
    await websocket.accept()
    
    # Get the WebSocket manager
    ws_manager = get_websocket_manager()
    
    # Register this connection
    await ws_manager.connect(websocket)
    
    try:
        # Keep the connection alive and handle incoming messages
        while True:
            # Wait for any message from the client (ping/heartbeat)
            # This helps detect disconnected clients
            data = await websocket.receive_text()
            
            # Handle client messages if needed
            # For now, we just keep the connection alive
            logger.debug(f"WebSocket received: {data}")
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Clean up the connection
        await ws_manager.disconnect(websocket)


# =============================================================================
# FRONTEND PATH SETUP - Define early so it's available for all routes
# =============================================================================
from pathlib import Path
from fastapi.staticfiles import StaticFiles

# Use Path for SAFE absolute path resolution
BASE_DIR = Path(__file__).resolve().parent.parent.parent
frontend_dist_path = BASE_DIR / "frontend" / "dist"


def get_frontend_index():
    """Helper to serve frontend index.html."""
    index_path = frontend_dist_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return None


@app.get("/")
async def root():
    """Root endpoint - serves frontend SPA for browser requests."""
    frontend_response = get_frontend_index()
    if frontend_response:
        return frontend_response
    
    # Fallback to API info if frontend not built
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Smart API Monitoring & Auto Debug Tool",
        "docs": "/docs" if settings.debug else None,
        "status": "operational",
        "message": "Frontend not found. Build with: cd frontend && npm run build"
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


# =============================================================================
# STATIC FILES - Serve frontend SPA with proper SPA fallback
# =============================================================================
# IMPORTANT: Order matters here! API routes are registered first (prefix="/api"),
# then we handle static files, then we add a catch-all for SPA routes.
# =============================================================================

from fastapi.staticfiles import StaticFiles

# Verify frontend dist exists
if frontend_dist_path.exists():
    # Mount static files for actual assets (JS, CSS, images, etc.)
    # This handles /assets/* paths correctly
    app.mount("/assets", StaticFiles(directory=str(frontend_dist_path / "assets")), name="assets")
    log.info(f"Frontend static files mounted from: {frontend_dist_path}")
else:
    log.warning(f"Frontend dist folder not found at: {frontend_dist_path}")


# =============================================================================
# SPA FALLBACK ROUTE - Must be LAST to catch all remaining routes
# =============================================================================
# This route serves index.html for any frontend route that isn't an API call
# or static file. This enables client-side routing to work on refresh.
# =============================================================================
# IMPORTANT: Use @app.get() directly on FastAPI app, NOT APIRouter!
# This ensures proper route ordering and avoids conflicts.

@app.get("/{path:path}")
async def serve_spa_fallback(path: str):
    """
    Catch-all route for SPA routing.
    
    This route ONLY handles paths that haven't been matched by:
    - /api/* routes (handled by api_router with prefix="/api")
    - /health/* routes
    - /docs, /redoc, /openapi.json
    - /assets/* (static files)
    - / (root - served by dedicated root route above)
    
    For all other frontend routes (like /apis/1, /dashboard), 
    we serve index.html so React can handle the routing.
    """
    # List of path prefixes that should NOT be handled by SPA fallback
    # These are handled by their specific routes above
    # IMPORTANT: Use "/" suffix to avoid matching "apis" when we mean "/api"
    protected_prefixes = [
        "api/",         # API endpoints - must have / after "api"
        "docs/",        # Swagger docs
        "redoc/",       # ReDoc docs  
        "openapi.json", # OpenAPI schema
        "health/",      # Health check endpoints
        "assets/",      # Static assets
    ]
    
    # Also check for exact matches (like /api without trailing slash)
    exact_matches = ["api", "docs", "redoc", "openapi.json", "health", "assets"]
    
    # Check if the path starts with any protected prefix
    for prefix in protected_prefixes:
        if path.startswith(prefix):
            return JSONResponse(
                status_code=404,
                content={"detail": "Not Found"}
            )
    
    # Check exact matches
    if path in exact_matches:
        return JSONResponse(
            status_code=404,
            content={"detail": "Not Found"}
        )
    
    # Check if the path looks like a file (has extension)
    # If it does, it's likely a static file request that doesn't exist
    path_parts = path.split("/")
    if len(path_parts) > 0 and "." in path_parts[-1]:
        # File with extension but not matched - 404
        return JSONResponse(
            status_code=404,
            content={"detail": "File not found"}
        )
    
    # For all other paths (SPA routes), serve index.html
    index_path = frontend_dist_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    
    # Fallback if index.html doesn't exist
    return JSONResponse(
        status_code=404,
        content={"detail": "Frontend not found. Please build the frontend."}
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
