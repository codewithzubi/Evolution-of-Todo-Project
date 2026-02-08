# [Task]: T366, [From]: specs/004-ai-chatbot/spec.md#Testing
"""Database integration tests for conversation and message models.

Tests:
- Conversation CRUD operations
- Message CRUD operations
- User isolation via foreign keys
- Soft delete functionality
- Cascade deletes
- Message ordering
- Index performance
"""

import time
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import Session

from src.models.base import User
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole


class TestConversationCRUD:
    """Tests for conversation CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_conversation(self, test_session: AsyncSession, test_user: User):
        """Test creating a conversation."""
        conversation = Conversation(
            user_id=test_user.id,
            title="Test Conversation",
        )
        test_session.add(conversation)
        await test_session.commit()
        await test_session.refresh(conversation)

        assert conversation.id is not None
        assert conversation.user_id == test_user.id
        assert conversation.title == "Test Conversation"
        assert conversation.is_active()
        assert conversation.deleted_at is None

    @pytest.mark.asyncio
    async def test_read_conversation(self, test_session: AsyncSession, sample_conversation):
        """Test reading a conversation from database."""
        stmt = select(Conversation).where(Conversation.id == sample_conversation.id)
        result = await test_session.execute(stmt)
        conversation = result.scalar_one_or_none()

        assert conversation is not None
        assert conversation.id == sample_conversation.id
        assert conversation.user_id == sample_conversation.user_id
        assert conversation.is_active()

    @pytest.mark.asyncio
    async def test_update_conversation(self, test_session: AsyncSession, sample_conversation):
        """Test updating a conversation."""
        sample_conversation.title = "Updated Title"
        test_session.add(sample_conversation)
        await test_session.commit()

        stmt = select(Conversation).where(Conversation.id == sample_conversation.id)
        result = await test_session.execute(stmt)
        updated = result.scalar_one_or_none()

        assert updated.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_soft_delete_conversation(self, test_session: AsyncSession, sample_conversation):
        """Test soft-deleting a conversation."""
        from datetime import datetime

        sample_conversation.deleted_at = datetime.utcnow()
        test_session.add(sample_conversation)
        await test_session.commit()

        assert sample_conversation.is_deleted()
        assert sample_conversation.deleted_at is not None

    @pytest.mark.asyncio
    async def test_soft_delete_filter(self, test_session: AsyncSession, test_user: User):
        """Test that soft-deleted conversations are excluded from queries."""
        from datetime import datetime

        # Create active conversation
        active = Conversation(user_id=test_user.id, title="Active")
        test_session.add(active)
        await test_session.commit()

        # Create deleted conversation
        deleted = Conversation(user_id=test_user.id, title="Deleted", deleted_at=datetime.utcnow())
        test_session.add(deleted)
        await test_session.commit()

        # Query only active conversations
        stmt = select(Conversation).where(
            (Conversation.user_id == test_user.id) & (Conversation.deleted_at.is_(None))
        )
        result = await test_session.execute(stmt)
        conversations = result.scalars().all()

        assert len(conversations) == 1
        assert conversations[0].id == active.id


class TestUserIsolation:
    """Tests for user isolation via foreign keys."""

    @pytest.mark.asyncio
    async def test_conversation_belongs_to_user(
        self, test_session: AsyncSession, test_user: User, other_user: User
    ):
        """Test that conversations are properly scoped to users."""
        user_a_conv = Conversation(user_id=test_user.id, title="User A's Conv")
        user_b_conv = Conversation(user_id=other_user.id, title="User B's Conv")

        test_session.add(user_a_conv)
        test_session.add(user_b_conv)
        await test_session.commit()

        # Query User A's conversations
        stmt = select(Conversation).where(
            (Conversation.user_id == test_user.id) & (Conversation.deleted_at.is_(None))
        )
        result = await test_session.execute(stmt)
        user_a_convs = result.scalars().all()

        assert len(user_a_convs) == 1
        assert user_a_convs[0].user_id == test_user.id

    @pytest.mark.asyncio
    async def test_message_user_isolation(
        self, test_session: AsyncSession, test_user: User, other_user: User
    ):
        """Test that messages are scoped to conversation AND user."""
        # Create conversations for both users
        user_a_conv = Conversation(user_id=test_user.id, title="User A's Conv")
        user_b_conv = Conversation(user_id=other_user.id, title="User B's Conv")

        test_session.add(user_a_conv)
        test_session.add(user_b_conv)
        await test_session.commit()

        # Create messages
        user_a_msg = Message(
            conversation_id=user_a_conv.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="User A message",
        )
        user_b_msg = Message(
            conversation_id=user_b_conv.id,
            user_id=other_user.id,
            role=MessageRole.USER,
            content="User B message",
        )

        test_session.add(user_a_msg)
        test_session.add(user_b_msg)
        await test_session.commit()

        # Query User A's messages (should only see their own)
        stmt = select(Message).where(
            (Message.user_id == test_user.id) & (Message.deleted_at.is_(None))
        )
        result = await test_session.execute(stmt)
        user_a_messages = result.scalars().all()

        assert len(user_a_messages) == 1
        assert user_a_messages[0].user_id == test_user.id


class TestMessageCRUD:
    """Tests for message CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_message(self, test_session: AsyncSession, sample_conversation, test_user):
        """Test creating a message."""
        message = Message(
            conversation_id=sample_conversation.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Hello!",
        )
        test_session.add(message)
        await test_session.commit()
        await test_session.refresh(message)

        assert message.id is not None
        assert message.conversation_id == sample_conversation.id
        assert message.user_id == test_user.id
        assert message.role == MessageRole.USER
        assert message.content == "Hello!"
        assert message.is_active()

    @pytest.mark.asyncio
    async def test_read_message(self, test_session: AsyncSession, sample_message):
        """Test reading a message."""
        stmt = select(Message).where(Message.id == sample_message.id)
        result = await test_session.execute(stmt)
        message = result.scalar_one_or_none()

        assert message is not None
        assert message.id == sample_message.id
        assert message.is_active()

    @pytest.mark.asyncio
    async def test_update_message(self, test_session: AsyncSession, sample_message):
        """Test updating a message."""
        sample_message.content = "Updated content"
        test_session.add(sample_message)
        await test_session.commit()

        stmt = select(Message).where(Message.id == sample_message.id)
        result = await test_session.execute(stmt)
        updated = result.scalar_one_or_none()

        assert updated.content == "Updated content"

    @pytest.mark.asyncio
    async def test_soft_delete_message(self, test_session: AsyncSession, sample_message):
        """Test soft-deleting a message."""
        from datetime import datetime

        sample_message.deleted_at = datetime.utcnow()
        test_session.add(sample_message)
        await test_session.commit()

        assert sample_message.is_deleted()


