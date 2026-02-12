"""Add priority, due_date, and tags fields to tasks table.

Revision ID: 003
Revises: 002
Create Date: 2026-02-10

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add priority, due_date, and tags columns to tasks table."""
    op.add_column('tasks', sa.Column('due_date', sa.Date(), nullable=True))
    op.add_column('tasks', sa.Column('priority', sa.String(length=20), nullable=False, server_default='medium'))
    op.add_column('tasks', sa.Column('tags', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Remove priority, due_date, and tags columns from tasks table."""
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'priority')
    op.drop_column('tasks', 'due_date')
