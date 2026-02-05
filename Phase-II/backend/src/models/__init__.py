# [Task]: T011, [From]: specs/001-task-crud-api/plan.md#Phase-2-Foundational
"""
Models package for SQLModel ORM entities.

Exports:
- User: Authentication user from Better Auth
- Task: Task entity with user relationship
- Base classes and mixins
"""

from .base import User  # noqa: F401
from .task import Task  # noqa: F401

__all__ = ["User", "Task"]
