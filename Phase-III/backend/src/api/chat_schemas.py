# [Task]: T328, [From]: specs/004-ai-chatbot/spec.md#Requirements
"""Chat endpoint Pydantic models for request/response validation.

Provides:
- ChatRequest: POST request body for sending messages
- ChatResponse: AI response model
- ConversationResponse: Conversation metadata model
- MessageResponse: Single message model
- PaginatedMessagesResponse: Paginated messages response
- ChatErrorResponse: Standardized error response
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# [Task]: T328
class ChatRequest(BaseModel):
    """Request schema for sending a chat message.

    Used for POST /api/v1/chat/conversations/{conversation_id}/messages
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User message content (required, 1-5000 characters)",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional message metadata (e.g., context info, tags)",
    )


# [Task]: T328
class ChatResponse(BaseModel):
    """Response schema for AI assistant message.

    Returned from POST /api/v1/chat/conversations/{conversation_id}/messages
    """
    id: UUID = Field(..., description="Message ID")
    role: str = Field(..., description="Message role (always 'assistant')")
    content: str = Field(..., description="AI response text")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional list of tool calls made by AI",
    )
    tool_results: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional results from tool execution",
    )
    created_at: datetime = Field(..., description="Timestamp when message was created")

    class Config:
        """Pydantic config."""
        from_attributes = True


# [Task]: T329
class ConversationCreateRequest(BaseModel):
    """Request schema for creating a new conversation.

    Used for POST /api/v1/chat/conversations
    """
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Conversation title (optional)",
    )


# [Task]: T329
class ConversationResponse(BaseModel):
    """Response schema for conversation metadata.

    Used for GET /api/v1/chat/conversations/{conversation_id}
    """
    id: UUID = Field(..., description="Conversation ID")
    user_id: UUID = Field(..., description="User ID (conversation owner)")
    title: Optional[str] = Field(default=None, description="Conversation title")
    message_count: int = Field(default=0, description="Number of messages in conversation")
    last_message_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last message in conversation",
    )
    created_at: datetime = Field(..., description="Conversation creation timestamp")
    updated_at: datetime = Field(..., description="Conversation last update timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


# [Task]: T329
class ConversationListResponse(BaseModel):
    """Response schema for paginated conversations list.

    Used for GET /api/v1/chat/conversations
    """
    conversations: List[ConversationResponse] = Field(
        default_factory=list,
        description="List of conversations",
    )
    total: int = Field(..., description="Total number of conversations")
    limit: int = Field(..., description="Pagination limit")
    offset: int = Field(..., description="Pagination offset")


# [Task]: T330
class MessageResponse(BaseModel):
    """Response schema for a single message.

    Used in message list responses and history retrieval.
    """
    id: UUID = Field(..., description="Message ID")
    conversation_id: UUID = Field(..., description="Conversation ID")
    role: str = Field(..., description="Message role (user/assistant/system)")
    content: str = Field(..., description="Message content")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional tool calls made by assistant",
    )
    tool_results: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional tool execution results",
    )
    created_at: datetime = Field(..., description="Message creation timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


# [Task]: T330
class PaginatedMessagesResponse(BaseModel):
    """Response schema for paginated messages list.

    Used for GET /api/v1/chat/conversations/{conversation_id}/messages
    """
    messages: List[MessageResponse] = Field(
        default_factory=list,
        description="List of messages",
    )
    total: int = Field(..., description="Total number of messages")
    limit: int = Field(..., description="Pagination limit")
    offset: int = Field(..., description="Pagination offset")


# [Task]: T328, T331, T336
class ChatErrorResponse(BaseModel):
    """Error response schema for chat API errors.

    Standard error format returned by all chat endpoints.
    """
    error_code: str = Field(..., description="Machine-readable error code")
    error_message: str = Field(..., description="Human-readable error message")
    status_code: int = Field(..., description="HTTP status code")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional additional error details",
    )


# [Task]: T328
class SuccessResponseWrapper(BaseModel):
    """Wrapper for successful API responses following standard format."""
    data: Any = Field(..., description="Response data")
    error: Optional[ChatErrorResponse] = Field(
        default=None,
        description="Error (null for successful responses)",
    )


# [Task]: T328
class ErrorResponseWrapper(BaseModel):
    """Wrapper for error API responses following standard format."""
    data: None = Field(default=None, description="Data (null for errors)")
    error: ChatErrorResponse = Field(..., description="Error details")
