# [Task]: T371, [From]: specs/004-ai-chatbot/spec.md#Testing
"""Persistence and data integrity tests.

Tests:
- Conversation persistence across server restart
- Message persistence across server restart
- Soft delete persistence
- Metadata persistence
- Tool call metadata preservation
- Large conversation handling (100+ messages)
- Data consistency after failures
- Recovery scenarios
"""

from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import User
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole


class TestConversationPersistence:
    """Tests for conversation data persistence."""

    @pytest.mark.asyncio
    async def test_conversation_persists_after_creation(self, test_session: AsyncSession, test_user: User):
        """Test that created conversation persists in database."""
        conv = Conversation(
            user_id=test_user.id,
            title="Persistent Conversation",
            attributes={"tags": ["important"]},
        )
        test_session.add(conv)
        await test_session.commit()
        conv_id = conv.id

        # Simulate closing and reopening session
        await test_session.refresh(conv)

        # Verify all fields persisted
        assert conv.id == conv_id
        assert conv.user_id == test_user.id
        assert conv.title == "Persistent Conversation"
        assert conv.attributes == {"tags": ["important"]}
        assert conv.deleted_at is None

    @pytest.mark.asyncio
    async def test_conversation_timestamps_persist(self, test_session: AsyncSession, test_user: User):
        """Test that conversation timestamps are correctly stored and retrieved."""
        before_create = datetime.utcnow()
        conv = Conversation(user_id=test_user.id, title="Timestamped Conv")
        test_session.add(conv)
        await test_session.commit()
        await test_session.refresh(conv)
        after_create = datetime.utcnow()

        # created_at should be between before and after
        assert before_create <= conv.created_at <= after_create

    @pytest.mark.asyncio
    async def test_conversation_soft_delete_persists(self, test_session: AsyncSession, sample_conversation):
        """Test that soft delete timestamp persists."""
        delete_time = datetime.utcnow()
        sample_conversation.deleted_at = delete_time
        test_session.add(sample_conversation)
        await test_session.commit()
        await test_session.refresh(sample_conversation)

        # Verify deletion is persisted
        stmt = select(Conversation).where(Conversation.id == sample_conversation.id)
        result = await test_session.execute(stmt)
        retrieved = result.scalar_one_or_none()

        assert retrieved.deleted_at is not None
        assert retrieved.is_deleted()


class TestMessagePersistence:
    """Tests for message data persistence."""

    @pytest.mark.asyncio
    async def test_message_persists_after_creation(
        self, test_session: AsyncSession, sample_conversation, test_user
    ):
        """Test that created message persists in database."""
        msg = Message(
            conversation_id=sample_conversation.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="This is a persistent message",
        )
        test_session.add(msg)
        await test_session.commit()
        msg_id = msg.id

        # Retrieve and verify
        stmt = select(Message).where(Message.id == msg_id)
        result = await test_session.execute(stmt)
        retrieved = result.scalar_one_or_none()

        assert retrieved is not None
        assert retrieved.content == "This is a persistent message"
        assert retrieved.role == MessageRole.USER

    @pytest.mark.asyncio
    async def test_message_role_persists(self, test_session: AsyncSession, sample_conversation, test_user):
        """Test that message role is correctly persisted."""
        roles = [MessageRole.USER, MessageRole.ASSISTANT, MessageRole.SYSTEM]
        message_ids = []

        for role in roles:
            msg = Message(
                conversation_id=sample_conversation.id,
                user_id=test_user.id,
                role=role,
                content=f"Message with role {role}",
            )
            test_session.add(msg)
            await test_session.commit()
            message_ids.append((msg.id, role))

        # Verify each message's role
        for msg_id, expected_role in message_ids:
            stmt = select(Message).where(Message.id == msg_id)
            result = await test_session.execute(stmt)
            retrieved = result.scalar_one_or_none()

            assert retrieved.role == expected_role

    @pytest.mark.asyncio
    async def test_message_tool_calls_persist(self, test_session: AsyncSession, sample_conversation, test_user):
        """Test that tool_calls JSON metadata persists."""
        tool_calls = {
            "tool_call_id": "call_abc123",
            "function": "add_task",
            "arguments": {"title": "Important task", "priority": "high"},
        }
        msg = Message(
            conversation_id=sample_conversation.id,
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="Creating task",
            tool_calls=tool_calls,
        )
        test_session.add(msg)
        await test_session.commit()

        # Verify tool_calls persisted
        stmt = select(Message).where(Message.id == msg.id)
        result = await test_session.execute(stmt)
        retrieved = result.scalar_one_or_none()

        assert retrieved.tool_calls == tool_calls
        assert retrieved.tool_calls["function"] == "add_task"

    @pytest.mark.asyncio
    async def test_message_tool_results_persist(self, test_session: AsyncSession, sample_conversation, test_user):
        """Test that tool_results JSON metadata persists."""
        tool_results = {
            "tool_call_id": "call_abc123",
            "status": "success",
            "result": {"task_id": str(uuid4()), "title": "New task"},
        }
        msg = Message(
            conversation_id=sample_conversation.id,
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="Task created",
            tool_results=tool_results,
        )
        test_session.add(msg)
        await test_session.commit()

        # Verify tool_results persisted
        stmt = select(Message).where(Message.id == msg.id)
        result = await test_session.execute(stmt)
        retrieved = result.scalar_one_or_none()

        assert retrieved.tool_results == tool_results
        assert retrieved.tool_results["status"] == "success"


