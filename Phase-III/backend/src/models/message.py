# [Task]: T301, [From]: specs/004-ai-chatbot/spec.md#Key-Entities
"""Message model for storing conversation messages.

Represents a single message within a conversation between user and AI.
Supports user, assistant, and system messages with full metadata tracking.

Features:
- Conversation-scoped: belongs to exactly one conversation
- User-scoped: includes user_id for efficient multi-user filtering
- Role-based: user, assistant, or system messages
- Tool integration: stores tool_calls and tool_results as JSONB
- Metadata tracking: additional context for debugging and auditing
- Soft deletes: deleted_at for audit trail preservation
- Timestamps: created_at, updated_at for lifecycle tracking

Part of Phase-III persistence layer (P3.5 Stateless Backend, Persistent Memory).
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column
from pydantic import Field as PydanticField
from sqlmodel import Field, SQLModel


class MessageRole(str, Enum):
    """Message role enumeration for conversation types."""

    USER = "user"  # User-sent message
    ASSISTANT = "assistant"  # AI assistant response
    SYSTEM = "system"  # System message (context, instructions, etc.)

    def __str__(self) -> str:
        """String representation."""
        return self.value


class Message(SQLModel, table=True):
    """Message entity representing a single message in a conversation.

    Each message:
    - Belongs to exactly one conversation (conversation_id foreign key)
    - Belongs to exactly one user (user_id foreign key, for efficient filtering)
    - Has a role (user, assistant, or system)
    - Stores message content as text
    - Optionally stores tool_calls and tool_results as JSONB
    - Includes metadata for debugging, tracing, and auditing
    - Tracks creation and update timestamps
    - Supports soft deletes via deleted_at

    Indexes:
    - (conversation_id, created_at): "get all messages in conversation, ordered by recency"
    - (user_id, created_at): "get all messages sent by user, ordered by recency"
    - (conversation_id, deleted_at): "filter out soft-deleted messages for active conversations"

    Foreign Key Cascade Behavior:
    - conversation_id → conversations.id: CASCADE DELETE (deleting conversation deletes all messages)
    - user_id → users.id: CASCADE DELETE (deleting user deletes all their messages)

    [Task]: T301, [From]: specs/004-ai-chatbot/spec.md#Key-Entities
    [Task]: T301, [From]: specs/004-ai-chatbot/plan.md#Phase-1-Database-Schema
    """

    __tablename__ = "messages"

    # Primary key and timestamps
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when message was created",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when message was last updated",
    )

    # Conversation relationship (foreign key with cascade delete)
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        description="Conversation ID - links message to conversation; cascades on delete",
    )

    # User relationship (for efficient user-scoped queries and isolation)
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="User ID - enables efficient user-scoped queries and audit trails",
    )

    # Message content
    role: MessageRole = Field(
        description="Message role: 'user' (human), 'assistant' (AI), or 'system' (context)",
    )
    content: str = Field(
        description="Message text content (the actual message body)",
    )

    # Tool integration (OpenAI Agents SDK)
    # Stores JSON representation of tool calls made by the assistant
    tool_calls: Optional[list[dict[str, Any]]] = Field(
        default=None,
        sa_column=Column("tool_calls", JSON),
        description="Optional JSON: OpenAI tool_calls array (if assistant invoked tools)",
    )

    # Tool execution results from MCP (Model Context Protocol)
    # Stores JSON representation of tool results returned to the agent
    tool_results: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column("tool_results", JSON),
        description="Optional JSON: MCP tool execution results (if tools were executed)",
    )

    # General metadata for debugging, tracing, and context
    # Examples: embedding_tokens, reasoning_trace, correlation_id, model_used, etc.
    # Note: Python field 'attributes' maps to database column 'metadata'
    attributes: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column("metadata", JSON),
        description="Optional JSON metadata (embedding tokens, traces, correlation IDs, etc.)",
    )

    # Soft delete support for audit trail and recovery
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when message was soft-deleted (null if active). Used for audit trail.",
    )

    def __repr__(self) -> str:
        """String representation for debugging and logging."""
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        status = "deleted" if self.deleted_at else "active"
        tool_info = ""
        if self.tool_calls:
            tool_info = " [has_tool_calls]"
        if self.tool_results:
            tool_info += " [has_tool_results]"
        return (
            f"<Message id={self.id} conversation_id={self.conversation_id} "
            f"role={self.role} content='{content_preview}' status={status}{tool_info}>"
        )

    def is_active(self) -> bool:
        """Check if message is active (not soft-deleted)."""
        return self.deleted_at is None

    def is_deleted(self) -> bool:
        """Check if message is soft-deleted."""
        return self.deleted_at is not None

    def has_tool_calls(self) -> bool:
        """Check if message contains tool calls."""
        return self.tool_calls is not None and len(self.tool_calls) > 0

    def has_tool_results(self) -> bool:
        """Check if message contains tool results."""
        return self.tool_results is not None and len(self.tool_results) > 0

    class Config:
        """Pydantic config for JSON serialization."""

        use_enum_values = True
