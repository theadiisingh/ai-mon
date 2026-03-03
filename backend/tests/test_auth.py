"""
Unit tests for authentication functionality.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token, decode_token


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_get_password_hash(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False


class TestTokenGeneration:
    """Test JWT token generation and decoding."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_token_valid(self):
        """Test decoding a valid token."""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        payload = decode_token(token)
        
        assert payload is not None
        assert payload.get("sub") == "123"
        assert payload.get("type") == "access"
    
    def test_decode_token_invalid(self):
        """Test decoding an invalid token."""
        payload = decode_token("invalid_token")
        
        assert payload is None
    
    def test_decode_token_tampered(self):
        """Test decoding a tampered token."""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        # Tamper with the token
        tampered_token = token[:-5] + "xxxxx"
        
        payload = decode_token(tampered_token)
        
        assert payload is None


class TestAuthenticationAPI:
    """Test authentication API endpoints."""
    
    @pytest.mark.asyncio
    async def test_register_new_user(self, client: AsyncClient):
        """Test registering a new user."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "password123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        # Response has user nested inside 'user' key plus tokens at top level
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["username"] == "newuser"
        assert "access_token" in data
        assert "refresh_token" in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Test registering with duplicate email."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,  # Already exists
                "username": "anotheruser",
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test successful login."""
        response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, test_user: User):
        """Test login with invalid password."""
        response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user."""
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_inactive_user(self, client: AsyncClient, test_user_inactive: User):
        """Test login with inactive user."""
        response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user_inactive.email,
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient, test_user: User):
        """Test token refresh."""
        # First login to get a token
        login_response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        
        # Use the token to get current user
        token = login_response.json()["access_token"]
        
        # Get current user info
        me_response = await client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert me_response.status_code == 200
        assert me_response.json()["email"] == test_user.email
