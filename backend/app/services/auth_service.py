"""
Authentication service for login, registration, and token management.
"""
from typing import Optional
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession

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
        # Get user by email
        user = await self.user_service.get_user_by_email(login_data.email)
        
        if not user:
            return None
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            return None
        
        # Check if user is active
        if not user.is_active:
            return None
        
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
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        # Create refresh token
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
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
