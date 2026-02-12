"""Pytest configuration and fixtures for backend testing.

This module provides:
- Test database setup with SQLModel
- Database session fixtures
- Test client fixtures for FastAPI
- User authentication fixtures
"""

import os

# Set test environment variables BEFORE any imports
os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-minimum-32-characters-long-for-testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["FRONTEND_URL"] = "http://localhost:3000"

import pytest
from typing import Generator
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User
from app.services.password_service import hash_password
from app.services.jwt_service import create_token
from app.config import get_settings
from app.api.deps import get_session


# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(name="engine")
def engine_fixture():
    """Create a test database engine with in-memory SQLite."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """Create a test client for FastAPI with database session override."""

    def get_session_override():
        return session

    # Override the database session dependency
    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> User:
    """Create a test user in the database."""
    user = User(
        email="test@example.com",
        hashed_password=hash_password("password123"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_user_token")
def test_user_token_fixture(test_user: User) -> str:
    """Generate a JWT token for the test user."""
    settings = get_settings()
    return create_token(
        user_id=test_user.id,
        email=test_user.email,
        secret_key=settings.BETTER_AUTH_SECRET,
    )


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_user_token: str) -> dict:
    """Create authorization headers with JWT token."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture(name="second_user")
def second_user_fixture(session: Session) -> User:
    """Create a second test user for multi-user testing."""
    user = User(
        email="user2@example.com",
        hashed_password=hash_password("password456"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="second_user_token")
def second_user_token_fixture(second_user: User) -> str:
    """Generate a JWT token for the second test user."""
    settings = get_settings()
    return create_token(
        user_id=second_user.id,
        email=second_user.email,
        secret_key=settings.BETTER_AUTH_SECRET,
    )


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
