"""In-memory storage implementation for tasks."""

from typing import Dict, Optional, List

from models.task import Task


class InMemoryTaskStore:
    """In-memory storage for tasks using dictionary for O(1) lookups."""

    def __init__(self):
        """Initialize the in-memory store."""
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, task: Task) -> Task:
        """Add a task to storage.

        Args:
            task: Task object to store

        Returns:
            The stored task
        """
        self._tasks[task.id] = task
        return task

    def get(self, task_id: int) -> Optional[Task]:
        """Get a task by ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            Task if found, None otherwise
        """
        return self._tasks.get(task_id)

    def get_all(self) -> List[Task]:
        """Get all tasks sorted by ID.

        Returns:
            List of all tasks in ascending ID order
        """
        return [self._tasks[task_id] for task_id in sorted(self._tasks.keys())]

    def update(self, task: Task) -> Task:
        """Update an existing task.

        Args:
            task: Task object with updated values

        Returns:
            The updated task
        """
        self._tasks[task.id] = task
        return task

    def delete(self, task_id: int) -> None:
        """Delete a task by ID.

        Args:
            task_id: Task ID to delete

        Note:
            Task IDs are never reused after deletion
        """
        if task_id in self._tasks:
            del self._tasks[task_id]

    def exists(self, task_id: int) -> bool:
        """Check if a task exists.

        Args:
            task_id: Task ID to check

        Returns:
            True if task exists, False otherwise
        """
        return task_id in self._tasks

    def generate_id(self) -> int:
        """Generate a unique task ID.

        Returns:
            New unique task ID
        """
        current_id = self._next_id
        self._next_id += 1
        return current_id
