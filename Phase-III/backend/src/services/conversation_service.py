# [Task]: T325, [From]: specs/004-ai-chatbot/spec.md#FR-009
"""Conversation and Message persistence service.

Handles CRUD operations for conversations and messages.
Retrieves conversation history from database for agent context.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, and_, desc, select

from ..models.conversation import Conversation
from ..models.message import Message, MessageRole

logger = logging.getLogger(__name__)


# [Task]: T325, [From]: specs/004-ai-chatbot/spec.md#FR-009
class ConversationService:
    """Service for conversation CRUD operations."""

    @staticmethod
    async def create_conversation(
        db: Session,
        user_id: UUID,
        title: Optional[str] = None,
    ) -> Conversation:
        """Create a new conversation.

        Args:
            db: Database session
            user_id: User ID (from JWT)
            title: Optional conversation title

        Returns:
            Created Conversation object

        Raises:
            Exception: If database operation fails
        """
        conversation = Conversation(
            user_id=user_id,
            title=title or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        logger.info(f"Created conversation {conversation.id} for user {user_id}")

        return conversation

    @staticmethod
    async def get_conversation(
        db: Session,
        user_id: UUID,
        conversation_id: UUID,
    ) -> Optional[Conversation]:
        """Get a conversation by ID (with user isolation).

        Args:
            db: Database session
            user_id: User ID (from JWT)
            conversation_id: Conversation ID to retrieve

        Returns:
            Conversation object or None if not found

        Raises:
            Exception: If database operation fails
        """
        statement = select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
                Conversation.deleted_at.is_(None),  # Exclude soft-deleted
            )
        )

        conversation = db.execute(statement).scalars().first()

        if not conversation:
            logger.warning(
                f"Conversation {conversation_id} not found or "
                f"user {user_id} doesn't have access"
            )

        return conversation

    @staticmethod
    async def list_conversations(
        db: Session,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[Conversation], int]:
        """List user's conversations (paginated).

        Args:
            db: Database session
            user_id: User ID (from JWT)
            limit: Max results per page
            offset: Pagination offset

        Returns:
            Tuple of (conversations list, total count)

        Raises:
            Exception: If database operation fails
        """
        # Count total
        count_statement = select(Conversation).where(
            and_(
                Conversation.user_id == user_id,
                Conversation.deleted_at.is_(None),
            )
        )
        total = db.execute(count_statement).scalars().all()
        total_count = len(total)

        # Fetch paginated results
        statement = (
            select(Conversation)
            .where(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.deleted_at.is_(None),
                )
            )
            .order_by(desc(Conversation.created_at))
            .limit(limit)
            .offset(offset)
        )

        conversations = db.execute(statement).scalars().all()

        logger.debug(
            f"Listed {len(conversations)} conversations for user {user_id} "
            f"(total: {total_count})"
        )

        return conversations, total_count

    @staticmethod
    async def update_conversation(
        db: Session,
        user_id: UUID,
        conversation_id: UUID,
        title: Optional[str] = None,
    ) -> Optional[Conversation]:
        """Update a conversation (title only).

        Args:
            db: Database session
            user_id: User ID (from JWT)
            conversation_id: Conversation ID to update
            title: New title (optional)

        Returns:
            Updated Conversation or None if not found

        Raises:
            Exception: If database operation fails
        """
        conversation = await ConversationService.get_conversation(db, user_id, conversation_id)

        if not conversation:
            return None

        if title is not None:
            conversation.title = title

        conversation.updated_at = datetime.utcnow()

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        logger.info(f"Updated conversation {conversation_id} for user {user_id}")

        return conversation

    @staticmethod
    async def soft_delete_conversation(
        db: Session,
        user_id: UUID,
        conversation_id: UUID,
    ) -> bool:
        """Soft-delete a conversation.

        Args:
            db: Database session
            user_id: User ID (from JWT)
            conversation_id: Conversation ID to delete

        Returns:
            True if deleted, False if not found

        Raises:
            Exception: If database operation fails
        """
        conversation = await ConversationService.get_conversation(db, user_id, conversation_id)

        if not conversation:
            return False

        conversation.deleted_at = datetime.utcnow()

        db.add(conversation)
        db.commit()

        logger.info(f"Soft-deleted conversation {conversation_id} for user {user_id}")

        return True


# [Task]: T325, [From]: specs/004-ai-chatbot/spec.md#FR-010
class MessageService:
    """Service for message persistence and retrieval."""

    @staticmethod
    async def add_message(
        db: Session,
        conversation_id: UUID,
        user_id: UUID,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Add a message to a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID (for efficient filtering)
            role: Message role ("user", "assistant", "system")
            content: Message text content
            metadata: Optional metadata (tool calls, etc.)

        Returns:
            Created Message object

        Raises:
            Exception: If database operation fails
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            attributes=metadata,
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        logger.debug(
            f"Added message to conversation {conversation_id}: "
            f"role={role}, content_length={len(content)}"
        )

        return message

    @staticmethod
    async def get_conversation_messages(
        db: Session,
        user_id: UUID,
        conversation_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[Message], int]:
        """Get messages from a conversation (paginated, oldest first for agent context).

        [Task]: T325, [From]: specs/004-ai-chatbot/spec.md#FR-010
        Retrieves conversation history in chronological order (oldest → newest)
        for agent context window. Returns both messages and total count.

        Args:
            db: Database session
            user_id: User ID (from JWT, for verification)
            conversation_id: Conversation ID to fetch messages from
            limit: Max messages to retrieve
            offset: Pagination offset

        Returns:
            Tuple of (messages list, total count)

        Raises:
            Exception: If database operation fails
        """
        # Verify user owns this conversation
        conversation = await ConversationService.get_conversation(db, user_id, conversation_id)

        if not conversation:
            logger.warning(
                f"Cannot get messages: conversation {conversation_id} "
                f"not found for user {user_id}"
            )
            return [], 0

        # Count total messages
        count_statement = select(Message).where(Message.conversation_id == conversation_id)
        all_messages = db.execute(count_statement).scalars().all()
        total_count = len(all_messages)

        # Fetch messages in chronological order (oldest first)
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())  # Oldest first for agent context
            .limit(limit)
            .offset(offset)
        )

        messages = db.execute(statement).scalars().all()

        logger.debug(
            f"Retrieved {len(messages)} messages from conversation {conversation_id} "
            f"(total: {total_count})"
        )

        return messages, total_count

    @staticmethod
    async def get_conversation_messages_as_dicts(
        db: Session,
        user_id: UUID,
        conversation_id: UUID,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get conversation messages as dictionaries (for agent context).

        [Task]: T325, [From]: specs/004-ai-chatbot/spec.md#FR-010
        Converts Message objects to dictionaries in OpenAI format.

        Args:
            db: Database session
            user_id: User ID (from JWT)
            conversation_id: Conversation ID
            limit: Max messages to retrieve

        Returns:
            List of message dicts: [{"role": "...", "content": "..."}]

        Raises:
            Exception: If database operation fails
        """
        messages, _ = await MessageService.get_conversation_messages(
            db=db,
            user_id=user_id,
            conversation_id=conversation_id,
            limit=limit,
        )

        return [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            }
            for msg in messages
        ]
