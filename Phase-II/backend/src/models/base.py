# [Task]: T016, [From]: specs/001-task-crud-api/spec.md#Key-Entities
# [From]: specs/001-task-crud-api/plan.md#Phase-2-Foundational
"""
Base model classes and User entity.

Provides:
- Base SQLModel class with common fields (id, created_at, updated_at)
- User model representing authenticated user from Better Auth
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    """Base SQLModel with common fields."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(BaseModel, table=True):
    """User entity from Better Auth.

    Represents an authenticated user in the system.
    """

    __tablename__ = "users"

    email: str = Field(index=True, unique=True, max_length=255)
    name: str = Field(max_length=255)
    password_hash: str = Field(max_length=255)
    image: str | None = Field(default=None, max_length=2048)
    email_verified: bool = Field(default=False)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} name={self.name}>"
