# [Task]: T011, [From]: specs/001-task-crud-api/plan.md#Phase-2-Foundational
"""
Models package for SQLModel ORM entities.

Exports:
- User: Authentication user from Better Auth
- Task: Task entity with user relationship
- Base classes and mixins
"""

# [Task]: T325, [From]: specs/004-ai-chatbot/spec.md#Key-Entities
from .base import User  # noqa: F401
from .conversation import Conversation  # noqa: F401
from .message import Message, MessageRole  # noqa: F401
from .task import Task  # noqa: F401

__all__ = ["User", "Task", "Conversation", "Message", "MessageRole"]