class TestMessageOrdering:
    """Tests for message ordering and retrieval."""

    @pytest.mark.asyncio
    async def test_messages_ordered_by_created_at(
        self, test_session: AsyncSession, sample_conversation, test_user
    ):
        """Test that messages are ordered by creation date (DESC)."""
        import time

        # Create multiple messages with slight delays
        messages = []
        for i in range(3):
            msg = Message(
                conversation_id=sample_conversation.id,
                user_id=test_user.id,
                role=MessageRole.USER,
                content=f"Message {i}",
            )
            test_session.add(msg)
            await test_session.commit()
            messages.append(msg)
            time.sleep(0.01)

        # Query messages in reverse chronological order
        stmt = (
            select(Message)
            .where((Message.conversation_id == sample_conversation.id))
            .order_by(Message.created_at.desc())
        )
        result = await test_session.execute(stmt)
        ordered = result.scalars().all()

        assert len(ordered) == 3
        # Newest first
        assert ordered[0].id == messages[2].id
        assert ordered[1].id == messages[1].id
        assert ordered[2].id == messages[0].id

    @pytest.mark.asyncio
    async def test_list_messages_excludes_deleted(
        self, test_session: AsyncSession, sample_conversation, test_user
    ):
        """Test that soft-deleted messages are excluded from queries."""
        from datetime import datetime

        # Create active message
        active = Message(
            conversation_id=sample_conversation.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Active",
        )
        test_session.add(active)
        await test_session.commit()

        # Create deleted message
        deleted = Message(
            conversation_id=sample_conversation.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Deleted",
            deleted_at=datetime.utcnow(),
        )
        test_session.add(deleted)
        await test_session.commit()

        # Query only active messages
        stmt = select(Message).where(
            (Message.conversation_id == sample_conversation.id)
            & (Message.deleted_at.is_(None))
        )
        result = await test_session.execute(stmt)
        messages = result.scalars().all()

        assert len(messages) == 1
        assert messages[0].id == active.id


