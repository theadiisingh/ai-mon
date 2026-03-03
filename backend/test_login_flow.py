import sys
sys.path.insert(0, '.')

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.services.auth_service import AuthService
from app.schemas.auth_schema import LoginRequest

async def test_login():
    # Create async engine
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        auth_service = AuthService(session)
        
        # Test login
        login_data = LoginRequest(email="test@example.com", password="TestPass123")
        result = await auth_service.login(login_data)
        
        if result:
            print(f"Login successful!")
            print(f"Access token: {result.access_token[:50]}...")
            print(f"Refresh token: {result.refresh_token[:50]}...")
            print(f"Token type: {result.token_type}")
        else:
            print("Login failed!")

asyncio.run(test_login())
