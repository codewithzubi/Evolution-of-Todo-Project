"""
Alembic environment configuration for async SQLAlchemy.

This file handles migration execution for both online and offline modes.
Configured for async SQLAlchemy with Neon PostgreSQL and SQLite support.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from alembic.config import Config as AlembicConfig
import asyncio

# Import SQLModel metadata and models
import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from sqlmodel import SQLModel
from src.models.task import Task
from src.models.user import User

# Alembic config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model's metadata object for autogenerate support
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the create_engine() call we don't even
    need a DBAPI to be available.
    """
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Execute migrations with the given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Create async engine
    configuration = AlembicConfig(config.config_file_name)

    async_engine = create_async_engine(
        settings.database_url,
        echo=False,
        future=True,
    )

    async with async_engine.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await async_engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
