from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import uuid

class Task(SQLModel, table=True):
    """
    Task model representing a user's task with ownership and status.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="pending")  # pending, completed
    user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to User (using string reference to avoid circular import)
    user: "User" = Relationship(back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status}, user_id={self.user_id})>"

# Request/response models for API
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    status: str
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime