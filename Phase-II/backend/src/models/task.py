# [Task]: T002, [From]: specs/001-task-crud-api/spec.md#Key-Entities
# [From]: specs/001-task-crud-api/plan.md#Phase-2-Foundational
"""
Task model representing user's to-do items.

Provides:
- Task SQLModel with all required fields per spec
- Validation rules (title required, length constraints)
- Foreign key relationship to User
- Indexes for efficient queries
- Completion tracking with optional completed_at timestamp
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(SQLModel, table=True):
    """Task entity representing a user's to-do item.

    Each task belongs to a single user and includes:
    - Title (required, 1-255 chars)
    - Description (optional, max 2000 chars)
    - Due date (optional, ISO 8601 datetime)
    - Completion status with timestamp
    - Automatic created_at and updated_at timestamps
    """

    __tablename__ = "tasks"

    # Primary key and timestamps
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # User relationship (foreign key)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    # Task content
    title: str = Field(
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
        description="Task due date (optional, ISO 8601 format)",
    )

    # Completion tracking
    completed: bool = Field(
        default=False,
        description="Task completion status",
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when task was completed (null if not completed)",
    )

    # Priority and tags
    priority: str = Field(
        default="medium",
        description="Task priority level (low, medium, high)",
    )
    tags: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Comma-separated task tags (e.g., 'work,urgent,review')",
    )

    def __repr__(self) -> str:
        return (
            f"<Task id={self.id} user_id={self.user_id} title={self.title!r} "
            f"completed={self.completed}>"
        )
