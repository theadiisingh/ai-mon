"""
Authentication service for login, registration, and token management.
"""
from typing import Optional
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.user import User
from app.schemas.auth_schema import LoginRequest, RegisterRequest
from app.schemas.user_schema import Token
from app.services.user_service import UserService
from app.core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token,
    decode_token
)
from app.core.config import settings


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)
    
    async def login(self, login_data: LoginRequest) -> Optional[Token]:
        """Authenticate user and generate tokens."""
        # Get user by email (lowercase for case-insensitive lookup)
        email_lower = login_data.email.lower()
        user = await self.user_service.get_user_by_email(email_lower)
        
        if not user:
            logger.warning(f"Login failed: User not found for email: {email_lower}")
            return None
        
        logger.info(f"User found: {user.id}, {user.email}, is_active={user.is_active}")
        logger.info(f"Hashed password in DB: {user.hashed_password[:50]}...")
        
        # Verify password
        password_verified = verify_password(login_data.password, user.hashed_password)
        logger.info(f"Password verification result: {password_verified}")
        
        if not password_verified:
            logger.warning(f"Login failed: Password verification failed for email: {email_lower}")
            return None
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login failed: User is inactive: {email_lower}")
            return None
        
        logger.info(f"Login successful for user: {user.id}")
        # Generate tokens
        return await self._generate_tokens(user)
    
    async def register(self, register_data: RegisterRequest) -> Optional[Token]:
        """Register a new user and generate tokens."""
        try:
            # Create new user
            user = await self.user_service.create_user(register_data)
            
            # Generate tokens
            return await self._generate_tokens(user)
        except ValueError:
            # Email or username already exists
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[Token]:
        """Refresh access token using refresh token."""
        # Decode refresh token
        payload = decode_token(refresh_token)
        
        if not payload:
            return None
        
        # Check token type
        if payload.get("type") != "refresh":
            return None
        
        # Get user ID from payload
        user_id = payload.get("sub")
        
        if not user_id:
            return None
        
        # Get user
        user = await self.user_service.get_user_by_id(int(user_id))
        
        if not user or not user.is_active:
            return None
        
        # Generate new tokens
        return await self._generate_tokens(user)
    
    async def _generate_tokens(self, user: User) -> Token:
        """Generate access and refresh tokens for a user."""
        logger.info(f"[AUTH_SERVICE] Generating tokens for user_id: {user.id}")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        logger.info(f"[AUTH_SERVICE] Access token created: {access_token[:50]}...")
        
        # Create refresh token
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        logger.info(f"[AUTH_SERVICE] Refresh token created: {refresh_token[:50]}...")
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    async def validate_user_credentials(
        self, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """Validate user credentials and return user if valid."""
        user = await self.user_service.get_user_by_email(email.lower())
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
