"""Create conversations and messages tables for Phase-III AI Chatbot.

This migration creates the core database schema for conversation persistence:
- conversations table: stores chat sessions between users and AI
- messages table: stores individual messages within conversations

Schema Features:
- User-scoped isolation: user_id foreign key on both tables
- Soft deletes: deleted_at column for audit trail preservation
- Metadata storage: JSONB columns for flexible data (metadata, tool_calls, tool_results)
- Optimized indexes: (user_id, created_at), (conversation_id, created_at), etc.
- Cascade delete: removing user/conversation cascades to related records

Spec Reference:
- specs/004-ai-chatbot/spec.md#Key-Entities
- specs/004-ai-chatbot/plan.md#Phase-1-Database-Schema

Revision ID: 003
Revises: 002
Create Date: 2026-02-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create conversations and messages tables with indexes and constraints.

    Creates:
    1. conversations table with user_id foreign key and indexes
    2. messages table with conversation_id and user_id foreign keys and indexes
    """

    # Create conversations table
    # [Task]: T300, T302, [From]: specs/004-ai-chatbot/spec.md#Key-Entities
    op.create_table(
        "conversations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSON() if "postgresql" in op.get_bind().dialect.name else sa.JSON(),
            nullable=True,
            comment="Optional JSON metadata (conversation tags, settings, context info, etc.)",
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for conversations table
    # Index 1: (user_id, created_at) - optimize "get conversations for user, ordered by recency"
    op.create_index(
        op.f("ix_conversations_user_id_created_at"),
        "conversations",
        ["user_id", "created_at"],
        unique=False,
    )

    # Index 2: (user_id, deleted_at) - optimize "get active conversations for user"
    op.create_index(
        op.f("ix_conversations_user_id_deleted_at"),
        "conversations",
        ["user_id", "deleted_at"],
        unique=False,
    )

    # Index 3: user_id (implicit from foreign key, but explicit for query optimizer)
    op.create_index(
        op.f("ix_conversations_user_id"),
        "conversations",
        ["user_id"],
        unique=False,
    )

    # Create messages table
    # [Task]: T301, T302, [From]: specs/004-ai-chatbot/spec.md#Key-Entities
    op.create_table(
        "messages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("conversation_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),  # 'user', 'assistant', 'system'
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "tool_calls",
            postgresql.JSON() if "postgresql" in op.get_bind().dialect.name else sa.JSON(),
            nullable=True,
            comment="Optional JSON: OpenAI tool_calls array (if assistant invoked tools)",
        ),
        sa.Column(
            "tool_results",
            postgresql.JSON() if "postgresql" in op.get_bind().dialect.name else sa.JSON(),
            nullable=True,
            comment="Optional JSON: MCP tool execution results (if tools were executed)",
        ),
        sa.Column(
            "metadata",
            postgresql.JSON() if "postgresql" in op.get_bind().dialect.name else sa.JSON(),
            nullable=True,
            comment="Optional JSON metadata (embedding tokens, traces, correlation IDs, etc.)",
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for messages table
    # Index 1: (conversation_id, created_at) - optimize "get all messages in conversation, ordered by recency"
    op.create_index(
        op.f("ix_messages_conversation_id_created_at"),
        "messages",
        ["conversation_id", "created_at"],
        unique=False,
    )

    # Index 2: (user_id, created_at) - optimize "get all messages sent by user, ordered by recency"
    op.create_index(
        op.f("ix_messages_user_id_created_at"),
        "messages",
        ["user_id", "created_at"],
        unique=False,
    )

    # Index 3: (conversation_id, deleted_at) - optimize "filter out soft-deleted messages for active conversations"
    op.create_index(
        op.f("ix_messages_conversation_id_deleted_at"),
        "messages",
        ["conversation_id", "deleted_at"],
        unique=False,
    )

    # Index 4: conversation_id (implicit from foreign key)
    op.create_index(
        op.f("ix_messages_conversation_id"),
        "messages",
        ["conversation_id"],
        unique=False,
    )

    # Index 5: user_id (implicit from foreign key)
    op.create_index(
        op.f("ix_messages_user_id"),
        "messages",
        ["user_id"],
        unique=False,
    )

    # Index 6: role - optimize filtering by message role
    op.create_index(
        op.f("ix_messages_role"),
        "messages",
        ["role"],
        unique=False,
    )


def downgrade() -> None:
    """
    Drop conversations and messages tables and their indexes.

    Removes:
    1. All indexes from messages and conversations tables
    2. messages table (drop before conversations due to foreign key)
    3. conversations table
    """

    # Drop messages table (must be first due to foreign key constraint)
    # Indexes are automatically dropped with the table
    op.drop_table("messages")

    # Drop conversations table
    op.drop_table("conversations")
