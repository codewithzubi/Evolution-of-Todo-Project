"""Add priority and tags fields back to tasks table

This migration re-adds the priority and tags fields to the tasks table.
These fields were previously removed but are now part of the specification
and required for the feature enhancement.

Spec Reference: Priority (Low/Medium/High) and Tags (comma-separated string)

Revision ID: 002
Revises: 001
Create Date: 2026-02-04

Migration Type:
- For NEW databases (development/test): Not needed - schema starts with these fields
- For EXISTING databases (production): Required - adds columns to existing schema
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add priority and tags columns to tasks table.

    Priority: VARCHAR(10) - stores 'low', 'medium', or 'high'
    Tags: TEXT - stores comma-separated string of tags
    Both columns are optional (nullable).
    """
    # Add priority column with default value of 'medium'
    op.add_column(
        "task",
        sa.Column(
            "priority",
            sa.String(10),
            nullable=False,
            server_default="medium",
        ),
    )

    # Add tags column as optional text field
    op.add_column(
        "task",
        sa.Column(
            "tags",
            sa.String(500),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """
    Remove priority and tags columns from tasks table.

    This reverts to the previous schema state (revision 001).
    """
    # Drop tags column first (no dependencies)
    op.drop_column("task", "tags")

    # Drop priority column
    op.drop_column("task", "priority")
