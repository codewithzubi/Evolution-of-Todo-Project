# [Task]: T300, [From]: specs/004-ai-chatbot/spec.md#Key-Entities
"""Conversation model for storing chat sessions.

Represents a single conversation between a user and the AI chatbot.
Part of Phase-III persistence layer (P3.5 Stateless Backend, Persistent Memory).

Features:
- User-scoped: each conversation belongs to exactly one user
- Soft deletes: deleted_at timestamp for audit trail
- Metadata storage: JSONB field for conversation settings/tags
- Timestamps: created_at, updated_at for tracking lifecycle
- Indexed: (user_id, created_at) for efficient user conversation listing
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import Field as PydanticField
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """Conversation entity representing a chat session between user and AI.

    Each conversation:
    - Belongs to exactly one user (user_id foreign key)
    - Can have multiple messages
    - Includes optional title for display
    - Stores optional metadata as JSONB (e.g., tags, settings, model params)
    - Tracks creation and update timestamps with soft delete support

    Indexes:
    - (user_id, created_at): optimizes "get conversations for user, sorted by recency"
    - (user_id, deleted_at): optimizes "get active conversations for user"

    Foreign Key Cascade Behavior:
    - user_id → users.id: CASCADE DELETE (deleting user deletes all conversations)
    - Related messages deleted via conversation cascade

    [Task]: T300, [From]: specs/004-ai-chatbot/spec.md#Key-Entities
    """

    __tablename__ = "conversations"

    # Primary key and timestamps
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when conversation was created",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when conversation was last updated",
    )

    # User relationship (foreign key - enforces row-level security)
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="User ID - enforces conversation ownership and enables user-scoped queries",
    )

    # Conversation metadata
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Conversation title (optional, user-provided display name)",
    )

    # Additional metadata stored as JSONB (PostgreSQL) or JSON (SQLite)
    # Examples: conversation_tags, model_params, system_prompt_version, etc.
    # Note: Python field 'attributes' maps to database column 'metadata'
    attributes: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column("metadata", JSON),
        description="Optional JSON metadata (conversation tags, settings, context info, etc.)",
    )

    # Soft delete support for audit trail and recovery
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when conversation was soft-deleted (null if active). Used for audit trail.",
    )

    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        status = "deleted" if self.deleted_at else "active"
        title_preview = (
            f"'{self.title[:30]}...'" if self.title and len(self.title) > 30
            else f"'{self.title}'" if self.title
            else "untitled"
        )
        return (
            f"<Conversation id={self.id} user_id={self.user_id} "
            f"title={title_preview} status={status}>"
        )

    def is_active(self) -> bool:
        """Check if conversation is active (not soft-deleted)."""
        return self.deleted_at is None

    def is_deleted(self) -> bool:
        """Check if conversation is soft-deleted."""
        return self.deleted_at is not None
