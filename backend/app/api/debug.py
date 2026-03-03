"""
Debug routes for troubleshooting authentication issues.
"""
from fastapi import APIRouter, Request, Depends
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/debug/me")
async def debug_current_user(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Debug endpoint that returns user info if token is valid."""
    from app.utils.logger import log
    log.info(f"[DEBUG] User authenticated: {current_user.id} - {current_user.email}")
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "message": "Token is valid!"
    }


@router.get("/debug/token-info")
async def debug_token_info(request: Request):
    """Debug endpoint to see what's being sent."""
    from app.utils.logger import log
    
    auth_header = request.headers.get("Authorization", "NOT FOUND")
    log.info(f"[DEBUG] Authorization header: {auth_header}")
    
    return {
        "authorization_header": auth_header,
        "path": request.url.path,
    }
