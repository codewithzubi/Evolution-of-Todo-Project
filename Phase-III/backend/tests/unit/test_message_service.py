# [Task]: T342, [From]: specs/004-ai-chatbot/spec.md#Testing
"""Unit tests for MessagePersistenceService.

Tests:
- Saving user messages
- Saving assistant messages with tool metadata
- Retrieving messages with pagination
- Soft delete functionality
- Conversation history formatting
"""

import pytest
from datetime import datetime
from uuid import uuid4

from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.services.message_service import MessagePersistenceService


@pytest.fixture
def db():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables
    from src.models.base import SQLModel
    SQLModel.metadata.create_all(engine)

    from sqlmodel import Session
    with Session(engine) as session:
        yield session


@pytest.fixture
def user_id():
    """Generate test user ID."""
    return uuid4()


@pytest.fixture
def conversation(db, user_id):
    """Create test conversation."""
    conv = Conversation(
        id=uuid4(),
        user_id=user_id,
        title="Test Conversation",
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


class TestMessagePersistenceService:
    """Tests for message persistence service."""

    @pytest.mark.asyncio
    async def test_save_user_message(self, db, user_id, conversation):
        """Test saving a user message."""
        message = await MessagePersistenceService.save_user_message(
            db=db,
            user_id=user_id,
            conversation_id=conversation.id,
            content="Hello, AI!",
        )

        assert message.id is not None
        assert message.role == MessageRole.USER
        assert message.content == "Hello, AI!"
        assert message.conversation_id == conversation.id
        assert message.user_id == user_id
        assert message.deleted_at is None

    @pytest.mark.asyncio
    async def test_save_user_message_with_metadata(self, db, user_id, conversation):
        """Test saving user message with metadata."""
        metadata = {"source": "test", "tags": ["greeting"]}

        message = await MessagePersistenceService.save_user_message(
            db=db,
            user_id=user_id,
            conversation_id=conversation.id,
            content="Hello",
            metadata=metadata,
        )

        assert message.attributes == metadata

    @pytest.mark.asyncio
    async def test_save_assistant_message(self, db, user_id, conversation):
        """Test saving an assistant message."""
        message = await MessagePersistenceService.save_assistant_message(
            db=db,
            user_id=user_id,
            conversation_id=conversation.id,
            content="Hi there!",
        )

        assert message.role == MessageRole.ASSISTANT
        assert message.content == "Hi there!"
        assert message.tool_calls is None
        assert message.tool_results is None

    @pytest.mark.asyncio
    async def test_save_assistant_message_with_tool_calls(self, db, user_id, conversation):
        """Test saving assistant message with tool calls."""
        tool_calls = [
            {
                "id": "call_1",
                "type": "function",
                "function": {"name": "search", "arguments": '{"query": "test"}'},
            }
        ]

        message = await MessagePersistenceService.save_assistant_message(
            db=db,
            user_id=user_id,
            conversation_id=conversation.id,
            content="Let me search for that.",
            tool_calls=tool_calls,
        )

        assert message.tool_calls == tool_calls

    @pytest.mark.asyncio
    async def test_save_assistant_message_with_tool_results(self, db, user_id, conversation):
        """Test saving assistant message with tool results."""
        tool_results = {"search": "Found results"}

        message = await MessagePersistenceService.save_assistant_message(
            db=db,
            user_id=user_id,
            conversation_id=conversation.id,
            content="Based on the search results...",
            tool_results=tool_results,
        )

        assert message.tool_results == tool_results

    @pytest.mark.asyncio
    async def test_get_conversation_messages_empty(self, db, conversation):
        """Test getting messages from empty conversation."""
        messages, total = await MessagePersistenceService.get_conversation_messages(
            db=db,
            conversation_id=conversation.id,
        )

        assert messages == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_get_conversation_messages(self, db, user_id, conversation):
        """Test retrieving conversation messages."""
        # Add messages
        msg1 = await MessagePersistenceService.save_user_message(
            db=db,
            user_id=user_id,
            conversation_id=conversation.id,
            content="First message",
        )

        msg2 = await MessagePersistenceService.save_assistant_message(
            db=db,
            user_id=user_id,
            conversation_id=conversation.id,
            content="Response",
        )

        # Retrieve
        messages, total = await MessagePersistenceService.get_conversation_messages(
            db=db,
            conversation_id=conversation.id,
        )

        assert len(messages) == 2
        assert total == 2
        assert messages[0].id == msg1.id
        assert messages[1].id == msg2.id
        # Should be in chronological order (oldest first)
        assert messages[0].created_at <= messages[1].created_at

    @pytest.mark.asyncio
    async def test_get_conversation_messages_pagination(self, db, user_id, conversation):
        """Test message pagination."""
        # Add 5 messages
        for i in range(5):
            await MessagePersistenceService.save_user_message(
                db=db,
                user_id=user_id,
                conversation_id=conversation.id,
                content=f"Message {i}",
            )

        # Get first 2
        messages, total = await MessagePersistenceService.get_conversation_messages(
            db=db,
            conversation_id=conversation.id,
            limit=2,
            offset=0,
        )

        assert len(messages) == 2
        assert total == 5

        # Get next 2
        messages, total = await MessagePersistenceService.get_conversation_messages(
            db=db,
            conversation_id=conversation.id,
            limit=2,
            offset=2,
        )

        assert len(messages) == 2
        assert total == 5

    @pytest.mark.asyncio
    async def test_soft_delete_message(self, db, user_id, conversation):
        """Test soft-deleting a message."""
        message = await MessagePersistenceService.save_user_message(
            db=db,
            user_id=user_id,
            conversation_id=conversation.id,
            content="To delete",
        )

        # Delete it
        success = await MessagePersistenceService.soft_delete_message(
            db=db,
            message_id=message.id,
        )

        assert success is True

        # Verify it's marked as deleted
        retrieved = await MessagePersistenceService.get_message(
            db=db,
            message_id=message.id,
        )
        assert retrieved is None  # Filtered out by default

        # Verify with include_deleted=True
        retrieved = await MessagePersistenceService.get_message(
            db=db,
            message_id=message.id,
            include_deleted=True,
        )
        assert retrieved.deleted_at is not None

    @pytest.mark.asyncio
    async def test_soft_delete_nonexistent_message(self, db):
        """Test deleting non-existent message."""
        fake_id = uuid4()
        success = await MessagePersistenceService.soft_delete_message(
            db=db,
            message_id=fake_id,
        )

        assert success is False

    @pytest.mark.asyncio
    async def test_deleted_messages_excluded_by_default(self, db, user_id, conversation):
        """Test that deleted messages are excluded from queries."""
        # Add active and deleted messages
        active = await MessagePersistenceService.save_user_message(
            db=db,
            user_id=user_id,
            conversation_id=conversation.id,
            content="Active",
        )

        deleted = await MessagePersistenceService.save_user_message(
            db=db,
            user_id=user_id,
            conversation_id=conversation.id,
            content="To delete",
        )

        # Delete one
        await MessagePersistenceService.soft_delete_message(
            db=db,
            message_id=deleted.id,
        )

        # Query
        messages, total = await MessagePersistenceService.get_conversation_messages(
            db=db,
            conversation_id=conversation.id,
        )

        # Should only see active message
        assert len(messages) == 1
        assert total == 1
        assert messages[0].id == active.id

    @pytest.mark.asyncio
    async def test_soft_delete_conversation_messages(self, db, user_id, conversation):
        """Test soft-deleting all messages in a conversation."""
        # Add messages
        for i in range(3):
            await MessagePersistenceService.save_user_message(
                db=db,
                user_id=user_id,
                conversation_id=conversation.id,
                content=f"Message {i}",
            )

        # Delete all
        deleted_count = await MessagePersistenceService.soft_delete_conversation_messages(
            db=db,
            conversation_id=conversation.id,
        )

        assert deleted_count == 3

        # Verify all are gone
        messages, total = await MessagePersistenceService.get_conversation_messages(
            db=db,
            conversation_id=conversation.id,
        )

        assert len(messages) == 0
        assert total == 0
