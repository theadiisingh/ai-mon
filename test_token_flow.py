"""
Test script to verify token generation and validation works correctly.
Run this to check if the JWT token flow is working without the frontend.
"""
import asyncio
import sys
sys.path.insert(0, 'backend')

from app.core.security import create_access_token, decode_token
from app.core.config import settings
from datetime import timedelta


def test_token_creation_and_validation():
    """Test that tokens can be created and validated correctly."""
    print("=" * 60)
    print("Testing JWT Token Flow")
    print("=" * 60)
    
    # Test settings
    print(f"\n[CONFIG]")
    print(f"  Secret Key: {settings.secret_key[:20]}...")
    print(f"  Algorithm: {settings.algorithm}")
    print(f"  Access Token Expire: {settings.access_token_expire_minutes} minutes")
    
    # Create a test token with user_id = 1
    test_user_id = "1"
    
    print(f"\n[CREATE TOKEN]")
    print(f"  Creating access token for user_id: {test_user_id}")
    
    access_token = create_access_token(
        data={"sub": test_user_id},
        expires_delta=timedelta(minutes=30)
    )
    
    print(f"  Access Token: {access_token[:50]}...")
    
    # Decode the token
    print(f"\n[DECODE TOKEN]")
    payload = decode_token(access_token)
    
    if payload:
        print(f"  ✓ Token decoded successfully!")
        print(f"  Payload: {payload}")
        
        # Verify claims
        print(f"\n[VERIFY CLAIMS]")
        print(f"  sub (user_id): {payload.get('sub')}")
        print(f"  type: {payload.get('type')}")
        print(f"  exp: {payload.get('exp')}")
        print(f"  iat: {payload.get('iat')}")
        
        # Check token type
        if payload.get('type') == 'access':
            print(f"  ✓ Token type is 'access'")
        else:
            print(f"  ✗ ERROR: Token type is '{payload.get('type')}' (expected 'access')")
        
        # Check user_id
        if payload.get('sub') == test_user_id:
            print(f"  ✓ User ID matches: {payload.get('sub')}")
        else:
            print(f"  ✗ ERROR: User ID mismatch")
    else:
        print(f"  ✗ FAILED to decode token!")
        return False
    
    print("\n" + "=" * 60)
    print("Token flow test PASSED!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_token_creation_and_validation()
    sys.exit(0 if success else 1)
