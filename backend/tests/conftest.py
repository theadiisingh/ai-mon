"""
Test fixtures and configuration for pytest.
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models.user import User
from app.models.api import ApiEndpoint, HttpMethod
from app.models.monitoring_log import MonitoringLog, CheckStatus
from app.core.security import get_password_hash


# Test database URL (use SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_inactive(db_session: AsyncSession) -> User:
    """Create an inactive test user."""
    user = User(
        email="inactive@example.com",
        username="inactiveuser",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Inactive User",
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_api_endpoint(db_session: AsyncSession, test_user: User) -> ApiEndpoint:
    """Create a test API endpoint."""
    endpoint = ApiEndpoint(
        user_id=test_user.id,
        name="Test API",
        url="https://api.example.com/health",
        method=HttpMethod.GET,
        expected_status_code=200,
        timeout_seconds=30,
        interval_seconds=60,
        is_active=True,
    )
    db_session.add(endpoint)
    await db_session.commit()
    await db_session.refresh(endpoint)
    return endpoint


@pytest_asyncio.fixture
async def test_monitoring_logs(db_session: AsyncSession, test_api_endpoint: ApiEndpoint, test_user: User):
    """Create test monitoring logs."""
    logs = []
    for i in range(10):
        log = MonitoringLog(
            api_endpoint_id=test_api_endpoint.id,
            user_id=test_user.id,
            status=CheckStatus.SUCCESS if i < 8 else CheckStatus.FAILURE,
            status_code=200 if i < 8 else 500,
            response_time=100.0 + i * 10,
            checked_at=None,  # Will use default
        )
        db_session.add(log)
        logs.append(log)
    
    await db_session.commit()
    return logs


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    mock = AsyncMock()
    mock.generate = AsyncMock(return_value={
        "summary": "Test analysis summary",
        "possible_causes": ["Cause 1", "Cause 2"],
        "suggested_steps": ["Step 1", "Step 2"],
        "confidence": 0.85,
        "severity": "medium"
    })
    mock.generate_text = AsyncMock(return_value="Test text response")
    return mock


@pytest.fixture
def mock_email_service():
    """Create a mock email service."""
    mock = AsyncMock()
    mock.send_email = AsyncMock(return_value=True)
    mock.send_api_down_notification = AsyncMock(return_value=True)
    mock.send_api_recovered_notification = AsyncMock(return_value=True)
    mock.send_anomaly_detected_notification = AsyncMock(return_value=True)
    mock.send_welcome_email = AsyncMock(return_value=True)
    return mock
