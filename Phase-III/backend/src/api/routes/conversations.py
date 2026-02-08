# [Task]: T329, T333, T338, [From]: specs/004-ai-chatbot/spec.md#Requirements
"""Conversation CRUD endpoints for chat API.

Provides:
- POST /api/v1/chat/conversations - Create new conversation
- GET /api/v1/chat/conversations - List user's conversations (paginated)
- GET /api/v1/chat/conversations/{conversation_id} - Get conversation details
- DELETE /api/v1/chat/conversations/{conversation_id} - Soft-delete conversation
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session

from ...database import get_db
from ...models.conversation import Conversation
from ...services.conversation_service import ConversationService
from ...services.message_service import MessagePersistenceService
from ..chat_exceptions import ConversationNotFoundError, UnauthorizedConversationAccessError
from ..chat_schemas import (
    ConversationCreateRequest,
    ConversationListResponse,
    ConversationResponse,
    SuccessResponseWrapper,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["conversations"],
)


# [Task]: T329
@router.post("/conversations", response_model=SuccessResponseWrapper)
async def create_conversation(
    request: Request,
    body: ConversationCreateRequest,
    db: Session = Depends(get_db),
) -> SuccessResponseWrapper:
    """Create a new conversation.

    User ID is extracted from JWT token (set by middleware).
    Returns 401 if token is missing or invalid.

    Args:
        request: FastAPI Request object (contains user_id in state)
        body: Conversation creation request
        db: Database session

    Returns:
        SuccessResponseWrapper containing created Conversation

    Raises:
        UnauthorizedException: If JWT token is missing or invalid (401)
    """
    user_id = request.state.user_id

    logger.info(f"Creating conversation for user {user_id}")

    conversation = await ConversationService.create_conversation(
        db=db,
        user_id=user_id,
        title=body.title,
    )

    response_data = ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        message_count=0,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )

    return SuccessResponseWrapper(data=response_data, error=None)


# [Task]: T329, T333
@router.get("/conversations", response_model=SuccessResponseWrapper)
async def list_conversations(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> SuccessResponseWrapper:
    """List user's conversations (paginated, newest first).

    [Task]: T329, [From]: specs/004-ai-chatbot/spec.md#Endpoints
    Lists all active conversations for the authenticated user.
    Returns paginated results ordered by creation date (newest first).

    Args:
        request: FastAPI Request object (contains user_id in state)
        limit: Max results per page (1-100, default 20)
        offset: Pagination offset (default 0)
        db: Database session

    Returns:
        SuccessResponseWrapper containing ConversationListResponse

    Raises:
        UnauthorizedException: If JWT token is missing or invalid (401)
    """
    user_id = request.state.user_id

    logger.info(f"Listing conversations for user {user_id} (limit={limit}, offset={offset})")

    conversations, total = await ConversationService.list_conversations(
        db=db,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )

    # Enrich with message counts
    conversation_responses = []
    for conv in conversations:
        _, message_count = await MessagePersistenceService.get_conversation_messages(
            db=db,
            conversation_id=conv.id,
            limit=1,
        )

        # Get last message timestamp
        messages, _ = await MessagePersistenceService.get_conversation_messages(
            db=db,
            conversation_id=conv.id,
            limit=1,
        )
        last_message_at = messages[-1].created_at if messages else None

        response = ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            message_count=message_count,
            last_message_at=last_message_at,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )
        conversation_responses.append(response)

    list_response = ConversationListResponse(
        conversations=conversation_responses,
        total=total,
        limit=limit,
        offset=offset,
    )

    return SuccessResponseWrapper(data=list_response, error=None)


# [Task]: T329, T333
@router.get("/conversations/{conversation_id}", response_model=SuccessResponseWrapper)
async def get_conversation(
    request: Request,
    conversation_id: UUID,
    db: Session = Depends(get_db),
) -> SuccessResponseWrapper:
    """Get a single conversation by ID.

    [Task]: T329, [From]: specs/004-ai-chatbot/spec.md#Endpoints
    Retrieves conversation metadata including message count and last message timestamp.
    Returns 403 if user doesn't own the conversation.

    Args:
        request: FastAPI Request object (contains user_id in state)
        conversation_id: Conversation ID to retrieve
        db: Database session

    Returns:
        SuccessResponseWrapper containing ConversationResponse

    Raises:
        UnauthorizedException: If JWT token is missing or invalid (401)
        ConversationNotFoundError: If conversation not found (404)
        UnauthorizedConversationAccessError: If user doesn't own conversation (403)
    """
    user_id = request.state.user_id

    logger.info(f"Getting conversation {conversation_id} for user {user_id}")

    conversation = await ConversationService.get_conversation(
        db=db,
        user_id=user_id,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise ConversationNotFoundError(str(conversation_id))

    # Get message count and last message timestamp
    _, message_count = await MessagePersistenceService.get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
        limit=1,
    )

    messages, _ = await MessagePersistenceService.get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
        limit=1,
    )
    last_message_at = messages[-1].created_at if messages else None

    response = ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        message_count=message_count,
        last_message_at=last_message_at,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )

    return SuccessResponseWrapper(data=response, error=None)


# [Task]: T338
@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    request: Request,
    conversation_id: UUID,
    db: Session = Depends(get_db),
):
    """Soft-delete a conversation and cascade to all messages.

    [Task]: T338, [From]: specs/004-ai-chatbot/spec.md#Endpoints
    Soft-deletes the conversation by setting deleted_at timestamp.
    Cascades soft-delete to all messages in the conversation.
    Returns 403 if user doesn't own the conversation.

    Args:
        request: FastAPI Request object (contains user_id in state)
        conversation_id: Conversation ID to delete
        db: Database session

    Returns:
        None (204 No Content)

    Raises:
        UnauthorizedException: If JWT token is missing or invalid (401)
        ConversationNotFoundError: If conversation not found (404)
        UnauthorizedConversationAccessError: If user doesn't own conversation (403)
    """
    user_id = request.state.user_id

    logger.info(f"Deleting conversation {conversation_id} for user {user_id}")

    # Verify conversation exists and belongs to user
    conversation = await ConversationService.get_conversation(
        db=db,
        user_id=user_id,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise ConversationNotFoundError(str(conversation_id))

    # Soft-delete conversation
    success = await ConversationService.soft_delete_conversation(
        db=db,
        user_id=user_id,
        conversation_id=conversation_id,
    )

    if not success:
        raise ConversationNotFoundError(str(conversation_id))

    # Soft-delete all messages in conversation
    await MessagePersistenceService.soft_delete_conversation_messages(
        db=db,
        conversation_id=conversation_id,
    )

    logger.info(
        f"Successfully deleted conversation {conversation_id} and all its messages for user {user_id}"
    )
