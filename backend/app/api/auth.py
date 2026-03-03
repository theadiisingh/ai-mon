"""
Authentication API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.config import settings
from app.schemas.auth_schema import LoginRequest
from app.schemas.user_schema import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from loguru import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

router = APIRouter()


async def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user."""
    from app.core.security import decode_token
    from app.services.user_service import UserService
    
    logger.info(f"[AUTH] get_current_active_user called with token: {token[:50] if token else 'None'}...")
    
    # Decode token
    payload = decode_token(token)
    
    if not payload:
        logger.warning("[AUTH] Failed to decode token in auth.py")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"[AUTH] Token payload: {payload}")
    
    # Get user ID from payload
    user_id = payload.get("sub")
    
    if not user_id:
        logger.warning("[AUTH] No user_id in token payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"[AUTH] Looking up user_id: {user_id}")
    
    # Get user from database
    user_service = UserService(db)
    user = await user_service.get_user_by_id(int(user_id))
    
    if not user:
        logger.warning(f"[AUTH] User not found for user_id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        logger.warning(f"[AUTH] User {user_id} is inactive")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    logger.info(f"[AUTH] User authenticated: {user.id} - {user.email}")
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user and return tokens for immediate login."""
    from app.services.user_service import UserService
    from app.core.security import create_access_token, create_refresh_token
    
    user_service = UserService(db)
    auth_service = AuthService(db)
    
    # Create new user
    try:
        user = await user_service.create_user(user_data)
    except ValueError:
        logger.warning(f"Registration failed: User already exists - {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    logger.info(f"New user registered: {user.id} - {user.email}")
    
    # Generate tokens for immediate login
    token = await auth_service._generate_tokens(user)
    
    # Send welcome email (don't fail if email not configured)
    email_service = EmailService()
    try:
        await email_service.send_welcome_email(user.email, user.username)
    except Exception as e:
        logger.warning(f"Failed to send welcome email: {e}")
    
    # Return both user and tokens
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        },
        "access_token": token.access_token,
        "refresh_token": token.refresh_token,
        "token_type": token.token_type
    }


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token."""
    auth_service = AuthService(db)
    
    # Create login request from form data
    login_data = LoginRequest(
        email=form_data.username,  # OAuth2 form uses username field for email
        password=form_data.password
    )
    
    # Authenticate user
    token = await auth_service.login(login_data)
    
    if not token:
        logger.warning(f"Login failed for email: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"User logged in: {login_data.email}")
    return {
        "access_token": token.access_token,
        "refresh_token": token.refresh_token,
        "token_type": token.token_type
    }


@router.post("/debug-token")
async def debug_token(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Debug endpoint to inspect token validation - FOR DEVELOPMENT ONLY."""
    from app.core.security import decode_token
    from app.services.user_service import UserService
    
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return {"error": "No Bearer token provided"}
    
    token = auth_header[7:]
    
    # Decode the token
    payload = decode_token(token)
    
    if not payload:
        return {
            "error": "Token decode failed",
            "possible_causes": [
                "Token expired",
                "Invalid signature",
                "Wrong secret key"
            ]
        }
    
    # Get user ID
    user_id = payload.get("sub")
    token_type = payload.get("type")
    
    # Try to get user
    user = None
    user_error = None
    if user_id:
        try:
            user_service = UserService(db)
            user = await user_service.get_user_by_id(int(user_id))
        except Exception as e:
            user_error = str(e)
    
    return {
        "token_payload": payload,
        "token_type": token_type,
        "user_id": user_id,
        "user_found": user is not None,
        "user_error": user_error,
        "user_active": user.is_active if user else None,
        "config": {
            "secret_key_first_chars": settings.secret_key[:20] + "...",
            "algorithm": settings.algorithm,
        }
    }


@router.post("/refresh")
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token.
    
    Accepts refresh token in two ways:
    1. Form field: 'refresh_token'
    2. Authorization header: Bearer <token>
    """
    from app.core.security import decode_token
    from app.services.user_service import UserService
    
    # Try to get token from form data first
    token = None
    
    # Check form data
    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type:
        try:
            body = await request.form()
            token = body.get("refresh_token")
        except Exception:
            pass
    
    # Fall back to Authorization header if not in form
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decode the refresh token
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate token type is refresh
    token_type = payload.get("type")
    if token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Expected refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user ID from payload
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_service = UserService(db)
    user = await user_service.get_user_by_id(int(user_id))
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    auth_service = AuthService(db)
    token = await auth_service._generate_tokens(user)
    
    return {
        "access_token": token.access_token,
        "refresh_token": token.refresh_token,
        "token_type": token.token_type
    }
