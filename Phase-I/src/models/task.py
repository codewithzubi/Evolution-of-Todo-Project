"""Task data model for in-memory todo application."""

from typing import Optional


class Task:
    """Represents a single todo item."""

    def __init__(self, task_id: int, title: str, description: str = "", completed: bool = False):
        """Initialize a Task.

        Args:
            task_id: Unique identifier for the task
            title: Task title (non-empty, not whitespace-only)
            description: Optional task description
            completed: Task completion status
        """
        self.id: int = task_id
        self.title: str = title
        self.description: str = description
        self.completed: bool = completed

    def __repr__(self) -> str:
        """Return string representation of Task."""
        return f"Task(id={self.id}, title={self.title!r}, description={self.description!r}, completed={self.completed})"

    def __eq__(self, other: object) -> bool:
        """Check equality based on task ID."""
        if not isinstance(other, Task):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Return hash based on task ID."""
        return hash(self.id)