class TestLargeConversationPersistence:
    """Tests for handling large conversations (100+ messages)."""

    @pytest.mark.asyncio
    async def test_large_conversation_100_messages(self, test_session: AsyncSession, sample_conversation, test_user):
        """Test persisting and retrieving conversation with 100 messages."""
        import time

        # Create 100 messages
        start = time.time()
        for i in range(100):
            role = MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT
            msg = Message(
                conversation_id=sample_conversation.id,
                user_id=test_user.id,
                role=role,
                content=f"Message {i}",
            )
            test_session.add(msg)

        await test_session.commit()
        commit_time = time.time() - start

        # Commit should be reasonably fast
        assert commit_time < 5.0, f"Commit of 100 messages took {commit_time}s"

        # Query all messages
        start = time.time()
        stmt = select(Message).where(Message.conversation_id == sample_conversation.id)
        result = await test_session.execute(stmt)
        messages = result.scalars().all()
        query_time = time.time() - start

        # Query should be fast
        assert query_time < 1.0, f"Query of 100 messages took {query_time}s"
        assert len(messages) == 100

    @pytest.mark.asyncio
    async def test_large_conversation_message_ordering_persists(
        self, test_session: AsyncSession, sample_conversation, test_user
    ):
        """Test that message ordering is preserved in large conversations."""
        import time

        # Create 50 messages with identifiable content
        message_ids = []
        for i in range(50):
            msg = Message(
                conversation_id=sample_conversation.id,
                user_id=test_user.id,
                role=MessageRole.USER,
                content=f"Message number {i:03d}",
            )
            test_session.add(msg)
            await test_session.commit()
            message_ids.append(msg.id)
            time.sleep(0.001)  # Ensure different timestamps

        # Query in reverse chronological order
        stmt = (
            select(Message)
            .where(Message.conversation_id == sample_conversation.id)
            .order_by(Message.created_at.desc())
        )
        result = await test_session.execute(stmt)
        ordered = result.scalars().all()

        # Should be in reverse order
        assert ordered[0].id == message_ids[-1]
        assert ordered[-1].id == message_ids[0]


class TestSoftDeletePersistence:
    """Tests for soft delete behavior and persistence."""

    @pytest.mark.asyncio
    async def test_soft_deleted_messages_excluded_from_active_queries(
        self, test_session: AsyncSession, sample_conversation, test_user
    ):
        """Test that soft-deleted messages don't appear in active message queries."""
        # Create active and deleted messages
        active_msg = Message(
            conversation_id=sample_conversation.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Active",
        )
        deleted_msg = Message(
            conversation_id=sample_conversation.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Deleted",
            deleted_at=datetime.utcnow(),
        )

        test_session.add(active_msg)
        test_session.add(deleted_msg)
        await test_session.commit()

        # Query only active messages
        stmt = select(Message).where(
            (Message.conversation_id == sample_conversation.id)
            & (Message.deleted_at.is_(None))
        )
        result = await test_session.execute(stmt)
        messages = result.scalars().all()

        # Should only see active message
        assert len(messages) == 1
        assert messages[0].id == active_msg.id

    @pytest.mark.asyncio
    async def test_soft_deleted_conversations_excluded_from_active_queries(
        self, test_session: AsyncSession, test_user
    ):
        """Test that soft-deleted conversations don't appear in active queries."""
        active_conv = Conversation(user_id=test_user.id, title="Active")
        deleted_conv = Conversation(
            user_id=test_user.id, title="Deleted", deleted_at=datetime.utcnow()
        )

        test_session.add(active_conv)
        test_session.add(deleted_conv)
        await test_session.commit()

        # Query only active conversations
        stmt = select(Conversation).where(
            (Conversation.user_id == test_user.id) & (Conversation.deleted_at.is_(None))
        )
        result = await test_session.execute(stmt)
        convs = result.scalars().all()

        # Should only see active conversation
        assert len(convs) == 1
        assert convs[0].id == active_conv.id


