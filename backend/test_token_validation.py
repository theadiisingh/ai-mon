"""
Test script to verify token generation and validation work correctly.
Run this to diagnose the 401 issue.
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.core.security import create_access_token, decode_token
from app.core.config import settings
from app.models.user import User
from sqlalchemy import select
from app.core.database import AsyncSessionLocal


async def test_token_flow():
    """Test the full token flow."""
    print("=" * 60)
    print("TOKEN VALIDATION TEST")
    print("=" * 60)
    
    # 1. Check config
    print("\n1. CONFIGURATION:")
    print(f"   Secret key (first 20 chars): {settings.secret_key[:20]}...")
    print(f"   Algorithm: {settings.algorithm}")
    print(f"   Access token expire minutes: {settings.access_token_expire_minutes}")
    
    # 2. Generate a test token
    print("\n2. GENERATING TEST TOKEN:")
    test_user_id = "1"
    token_data = {"sub": test_user_id}
    test_token = create_access_token(token_data)
    print(f"   Generated token (first 50 chars): {test_token[:50]}...")
    
    # 3. Decode the token we just generated
    print("\n3. DECODING TOKEN (self):")
    payload = decode_token(test_token)
    if payload:
        print(f"   ✓ Token decoded successfully!")
        print(f"   Payload: {payload}")
    else:
        print(f"   ✗ FAILED to decode token!")
        return
    
    # 4. Try to find user in database
    print("\n4. LOOKING UP USER IN DATABASE:")
    async with AsyncSessionLocal() as db:
        from app.services.user_service import UserService
        user_service = UserService(db)
        
        try:
            user_id = int(test_user_id)
            user = await user_service.get_user_by_id(user_id)
            if user:
                print(f"   ✓ User found!")
                print(f"   User ID: {user.id}")
                print(f"   Email: {user.email}")
                print(f"   is_active: {user.is_active}")
            else:
                print(f"   ✗ User NOT found!")
        except Exception as e:
            print(f"   ✗ Error looking up user: {e}")
    
    # 5. Simulate what the backend does for protected routes
    print("\n5. SIMULATING BACKEND VALIDATION:")
    payload = decode_token(test_token)
    if payload:
        user_id = payload.get("sub")
        token_type = payload.get("type")
        print(f"   user_id from token: {user_id}")
        print(f"   token_type: {token_type}")
        
        if user_id and token_type == "access":
            print(f"   ✓ Token type is valid!")
        else:
            print(f"   ✗ Token validation failed!")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_token_flow())
