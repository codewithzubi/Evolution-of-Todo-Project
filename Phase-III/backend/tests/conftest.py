# [Task]: T017-T018, [From]: specs/001-task-crud-api/spec.md#Test-Infrastructure
# [From]: specs/001-task-crud-api/plan.md#Phase-3-User-Story-1
"""
Pytest configuration and shared fixtures for task CRUD API tests.

Provides:
- Database session fixtures
- FastAPI TestClient
- Authentication tokens
- Test user and task fixtures
"""

import asyncio
import os
import sys
import tempfile
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import pytest_asyncio

# CRITICAL: Set environment variables BEFORE importing any backend modules
os.environ["JWT_SECRET"] = "test_secret_key"
os.environ["BETTER_AUTH_SECRET"] = "test_secret"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.config import settings
from src.main import app
from src.database import engine


def pytest_configure(config):
    """Configure pytest to run async tests properly."""
    config.option.asyncio_mode = "auto"


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_database():
    """Create and cleanup test database tables for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # Cleanup after each test
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture(scope="function")
def client():
    """Create a FastAPI TestClient."""
    # [Task]: T017-T018, [From]: specs/001-task-crud-api/spec.md#Test-Infrastructure
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture(scope="function")
async def test_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session using the global engine."""
    async_session_factory = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_factory() as session:
        yield session


@pytest.fixture
def test_user_id() -> UUID:
    """Generate a test user ID."""
    return uuid4()


@pytest.fixture
def test_jwt_token(test_user_id: UUID) -> str:
    """Generate a valid test JWT token."""
    payload = {
        "user_id": str(test_user_id),
        "email": "test@example.com",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return token


@pytest.fixture
def auth_headers(test_jwt_token: str) -> dict:
    """Generate authorization headers with JWT token."""
    return {"Authorization": f"Bearer {test_jwt_token}"}


@pytest.fixture
def other_user_id() -> UUID:
    """Generate a different test user ID for isolation testing."""
    return uuid4()


@pytest.fixture
def other_user_jwt_token(other_user_id: UUID) -> str:
    """Generate a JWT token for a different user."""
    payload = {
        "user_id": str(other_user_id),
        "email": "other@example.com",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return token


@pytest.fixture
def other_user_auth_headers(other_user_jwt_token: str) -> dict:
    """Generate authorization headers for different user."""
    return {"Authorization": f"Bearer {other_user_jwt_token}"}


@pytest.fixture
def mismatched_auth_headers(other_user_jwt_token: str) -> dict:
    """Generate authorization headers with mismatched user ID (for 403 tests)."""
    return {"Authorization": f"Bearer {other_user_jwt_token}"}


@pytest.fixture
def invalid_auth_headers() -> dict:
    """Generate authorization headers with invalid JWT token."""
    return {"Authorization": "Bearer invalid.jwt.token"}


# ============================================================================
# Phase-III Chatbot Test Fixtures (T300-T306)
# ============================================================================


@pytest_asyncio.fixture
async def test_user(test_session: AsyncSession, test_user_id: UUID):
    """Create a test user in database.

    [Task]: T366, [From]: specs/004-ai-chatbot/plan.md#Phase-1
    Ensures user exists for foreign key constraints.
    """
    from src.models.base import User

    user = User(
        id=test_user_id,
        email="test@example.com",
        name="Test User",
        password_hash="hashed_password",
        email_verified=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def other_user(test_session: AsyncSession, other_user_id: UUID):
    """Create another test user in database for isolation testing.

    [Task]: T366, T370, [From]: specs/004-ai-chatbot/plan.md#Phase-1
    """
    from src.models.base import User

    user = User(
        id=other_user_id,
        email="other@example.com",
        name="Other User",
        password_hash="hashed_password",
        email_verified=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def conversation_factory(test_session: AsyncSession):
    """Factory for creating test conversations.

    [Task]: T305, [From]: specs/004-ai-chatbot/plan.md#Phase-1
    """
    from tests.fixtures.test_conversations import ConversationFactory

    return ConversationFactory(session=test_session)


@pytest_asyncio.fixture
async def message_factory(test_session: AsyncSession):
    """Factory for creating test messages.

    [Task]: T305, [From]: specs/004-ai-chatbot/plan.md#Phase-1
    """
    from tests.fixtures.test_conversations import MessageFactory

    return MessageFactory(session=test_session)


@pytest_asyncio.fixture
async def sample_conversation(test_session: AsyncSession, test_user):
    """Create a sample active conversation for testing.

    [Task]: T305, [From]: specs/004-ai-chatbot/plan.md#Phase-1
    """
    from tests.fixtures.test_conversations import ConversationFactory

    factory = ConversationFactory()
    conversation = factory.create(user_id=test_user.id, title="Test Conversation")
    test_session.add(conversation)
    await test_session.commit()
    await test_session.refresh(conversation)
    return conversation


@pytest_asyncio.fixture
async def sample_message(test_session: AsyncSession, test_user, sample_conversation):
    """Create a sample message in a conversation for testing.

    [Task]: T305, [From]: specs/004-ai-chatbot/plan.md#Phase-1
    """
    from tests.fixtures.test_conversations import MessageFactory
    from src.models.message import MessageRole

    factory = MessageFactory()
    message = factory.create(
        conversation_id=sample_conversation.id,
        user_id=test_user.id,
        role=MessageRole.USER,
        content="Hello, can you help me?",
    )
    test_session.add(message)
    await test_session.commit()
    await test_session.refresh(message)
    return message


@pytest_asyncio.fixture
async def user_a_conversation(test_session: AsyncSession, test_user):
    """Create a conversation for User A.

    [Task]: T303, T305, [From]: specs/004-ai-chatbot/spec.md#FR-017
    """
    from tests.fixtures.test_conversations import ConversationFactory

    factory = ConversationFactory()
    conversation = factory.create(user_id=test_user.id, title="User A's Conversation")
    test_session.add(conversation)
    await test_session.commit()
    await test_session.refresh(conversation)
    return conversation


@pytest_asyncio.fixture
async def user_b_conversation(test_session: AsyncSession, other_user):
    """Create a conversation for User B (different user for isolation testing).

    [Task]: T303, T305, [From]: specs/004-ai-chatbot/spec.md#FR-018, FR-019
    """
    from tests.fixtures.test_conversations import ConversationFactory

    factory = ConversationFactory()
    conversation = factory.create(user_id=other_user.id, title="User B's Conversation")
    test_session.add(conversation)
    await test_session.commit()
    await test_session.refresh(conversation)
    return conversation
