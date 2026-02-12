"""Chat request and response schemas for Phase-III."""
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's natural language message"
    )

    conversation_id: Optional[UUID] = Field(
        None,
        description="Existing conversation ID (omit for new conversation)"
    )


class ChatContext(BaseModel):
    """Context information about the chat operation."""

    tasks_affected: int = Field(
        default=0,
        description="Number of tasks affected by this operation"
    )

    operation: Optional[str] = Field(
        None,
        description="Type of operation performed (create, read, update, delete, complete)"
    )


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    success: bool = Field(
        ...,
        description="Whether the request was successful"
    )

    conversation_id: UUID = Field(
        ...,
        description="Conversation ID for this thread"
    )

    response: str = Field(
        ...,
        description="AI-generated natural language response"
    )

    timestamp: datetime = Field(
        ...,
        description="When the response was generated"
    )

    tools_used: List[str] = Field(
        default_factory=list,
        description="MCP tools invoked during processing"
    )

    context: ChatContext = Field(
        default_factory=ChatContext,
        description="Metadata about operations performed"
    )
