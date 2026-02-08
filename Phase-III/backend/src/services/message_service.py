# [Task]: T335, [From]: specs/004-ai-chatbot/spec.md#FR-010
"""Message persistence service for saving and retrieving messages.

Handles:
- Saving user messages to database
- Saving AI assistant responses with tool metadata
- Soft delete support
- Efficient querying with filtering
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, and_, desc, select

from ..models.message import Message, MessageRole

logger = logging.getLogger(__name__)


# [Task]: T335
class MessagePersistenceService:
    """Service for message persistence and retrieval."""

    @staticmethod
    async def save_user_message(
        db: Session,
        user_id: UUID,
        conversation_id: UUID,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Save a user message to the database.

        Args:
            db: Database session
            user_id: User ID (for efficient filtering)
            conversation_id: Conversation ID
            content: Message text
            metadata: Optional metadata

        Returns:
            Created Message object

        Raises:
            Exception: If database operation fails
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=MessageRole.USER,
            content=content,
            attributes=metadata,
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        logger.debug(
            f"Saved user message {message.id} to conversation {conversation_id} "
            f"(content_length={len(content)})"
        )

        return message

    @staticmethod
    async def save_assistant_message(
        db: Session,
        user_id: UUID,
        conversation_id: UUID,
        content: str,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tool_results: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Save an assistant message to the database.

        Args:
            db: Database session
            user_id: User ID
            conversation_id: Conversation ID
            content: Assistant response text
            tool_calls: Optional list of tool calls made by assistant
            tool_results: Optional results from tool execution
            metadata: Optional additional metadata

        Returns:
            Created Message object

        Raises:
            Exception: If database operation fails
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results,
            attributes=metadata,
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        tool_info = ""
        if tool_calls:
            tool_info += f" with {len(tool_calls)} tool calls"
        if tool_results:
            tool_info += " [has results]"

        logger.debug(
            f"Saved assistant message {message.id} to conversation {conversation_id} "
            f"(content_length={len(content)}{tool_info})"
        )

        return message

    @staticmethod
    async def soft_delete_message(
        db: Session,
        message_id: UUID,
    ) -> bool:
        """Soft-delete a message by setting deleted_at timestamp.

        Args:
            db: Database session
            message_id: Message ID to delete

        Returns:
            True if deleted, False if not found

        Raises:
            Exception: If database operation fails
        """
        statement = select(Message).where(Message.id == message_id)
        message = db.execute(statement).scalars().first()

        if not message:
            logger.warning(f"Message {message_id} not found for deletion")
            return False

        message.deleted_at = datetime.utcnow()
        db.add(message)
        db.commit()

        logger.info(f"Soft-deleted message {message_id}")
        return True

    @staticmethod
    async def get_message(
        db: Session,
        message_id: UUID,
        include_deleted: bool = False,
    ) -> Optional[Message]:
        """Get a single message by ID.

        Args:
            db: Database session
            message_id: Message ID to retrieve
            include_deleted: Whether to include soft-deleted messages

        Returns:
            Message object or None if not found

        Raises:
            Exception: If database operation fails
        """
        filters = [Message.id == message_id]
        if not include_deleted:
            filters.append(Message.deleted_at.is_(None))

        statement = select(Message).where(and_(*filters))
        message = db.execute(statement).scalars().first()

        if not message:
            logger.debug(f"Message {message_id} not found")

        return message

    @staticmethod
    async def get_conversation_messages(
        db: Session,
        conversation_id: UUID,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> tuple[List[Message], int]:
        """Get messages from a conversation with pagination.

        Messages ordered by creation time (oldest first) for agent context.

        Args:
            db: Database session
            conversation_id: Conversation ID
            limit: Max messages to retrieve
            offset: Pagination offset
            include_deleted: Whether to include soft-deleted messages

        Returns:
            Tuple of (messages list, total count)

        Raises:
            Exception: If database operation fails
        """
        filters = [Message.conversation_id == conversation_id]
        if not include_deleted:
            filters.append(Message.deleted_at.is_(None))

        # Count total messages
        count_statement = select(Message).where(and_(*filters))
        all_messages = db.execute(count_statement).scalars().all()
        total_count = len(all_messages)

        # Fetch paginated messages ordered by creation time (oldest first)
        statement = (
            select(Message)
            .where(and_(*filters))
            .order_by(Message.created_at.asc())
            .limit(limit)
            .offset(offset)
        )

        messages = db.execute(statement).scalars().all()

        logger.debug(
            f"Retrieved {len(messages)} messages from conversation {conversation_id} "
            f"(total: {total_count}, limit={limit}, offset={offset})"
        )

        return messages, total_count

    @staticmethod
    async def get_conversation_messages_for_display(
        db: Session,
        conversation_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[List[Message], int]:
        """Get messages for display (newest first).

        Args:
            db: Database session
            conversation_id: Conversation ID
            limit: Max messages to retrieve
            offset: Pagination offset

        Returns:
            Tuple of (messages list ordered newest first, total count)

        Raises:
            Exception: If database operation fails
        """
        # Count total active messages
        count_statement = select(Message).where(
            and_(
                Message.conversation_id == conversation_id,
                Message.deleted_at.is_(None),
            )
        )
        all_messages = db.execute(count_statement).scalars().all()
        total_count = len(all_messages)

        # Fetch messages ordered by creation time (newest first for UI display)
        statement = (
            select(Message)
            .where(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.deleted_at.is_(None),
                )
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        messages = db.execute(statement).scalars().all()
        # Reverse to get oldest first in list for display
        messages.reverse()

        logger.debug(
            f"Retrieved {len(messages)} display messages from conversation {conversation_id} "
            f"(total: {total_count})"
        )

        return messages, total_count

    @staticmethod
    async def soft_delete_conversation_messages(
        db: Session,
        conversation_id: UUID,
    ) -> int:
        """Soft-delete all messages in a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID

        Returns:
            Number of messages deleted

        Raises:
            Exception: If database operation fails
        """
        statement = select(Message).where(
            and_(
                Message.conversation_id == conversation_id,
                Message.deleted_at.is_(None),
            )
        )
        messages = db.execute(statement).scalars().all()

        now = datetime.utcnow()
        for message in messages:
            message.deleted_at = now
            db.add(message)

        db.commit()

        logger.info(
            f"Soft-deleted {len(messages)} messages from conversation {conversation_id}"
        )

        return len(messages)