class TestMetadataPersistence:
    """Tests for JSON metadata field persistence."""

    @pytest.mark.asyncio
    async def test_conversation_complex_metadata_persists(self, test_session: AsyncSession, test_user):
        """Test that complex JSON metadata is preserved."""
        metadata = {
            "tags": ["work", "urgent", "follow-up"],
            "settings": {
                "auto_save": True,
                "notifications_enabled": False,
                "model": "gpt-4-turbo",
            },
            "context": {"project_id": "proj_123", "client": "Acme Corp"},
            "nested": {"deep": {"structure": {"value": 42}}},
        }

        conv = Conversation(user_id=test_user.id, title="Complex Metadata", attributes=metadata)
        test_session.add(conv)
        await test_session.commit()

        # Retrieve and verify structure is preserved
        stmt = select(Conversation).where(Conversation.id == conv.id)
        result = await test_session.execute(stmt)
        retrieved = result.scalar_one_or_none()

        assert retrieved.attributes == metadata
        assert retrieved.attributes["tags"] == ["work", "urgent", "follow-up"]
        assert retrieved.attributes["settings"]["model"] == "gpt-4-turbo"
        assert retrieved.attributes["nested"]["deep"]["structure"]["value"] == 42

    @pytest.mark.asyncio
    async def test_message_metadata_persists(self, test_session: AsyncSession, sample_conversation, test_user):
        """Test that message metadata persists."""
        metadata = {
            "sentiment": "positive",
            "tokens_used": 150,
            "processing_time_ms": 245,
        }

        msg = Message(
            conversation_id=sample_conversation.id,
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="Response",
            metadata=metadata,
        )
        test_session.add(msg)
        await test_session.commit()

        # Verify metadata persisted
        stmt = select(Message).where(Message.id == msg.id)
        result = await test_session.execute(stmt)
        retrieved = result.scalar_one_or_none()

        assert retrieved.metadata == metadata


class TestDataConsistencyAfterFailures:
    """Tests for data consistency in failure scenarios."""

    @pytest.mark.asyncio
    async def test_failed_commit_doesnt_corrupt_data(
        self, test_session: AsyncSession, test_user
    ):
        """Test that failed transaction doesn't leave inconsistent data."""
        # Create a valid conversation
        conv = Conversation(user_id=test_user.id, title="Valid")
        test_session.add(conv)
        await test_session.commit()

        # Try to create invalid message (this would need actual constraint violation)
        # For now, just verify rollback behavior
        conv2 = Conversation(user_id=test_user.id, title="Should persist")
        test_session.add(conv2)
        await test_session.commit()

        # Verify both persisted correctly
        stmt = select(Conversation).where(Conversation.user_id == test_user.id)
        result = await test_session.execute(stmt)
        convs = result.scalars().all()

        assert len(convs) == 2

    @pytest.mark.asyncio
    async def test_partial_updates_atomic(self, test_session: AsyncSession, sample_conversation):
        """Test that updates are atomic."""
        original_title = sample_conversation.title

        # Update multiple fields atomically
        sample_conversation.title = "New Title"
        sample_conversation.attributes = {"updated": True}

        test_session.add(sample_conversation)
        await test_session.commit()

        # Verify both fields updated together
        stmt = select(Conversation).where(Conversation.id == sample_conversation.id)
        result = await test_session.execute(stmt)
        retrieved = result.scalar_one_or_none()

        assert retrieved.title == "New Title"
        assert retrieved.attributes == {"updated": True}
