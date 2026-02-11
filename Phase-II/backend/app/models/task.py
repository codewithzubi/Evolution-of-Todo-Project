"""Task model for todo items."""
from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID


class Task(SQLModel, table=True):
    """Task entity for todo items."""
    __tablename__ = "tasks"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Key (User Ownership)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)

    # Task Content
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000, nullable=True)
    due_date: Optional[date] = Field(default=None, nullable=True)
    priority: str = Field(default="medium", nullable=False)  # high, medium, low
    tags: Optional[str] = Field(default=None, max_length=500, nullable=True)  # comma-separated

    # Task State
    is_completed: bool = Field(default=False, nullable=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class TaskCreate(SQLModel):
    """Request model for creating a task."""
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    due_date: Optional[date] = Field(default=None)
    priority: str = Field(default="medium")  # high, medium, low
    tags: Optional[str] = Field(default=None, max_length=500)  # comma-separated


class TaskUpdate(SQLModel):
    """Request model for updating a task."""
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    due_date: Optional[date] = Field(default=None)
    priority: Optional[str] = Field(default=None)  # high, medium, low
    tags: Optional[str] = Field(default=None, max_length=500)  # comma-separated


class TaskResponse(SQLModel):
    """Response model for task operations."""
    id: int
    user_id: UUID
    title: str
    description: Optional[str]
    due_date: Optional[date]
    priority: str
    tags: Optional[str]
    is_completed: bool
    created_at: datetime
    updated_at: datetime
