"""
Security module for JWT token handling and password hashing with production-ready features.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt, ExpiredSignatureError
import bcrypt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.utils.logger import log

# OAuth2 scheme with token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        log.error(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with proper claims."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token with rotation support."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token with proper error handling."""
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        return payload
    except ExpiredSignatureError:
        log.warning("[SECURITY] Token has expired")
        return None
    except JWTError as e:
        log.warning(f"[SECURITY] JWT decode error: {type(e).__name__}")
        return None
    except Exception as e:
        log.error(f"[SECURITY] Unexpected error decoding token: {type(e).__name__}")
        return None


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Get the current authenticated user from JWT token with proper error handling."""
    from app.models.user import User
    from app.services.user_service import UserService
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if token exists
    if not token:
        raise credentials_exception
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    # Validate token type
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_id(int(user_id))
    except ValueError:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(current_user = Depends(get_current_user)):
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional:
    """Get current user if authenticated, otherwise return None."""
    if not token:
        return None
    
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        return None
    
    user_id = payload.get("sub")
    if user_id is None:
        return None
    
    from app.services.user_service import UserService
    user_service = UserService(db)
    
    try:
        user = await user_service.get_user_by_id(int(user_id))
        if user and user.is_active:
            return user
    except ValueError:
        pass
    
    return None


def validate_password_strength(password: str) -> bool:
    """
    Validate password meets security requirements.
    - At least 8 characters
    - Contains uppercase and lowercase
    - Contains digit
    """
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True


async def get_current_user_optional(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user if authenticated, but require authentication in production.
    
    In development mode:
        - If token is provided, validates and returns the user
        - If no token is provided, returns None (for dashboard views)
    
    In production mode:
        - Requires valid authentication
        - Returns 401 if no valid token
    
    This allows internal dashboard metrics to work in development without auth,
    while maintaining security in production.
    """
    from app.models.user import User
    from app.services.user_service import UserService
    
    # If no token provided
    if not token:
        # In development mode, allow unauthenticated access (return None)
        # In production mode, require authentication
        if settings.is_development:
            log.info("[DEV] No token provided, allowing unauthenticated access in development mode")
            return None
        else:
            # Production requires authentication
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            raise credentials_exception
    
    # Token provided - validate it
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        # Invalid token
        if settings.is_development:
            log.info("[DEV] Invalid token provided, but allowing access in development mode")
            return None
        else:
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        if settings.is_development:
            return None
        else:
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            raise credentials_exception
    
    from app.services.user_service import UserService
    user_service = UserService(db)
    
    try:
        user = await user_service.get_user_by_id(int(user_id))
        if user and user.is_active:
            return user
    except ValueError:
        pass
    
    if settings.is_development:
        return None
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    raise credentials_exception
