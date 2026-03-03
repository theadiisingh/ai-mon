"""
FastAPI dependencies for authentication and database.
"""
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.services.user_service import UserService
from app.utils.logger import log

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    log.info(f"[AUTH_DEP] get_current_user called")
    log.info(f"[AUTH_DEP] Raw token: {token[:50] if token else 'None'}...")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        log.warning("[AUTH_DEP] No token provided")
        raise credentials_exception
    
    payload = decode_token(token)
    if payload is None:
        log.warning("[AUTH_DEP] Failed to decode token")
        raise credentials_exception
    
    log.info(f"[AUTH_DEP] Token payload: {payload}")
    
    user_id: str = payload.get("sub")
    token_type: str = payload.get("type")
    
    log.info(f"[AUTH_DEP] user_id: {user_id}, token_type: {token_type}")
    
    if user_id is None:
        log.warning("[AUTH_DEP] No user_id in token")
        raise credentials_exception
    
    if token_type != "access":
        log.warning(f"[AUTH_DEP] Invalid token type: {token_type} (expected: access)")
        raise credentials_exception
    
    try:
        user_id_int = int(user_id)
        log.info(f"[AUTH_DEP] Looking up user with id: {user_id_int}")
    except ValueError:
        log.warning(f"[AUTH_DEP] Invalid user_id format: {user_id}")
        raise credentials_exception
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id_int)
    
    if user is None:
        log.warning(f"[AUTH_DEP] User not found for user_id: {user_id}")
        raise credentials_exception
    
    # Refresh user from database to ensure it's loaded in current session
    await db.refresh(user)
    
    log.info(f"[AUTH_DEP] User authenticated: {user.id} - {user.email} - is_active: {user.is_active}")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        log.warning(f"[AUTH] User {current_user.id} is inactive")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    log.info(f"[AUTH] Active user: {current_user.id} - {current_user.email}")
    return current_user


class PaginationParams:
    """Pagination parameters for list endpoints."""
    
    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100
    ):
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page must be >= 1"
            )
        if page_size < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page size must be >= 1"
            )
        if page_size > max_page_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Page size must be <= {max_page_size}"
            )
        
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size


def get_pagination_params(
    pagination: PaginationParams = Depends()
) -> PaginationParams:
    """Get pagination parameters."""
    return pagination
