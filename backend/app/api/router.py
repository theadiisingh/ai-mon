"""
Main API router that combines all sub-routers.
"""
from fastapi import APIRouter

from app.api import auth, users, apis, monitoring, metrics

api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(apis.router, prefix="/apis", tags=["API Endpoints"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
