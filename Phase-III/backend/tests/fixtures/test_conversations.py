"""
Test fixtures and factories for conversations and messages.

Provides test data generation for:
- Conversations with various states (active, deleted)
- Messages with different roles (user, assistant, system)
- Tool call and tool result examples
- Multi-user conversation scenarios

Usage in tests:
    def test_something(conversation_factory, message_factory):
        conv = conversation_factory(user_id=user_id, title="Test")
        msg = message_factory(conversation_id=conv.id, role="user")
"""

from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session, select

from src.models.conversation import Conversation
from src.models.message import Message, MessageRole


class ConversationFactory:
    """Factory for creating test conversations."""

    def __init__(self, session: Optional[Session] = None):
        """Initialize factory with optional session for persistence."""
        self.session = session

    def create(
        self,
        user_id: UUID,
        title: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,
    ) -> Conversation:
        """
        Create a conversation instance.

        Args:
            user_id: User ID for conversation owner
            title: Optional conversation title
            metadata: Optional JSON metadata (tags, settings, etc.)
            created_at: Optional creation timestamp (defaults to now)
            deleted_at: Optional deletion timestamp (None = active)

        Returns:
            Conversation instance
        """
        return Conversation(
            id=uuid4(),
            user_id=user_id,
            title=title or f"Conversation {uuid4().hex[:8]}",
            metadata=metadata,
            created_at=created_at or datetime.utcnow(),
            updated_at=datetime.utcnow(),
            deleted_at=deleted_at,
        )

    async def create_async(
        self,
        session: AsyncSession,
        user_id: UUID,
        title: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,
    ) -> Conversation:
        """
        Create and persist a conversation in database.

        Args:
            session: Async database session
            user_id: User ID for conversation owner
            title: Optional conversation title
            metadata: Optional JSON metadata
            created_at: Optional creation timestamp
            deleted_at: Optional deletion timestamp

        Returns:
            Persisted Conversation instance
        """
        conversation = self.create(
            user_id=user_id,
            title=title,
            metadata=metadata,
            created_at=created_at,
            deleted_at=deleted_at,
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        return conversation


class MessageFactory:
    """Factory for creating test messages."""

    def __init__(self, session: Optional[Session] = None):
        """Initialize factory with optional session for persistence."""
        self.session = session

    def create(
        self,
        conversation_id: UUID,
        user_id: UUID,
        role: MessageRole = MessageRole.USER,
        content: Optional[str] = None,
        tool_calls: Optional[dict[str, Any]] = None,
        tool_results: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,
    ) -> Message:
        """
        Create a message instance.

        Args:
            conversation_id: Conversation ID this message belongs to
            user_id: User ID (message sender)
            role: Message role (user, assistant, system)
            content: Message text content
            tool_calls: Optional OpenAI tool_calls array
            tool_results: Optional MCP tool execution results
            metadata: Optional additional metadata
            created_at: Optional creation timestamp (defaults to now)
            deleted_at: Optional deletion timestamp (None = active)

        Returns:
            Message instance
        """
        return Message(
            id=uuid4(),
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content or f"Test message {uuid4().hex[:8]}",
            tool_calls=tool_calls,
            tool_results=tool_results,
            metadata=metadata,
            created_at=created_at or datetime.utcnow(),
            updated_at=datetime.utcnow(),
            deleted_at=deleted_at,
        )

    async def create_async(
        self,
        session: AsyncSession,
        conversation_id: UUID,
        user_id: UUID,
        role: MessageRole = MessageRole.USER,
        content: Optional[str] = None,
        tool_calls: Optional[dict[str, Any]] = None,
        tool_results: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,
    ) -> Message:
        """
        Create and persist a message in database.

        Args:
            session: Async database session
            conversation_id: Conversation ID this message belongs to
            user_id: User ID (message sender)
            role: Message role
            content: Message text content
            tool_calls: Optional tool_calls data
            tool_results: Optional tool_results data
            metadata: Optional metadata
            created_at: Optional creation timestamp
            deleted_at: Optional deletion timestamp

        Returns:
            Persisted Message instance
        """
        message = self.create(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results,
            metadata=metadata,
            created_at=created_at,
            deleted_at=deleted_at,
        )
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message


# ============================================================================
# Fixture Examples: Sample Conversations and Messages
# ============================================================================


def sample_active_conversation(user_id: UUID) -> Conversation:
    """Sample active conversation for testing."""
    factory = ConversationFactory()
    return factory.create(
        user_id=user_id,
        title="Sample Chat",
        metadata={"tags": ["test"], "model": "gpt-4-turbo"},
    )


def sample_deleted_conversation(user_id: UUID) -> Conversation:
    """Sample soft-deleted conversation for testing."""
    factory = ConversationFactory()
    return factory.create(
        user_id=user_id,
        title="Old Chat",
        deleted_at=datetime.utcnow() - timedelta(days=7),
    )


def sample_user_message(conversation_id: UUID, user_id: UUID) -> Message:
    """Sample user-sent message."""
    factory = MessageFactory()
    return factory.create(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.USER,
        content="Can you help me create a task?",
    )


def sample_assistant_message(
    conversation_id: UUID, user_id: UUID, tool_calls_data: Optional[dict] = None
) -> Message:
    """Sample assistant-sent message with optional tool calls."""
    factory = MessageFactory()
    return factory.create(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.ASSISTANT,
        content="I can help you create a task. What would you like to call it?",
        tool_calls=tool_calls_data or {
            "tool_call_id": "call_abc123",
            "function": "add_task",
            "arguments": {"title": "Example Task"},
        },
    )


def sample_tool_results_message(
    conversation_id: UUID, user_id: UUID, tool_result_data: Optional[dict] = None
) -> Message:
    """Sample message with tool execution results."""
    factory = MessageFactory()
    return factory.create(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.ASSISTANT,
        content="Task created successfully!",
        tool_results=tool_result_data or {
            "tool_call_id": "call_abc123",
            "status": "success",
            "result": {"task_id": str(uuid4()), "title": "Example Task"},
        },
    )


# ============================================================================
# Multi-User Test Scenarios
# ============================================================================


def sample_user_a_conversation(user_a_id: UUID) -> Conversation:
    """Sample conversation for User A."""
    factory = ConversationFactory()
    return factory.create(
        user_id=user_a_id,
        title="User A's Chat",
    )


def sample_user_b_conversation(user_b_id: UUID) -> Conversation:
    """Sample conversation for User B (different user)."""
    factory = ConversationFactory()
    return factory.create(
        user_id=user_b_id,
        title="User B's Chat",
    )
