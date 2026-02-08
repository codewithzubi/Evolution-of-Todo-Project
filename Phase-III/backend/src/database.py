# [Task]: T009, [From]: specs/001-task-crud-api/spec.md#Requirements
# [From]: specs/001-task-crud-api/plan.md#Phase-2-Foundational
"""
Async SQLAlchemy database engine and session factory for Neon PostgreSQL.

Provides:
- Async engine with asyncpg driver for non-blocking database operations
- Session factory for request-scoped database sessions
- Connection pooling configuration for Neon serverless
"""

from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
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
    """Initialize database tables and run migrations."""
    # [Task]: T009, [From]: specs/001-task-crud-api/spec.md#Requirements
    # Skip automatic table creation on startup
    # Tables are already created in Neon database
    # Use: asyncpg directly or SQLAlchemy async session if needed
    try:
        # Just verify the database is accessible
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        # Run SQL migrations from migrations directory
        await _run_migrations()

    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")


async def _run_migrations() -> None:
    """Apply SQL migrations from migrations directory."""
    import os
    import pathlib

    try:
        # Get migrations directory path
        migrations_dir = pathlib.Path(__file__).parent / "database" / "migrations"

        if not migrations_dir.exists():
            return

        # Get all .sql files in migrations directory, sorted by name
        migration_files = sorted(migrations_dir.glob("*.sql"))

        if not migration_files:
            return

        async with engine.connect() as conn:
            for migration_file in migration_files:
                try:
                    # Read migration SQL
                    migration_sql = migration_file.read_text()

                    # Split SQL into individual statements
                    # Remove comments and split by semicolon
                    statements = []
                    current_statement = []

                    for line in migration_sql.split('\n'):
                        # Skip comments and empty lines
                        line = line.strip()
                        if not line or line.startswith('--'):
                            continue
                        current_statement.append(line)
                        if line.endswith(';'):
                            statements.append(' '.join(current_statement))
                            current_statement = []

                    # Execute each statement separately
                    for stmt in statements:
                        if stmt.strip():
                            await conn.execute(text(stmt))

                    await conn.commit()
                    print(f"Applied migration: {migration_file.name}")
                except Exception as e:
                    print(f"Warning: Could not apply migration {migration_file.name}: {e}")
                    # Continue with next migration instead of failing
                    continue
    except Exception as e:
        print(f"Warning: Could not run migrations: {e}")


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


# Create synchronous engine and session factory for SQLModel
# Used by chat endpoints and other services that need sync database access
sync_engine = None
SessionLocal = None


def _init_sync_db():
    """Initialize synchronous database engine and session factory."""
    global sync_engine, SessionLocal

    if "sqlite" in settings.database_url:
        # SQLite
        sync_engine = create_engine(
            settings.database_url.replace("sqlite+aiosqlite", "sqlite"),
            echo=settings.debug,
            future=True,
        )
    else:
        # PostgreSQL with psycopg (sync)
        sync_url = settings.database_url.replace("postgresql+asyncpg", "postgresql")
        sync_engine = create_engine(
            sync_url,
            echo=settings.debug,
            future=True,
            pool_pre_ping=True,
        )

    SessionLocal = sessionmaker(
        bind=sync_engine,
        class_=Session,
        expire_on_commit=False,
    )


# Initialize sync database on module load
try:
    _init_sync_db()
except Exception as e:
    print(f"Warning: Could not initialize sync database: {e}")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to inject synchronous database session.

    [Task]: T334, [From]: specs/004-ai-chatbot/spec.md#Requirements
    Used by chat endpoints that need synchronous database access.

    Usage:
        async def my_endpoint(db: Session = Depends(get_db)):
            ...
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
