# [Task]: T009, [From]: specs/001-task-crud-api/spec.md#Requirements
# [From]: specs/001-task-crud-api/plan.md#Phase-2-Foundational
"""
Async SQLAlchemy database engine and session factory for Neon PostgreSQL.

Provides:
- Async engine with asyncpg driver for non-blocking database operations
- Session factory for request-scoped database sessions
- Connection pooling configuration for Neon serverless
"""

from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from .config import settings


# Create async engine based on database URL type
# [Task]: T009, [From]: specs/001-task-crud-api/spec.md#Requirements
if "sqlite" in settings.database_url:
    # SQLite doesn't support NullPool with pool_size/max_overflow
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        future=True,
    )
else:
    # Neon PostgreSQL with asyncpg driver
    # Using NullPool for serverless (no persistent connection pooling)
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        future=True,
        poolclass=NullPool,
    )


async def init_db() -> None:
    """Initialize database tables."""
    # [Task]: T009, [From]: specs/001-task-crud-api/spec.md#Requirements
    # Skip automatic table creation on startup
    # Tables are already created in Neon database
    # Use: asyncpg directly or SQLAlchemy async session if needed
    try:
        # Just verify the database is accessible
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"Warning: Could not verify database connection on startup: {e}")


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to inject async database session.

    Usage:
        async def my_endpoint(session: AsyncSession = Depends(get_session)):
            ...
    """
    # [Task]: T009, [From]: specs/001-task-crud-api/spec.md#Requirements
    async_session = AsyncSession(
        engine,
        expire_on_commit=False,
    )
    try:
        yield async_session
    finally:
        await async_session.close()
