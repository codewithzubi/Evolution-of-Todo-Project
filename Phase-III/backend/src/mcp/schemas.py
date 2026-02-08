"""Pydantic schemas for MCP tool inputs and outputs.

Defines type-safe request/response structures for all MCP tools.
These schemas validate parameters before tool execution and document the tool API.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    """Task status filters."""
    COMPLETED = "completed"
    INCOMPLETE = "incomplete"


# ============================================================================
# Tool Input Schemas
# ============================================================================


class AddTaskInput(BaseModel):
    """Input schema for add_task MCP tool.

    Creates a new task for the authenticated user via Phase-II API.
    Title is required; other fields are optional.
    """
    user_id: UUID = Field(..., description="User ID (extracted from JWT)")
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    priority: Optional[TaskPriority] = Field(TaskPriority.MEDIUM, description="Priority level")
    due_date: Optional[str] = Field(None, description="ISO 8601 due date (e.g., '2026-02-14')")
    tags: Optional[List[str]] = Field(None, description="Task tags/labels")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, butter",
                "priority": "high",
                "due_date": "2026-02-14",
                "tags": ["shopping", "urgent"],
            }
        }


class ListTasksInput(BaseModel):
    """Input schema for list_tasks MCP tool.

    Lists user's tasks with optional filters.
    All filters are optional; if not provided, returns all tasks.
    """
    user_id: UUID = Field(..., description="User ID (extracted from JWT)")
    status: Optional[TaskStatus] = Field(None, description="Filter by status")
    priority: Optional[TaskPriority] = Field(None, description="Filter by priority")
    overdue: Optional[bool] = Field(False, description="Show only overdue tasks")
    limit: int = Field(10, ge=1, le=100, description="Max results per page")
    offset: int = Field(0, ge=0, description="Pagination offset")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "incomplete",
                "priority": "high",
                "overdue": False,
                "limit": 20,
                "offset": 0,
            }
        }


class UpdateTaskInput(BaseModel):
    """Input schema for update_task MCP tool.

    Updates specific fields of an existing task.
    Only provided fields are updated; omitted fields remain unchanged.
    """
    user_id: UUID = Field(..., description="User ID (extracted from JWT)")
    task_id: UUID = Field(..., description="Task ID to update")
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="New title")
    description: Optional[str] = Field(None, max_length=2000, description="New description")
    priority: Optional[TaskPriority] = Field(None, description="New priority")
    due_date: Optional[str] = Field(None, description="New due date (ISO 8601)")
    tags: Optional[List[str]] = Field(None, description="New tags")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "task_id": "660e8400-e29b-41d4-a716-446655440001",
                "priority": "high",
                "due_date": "2026-02-21",
            }
        }


class CompleteTaskInput(BaseModel):
    """Input schema for complete_task MCP tool.

    Marks a task as completed.
    """
    user_id: UUID = Field(..., description="User ID (extracted from JWT)")
    task_id: UUID = Field(..., description="Task ID to complete")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "task_id": "660e8400-e29b-41d4-a716-446655440001",
            }
        }


class DeleteTaskInput(BaseModel):
    """Input schema for delete_task MCP tool.

    Deletes a task permanently.
    Requires explicit confirmation to prevent accidental deletion.
    """
    user_id: UUID = Field(..., description="User ID (extracted from JWT)")
    task_id: UUID = Field(..., description="Task ID to delete")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "task_id": "660e8400-e29b-41d4-a716-446655440001",
            }
        }


# ============================================================================
# Tool Output Schemas
# ============================================================================


class TaskOutput(BaseModel):
    """Task object returned by tools."""
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    priority: TaskPriority
    completed: bool
    completed_at: Optional[datetime]
    due_date: Optional[datetime]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ToolResult(BaseModel):
    """Standard result wrapper for all tool operations."""
    success: bool = Field(..., description="Whether operation succeeded")
    data: Optional[Any] = Field(None, description="Result data if successful")
    error: Optional[str] = Field(None, description="Error message if operation failed")
    message: Optional[str] = Field(None, description="User-friendly message")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": "660e8400-e29b-41d4-a716-446655440001", "title": "Buy groceries"},
                "message": "Task created successfully!",
            }
        }


class ListTasksOutput(BaseModel):
    """Output schema for list_tasks tool."""
    success: bool
    tasks: List[TaskOutput] = Field(default_factory=list)
    total_count: int = Field(0, description="Total number of matching tasks")
    returned_count: int = Field(0, description="Number of tasks returned in this response")
    error: Optional[str] = None
    message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "tasks": [
                    {
                        "id": "660e8400-e29b-41d4-a716-446655440001",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "priority": "high",
                        "completed": False,
                        "completed_at": None,
                        "due_date": "2026-02-14T00:00:00Z",
                        "tags": ["shopping"],
                        "created_at": "2026-02-07T10:00:00Z",
                        "updated_at": "2026-02-07T10:00:00Z",
                    }
                ],
                "total_count": 5,
                "returned_count": 1,
                "message": "Found 5 tasks, returning 1 (high priority only)",
            }
        }
