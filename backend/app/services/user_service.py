"""
User service for user management operations.
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserService:
    """Service for user-related operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username.lower())
        )
        return result.scalar_one_or_none()
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if email already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if username already exists
        existing_username = await self.get_user_by_username(user_data.username)
        if existing_username:
            raise ValueError("Username already taken")
        
        # Create new user
        db_user = User(
            email=user_data.email.lower(),
            username=user_data.username.lower(),
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
        )
        
        self.db.add(db_user)
        await self.db.flush()
        await self.db.refresh(db_user)
        
        return db_user
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update fields if provided
        if user_data.email is not None:
            # Check if new email is already taken
            existing = await self.get_user_by_email(user_data.email)
            if existing and existing.id != user_id:
                raise ValueError("Email already in use")
            user.email = user_data.email.lower()
        
        if user_data.username is not None:
            # Check if new username is already taken
            existing = await self.get_user_by_username(user_data.username)
            if existing and existing.id != user_id:
                raise ValueError("Username already taken")
            user.username = user_data.username.lower()
        
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.password is not None:
            user.hashed_password = get_password_hash(user_data.password)
        
        await self.db.flush()
        await self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.flush()
        
        return True
    
    async def list_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """List users with pagination."""
        query = select(User)
        
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_users(self, is_active: Optional[bool] = None) -> int:
        """Count total users."""
        query = select(User)
        
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        result = await self.db.execute(query)
        return len(result.scalars().all())
    
    async def activate_user(self, user_id: int) -> Optional[User]:
        """Activate a user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.is_active = True
        await self.db.flush()
        await self.db.refresh(user)
        
        return user
    
    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate a user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.is_active = False
        await self.db.flush()
        await self.db.refresh(user)
        
        return user
