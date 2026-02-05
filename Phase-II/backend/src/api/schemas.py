# [Task]: T005, [From]: specs/001-task-crud-api/spec.md#Request/Response-Schemas
# [From]: specs/001-task-crud-api/plan.md#Phase-2-Foundational
"""
Pydantic models for request/response validation.

Provides:
- TaskCreate: POST request body validation
- TaskUpdate: PUT request body validation (all fields required)
- TaskPatch: PATCH request body validation (all fields optional)
- TaskResponse: Task object response model
- PaginatedResponse: Paginated list response model
- ErrorResponse: Error response model
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field


class TaskPriorityEnum(str, Enum):
    """Task priority levels for API."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCreate(BaseModel):
    """Request schema for creating a new task."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Task title (required, 1-255 characters)",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Task description (optional, max 2000 characters)",
    )
    due_date: Optional[datetime] = Field(
        default=None,
        alias="dueDate",
        description="Task due date (optional, ISO 8601 format)",
    )
    priority: Optional[str] = Field(
        default="medium",
        description="Task priority level (optional, default: medium) - low, medium, or high",
    )
    tags: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Comma-separated task tags (optional, max 500 characters)",
    )

    model_config = {"populate_by_name": True}


class TaskUpdate(BaseModel):
    """Request schema for updating a task (PUT - all fields required)."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Task title (required, 1-255 characters)",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Task description (optional, max 2000 characters)",
    )
    due_date: Optional[datetime] = Field(
        default=None,
        alias="dueDate",
        description="Task due date (optional, ISO 8601 format)",
    )
    priority: str = Field(
        default="medium",
        description="Task priority level - low, medium, or high",
    )
    tags: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Comma-separated task tags (optional, max 500 characters)",
    )
    completed: bool = Field(
        default=False,
        description="Task completion status",
    )

    model_config = {"populate_by_name": True}


class TaskPatch(BaseModel):
    """Request schema for partial update (PATCH - all fields optional)."""

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Task title (optional, 1-255 characters)",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Task description (optional, max 2000 characters)",
    )
    due_date: Optional[datetime] = Field(
        default=None,
        alias="dueDate",
        description="Task due date (optional, ISO 8601 format)",
    )
    priority: Optional[str] = Field(
        default=None,
        description="Task priority level (optional) - low, medium, or high",
    )
    tags: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Comma-separated task tags (optional, max 500 characters)",
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Task completion status (optional)",
    )

    model_config = {"populate_by_name": True}


class TaskComplete(BaseModel):
    """Request schema for toggling task completion."""

    completed: bool = Field(
        ...,
        description="Set to true to mark complete, false to mark incomplete",
    )


class TaskResponse(BaseModel):
    """Response schema for task object."""

    id: UUID = Field(..., description="Unique task ID")
    user_id: UUID = Field(..., description="User who owns this task")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    due_date: Optional[datetime] = Field(default=None, description="Task due date")
    priority: str = Field(default="medium", description="Task priority level")
    tags: Optional[str] = Field(default=None, description="Comma-separated task tags")
    completed: bool = Field(default=False, description="Completion status")
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when task was completed",
    )
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last update timestamp")

    model_config = {
        "from_attributes": True,
    }


class PaginationMetadata(BaseModel):
    """Pagination metadata for list responses."""

    limit: int = Field(..., description="Number of items per page")
    offset: int = Field(..., description="Current page offset")
    total: int = Field(..., description="Total number of items")
    has_more: bool = Field(..., description="Whether more items exist")


class PaginatedResponse(BaseModel):
    """Paginated list response model."""

    items: List[TaskResponse] = Field(default_factory=list, description="List items")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")


class ErrorDetail(BaseModel):
    """Error response detail."""

    code: str = Field(..., description="Error code (e.g., UNAUTHORIZED)")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Field-level error details (for 422 validation errors)",
    )


T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]):
    """Success response wrapper."""

    data: T = Field(..., description="Response data")
    error: None = Field(default=None, description="Error (null on success)")


class ErrorResponse(BaseModel):
    """Error response wrapper."""

    data: None = Field(default=None, description="Data (null on error)")
    error: ErrorDetail = Field(..., description="Error details")


class SignupRequest(BaseModel):
    """Request schema for user signup."""

    email: str = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        description="User password (minimum 8 characters)",
    )


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """Response schema for user object."""

    id: str = Field(..., description="Unique user ID")
    email: str = Field(..., description="User email address")
    name: Optional[str] = Field(default=None, description="User full name")
    createdAt: Optional[str] = Field(default=None, description="Account creation timestamp")


class AuthResponse(BaseModel):
    """Response schema for authentication endpoints."""

    user: UserResponse = Field(..., description="Authenticated user")
    token: str = Field(..., description="JWT authentication token")
    expiresIn: int = Field(default=86400, description="Token expiration time in seconds")
