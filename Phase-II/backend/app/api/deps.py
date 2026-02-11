"""Dependency injection for API routes."""
from typing import Generator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, create_engine

from app.config import get_settings
from app.services.jwt_service import extract_user_id

# Security scheme for JWT Bearer token
security = HTTPBearer()

# Database engine (created once)
settings = get_settings()
engine = create_engine(settings.DATABASE_URL, echo=True)


def get_session() -> Generator[Session, None, None]:
    """
    Get database session for dependency injection.

    Yields:
        SQLModel Session for database operations
    """
    with Session(engine) as session:
        yield session


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """
    Extract and validate user_id from JWT token.

    This dependency:
    1. Extracts the JWT token from Authorization header
    2. Verifies the token signature using BETTER_AUTH_SECRET
    3. Extracts user_id from the token payload
    4. Returns user_id for use in route handlers

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        User UUID extracted from valid JWT token

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    settings = get_settings()
    token = credentials.credentials

    user_id = extract_user_id(token, settings.BETTER_AUTH_SECRET)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id
