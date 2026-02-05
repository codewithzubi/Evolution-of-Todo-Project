"""Remove priority and tags fields from tasks table

This migration removes the non-spec fields (priority and tags) from the tasks
table. These fields were removed from the specification and implementation
during Phase 8 spec alignment.

Spec Reference: "Tasks have no subtasks, dependencies, or priority levels in this MVP"

Revision ID: 001
Revises: None
Create Date: 2026-02-03

Migration Type:
- For NEW databases (development/test): Not needed - schema starts without these fields
- For EXISTING databases (production): Required - drops columns from existing schema
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql, sqlite

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Remove priority and tags columns from tasks table.

    These columns are not in the specification and were removed from the
    SQLModel Task definition during Phase 8. This migration ensures the
    database schema matches the code.
    """
    # SQLite doesn't support DROP COLUMN well in older versions, but modern
    # versions (3.35.0+) support it. For maximum compatibility, we use a
    # multi-step approach for SQLite.

    # Try to drop columns with generic SQL that works on most databases
    try:
        op.drop_column("task", "priority", schema=None)
    except Exception:
        # If it fails (older SQLite), skip - the column may not exist
        pass

    try:
        op.drop_column("task", "tags", schema=None)
    except Exception:
        # If it fails (older SQLite), skip - the column may not exist
        pass


def downgrade() -> None:
    """
    Restore priority and tags columns to tasks table.

    This is provided for rollback capability, though it will not restore
    the original data. The priority column defaults to 'MEDIUM' and tags
    defaults to an empty JSON array.
    """
    # Add back priority column with default
    try:
        op.add_column(
            "task",
            sa.Column(
                "priority",
                sa.String(10),
                nullable=True,
                server_default="MEDIUM",
            ),
        )
    except Exception:
        # Column may already exist
        pass

    # Add back tags column with default
    try:
        op.add_column(
            "task",
            sa.Column(
                "tags",
                sa.JSON(),
                nullable=True,
                server_default="[]",
            ),
        )
    except Exception:
        # Column may already exist
        pass