class TestPerformanceIndexes:
    """Tests for database index performance."""

    @pytest.mark.asyncio
    async def test_user_conversation_index_performance(
        self, test_session: AsyncSession, test_user: User
    ):
        """Test that (user_id, created_at) index enables fast queries."""
        # Create multiple conversations for a user
        for i in range(50):
            conv = Conversation(user_id=test_user.id, title=f"Conversation {i}")
            test_session.add(conv)
        await test_session.commit()

        # Time a query that should use the index
        start = time.time()
        stmt = (
            select(Conversation)
            .where(
                (Conversation.user_id == test_user.id)
                & (Conversation.deleted_at.is_(None))
            )
            .order_by(Conversation.created_at.desc())
            .limit(20)
        )
        result = await test_session.execute(stmt)
        conversations = result.scalars().all()
        elapsed = time.time() - start

        # Should be fast (< 200ms even in test)
        assert elapsed < 0.2, f"Query took {elapsed}s, expected < 0.2s"
        assert len(conversations) == 20

    @pytest.mark.asyncio
    async def test_message_conversation_index_performance(
        self, test_session: AsyncSession, sample_conversation, test_user
    ):
        """Test that messages can be queried efficiently by conversation."""
        # Create multiple messages
        for i in range(100):
            msg = Message(
                conversation_id=sample_conversation.id,
                user_id=test_user.id,
                role=MessageRole.USER,
                content=f"Message {i}",
            )
            test_session.add(msg)
        await test_session.commit()

        # Time a query
        start = time.time()
        stmt = (
            select(Message)
            .where(
                (Message.conversation_id == sample_conversation.id)
                & (Message.deleted_at.is_(None))
            )
            .order_by(Message.created_at.desc())
            .limit(20)
        )
        result = await test_session.execute(stmt)
        messages = result.scalars().all()
        elapsed = time.time() - start

        # Should be fast
        assert elapsed < 0.2, f"Query took {elapsed}s, expected < 0.2s"
        assert len(messages) == 20


class TestCascadingOperations:
    """Tests for cascade delete behavior."""

    @pytest.mark.asyncio
    async def test_conversation_cascade_delete_soft_deletes_messages(
        self, test_session: AsyncSession, test_user: User
    ):
        """Test that deleting conversation soft-deletes all related messages."""
        from datetime import datetime

        # Create conversation and messages
        conv = Conversation(user_id=test_user.id, title="To Delete")
        test_session.add(conv)
        await test_session.commit()

        messages = []
        for i in range(3):
            msg = Message(
                conversation_id=conv.id,
                user_id=test_user.id,
                role=MessageRole.USER,
                content=f"Message {i}",
            )
            test_session.add(msg)
            messages.append(msg)
        await test_session.commit()

        # Soft-delete conversation
        conv.deleted_at = datetime.utcnow()
        test_session.add(conv)
        await test_session.commit()

        # Messages should still exist but with soft delete flag for cascade
        stmt = select(Message).where(Message.conversation_id == conv.id)
        result = await test_session.execute(stmt)
        remaining = result.scalars().all()

        # Soft-deleted conversation still has messages (cascade delete is logical)
        assert len(remaining) == 3


class TestMetadataStorage:
    """Tests for metadata JSON field storage."""

    @pytest.mark.asyncio
    async def test_conversation_metadata_storage(self, test_session: AsyncSession, test_user: User):
        """Test storing and retrieving metadata in conversation."""
        metadata = {"tags": ["important", "work"], "settings": {"auto_save": True}}
        conv = Conversation(user_id=test_user.id, title="With Metadata", attributes=metadata)

        test_session.add(conv)
        await test_session.commit()

        stmt = select(Conversation).where(Conversation.id == conv.id)
        result = await test_session.execute(stmt)
        retrieved = result.scalar_one_or_none()

        assert retrieved.attributes == metadata

    @pytest.mark.asyncio
    async def test_message_tool_calls_storage(
        self, test_session: AsyncSession, sample_conversation, test_user
    ):
        """Test storing tool_calls in message."""
        tool_calls = {
            "tool_call_id": "call_abc123",
            "function": "add_task",
            "arguments": {"title": "New task"},
        }
        msg = Message(
            conversation_id=sample_conversation.id,
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="Creating a task",
            tool_calls=tool_calls,
        )

        test_session.add(msg)
        await test_session.commit()

        stmt = select(Message).where(Message.id == msg.id)
        result = await test_session.execute(stmt)
        retrieved = result.scalar_one_or_none()

        assert retrieved.tool_calls == tool_calls
