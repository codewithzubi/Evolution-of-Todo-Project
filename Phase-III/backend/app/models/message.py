"""Message model for Phase-III chat functionality."""
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text, JSON
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .conversation import Conversation


class Message(SQLModel, table=True):
    """Represents a single message exchange (user input or assistant response) within a conversation."""

    __tablename__ = "messages"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique message identifier"
    )

    # Foreign Keys
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        description="Conversation this message belongs to"
    )

    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User who owns this conversation"
    )

    # Message Data
    role: str = Field(
        nullable=False,
        description="Message role: 'user' or 'assistant'"
    )

    content: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Message content"
    )

    tools_used: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
        description="MCP tools invoked (assistant messages only)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="When message was created"
    )

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
