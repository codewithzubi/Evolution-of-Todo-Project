"""Task service layer for business logic."""

from typing import Optional, List

from models.task import Task
from storage.in_memory_store import InMemoryTaskStore
from utils.validators import validate_title, validate_task_id, validate_update_fields, ValidationError


class TaskService:
    """Business logic for task management."""

    def __init__(self, store: InMemoryTaskStore):
        """Initialize task service.

        Args:
            store: In-memory store instance
        """
        self.store = store

    def create_task(self, title: str, description: str = "") -> Task:
        """Create a new task.

        Args:
            title: Task title (required)
            description: Task description (optional)

        Returns:
            Created task with assigned ID

        Raises:
            ValidationError: If title is invalid
        """
        # Trim whitespace from title
        title = title.strip()

        # Validate title
        validate_title(title)

        # Generate unique ID and create task
        task_id = self.store.generate_id()
        task = Task(task_id=task_id, title=title, description=description)

        # Store task
        self.store.add(task)
        return task

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks.

        Returns:
            List of all tasks sorted by ID
        """
        return self.store.get_all()

    def update_task(self, task_id: int, title: str = None, description: str = None) -> Task:
        """Update a task.

        Args:
            task_id: Task ID to update
            title: New title (optional)
            description: New description (optional)

        Returns:
            Updated task

        Raises:
            ValidationError: If task not found or fields invalid
        """
        # Validate task exists
        validate_task_id(task_id)
        task = self.store.get(task_id)
        if task is None:
            raise ValidationError(f"Task with ID {task_id} not found")

        # Validate at least one field provided
        validate_update_fields(title, description)

        # Update fields
        if title is not None:
            title = title.strip()
            validate_title(title)
            task.title = title

        if description is not None:
            task.description = description

        # Store updated task
        self.store.update(task)
        return task

    def delete_task(self, task_id: int) -> Task:
        """Delete a task.

        Args:
            task_id: Task ID to delete

        Returns:
            Deleted task

        Raises:
            ValidationError: If task not found
        """
        validate_task_id(task_id)
        task = self.store.get(task_id)
        if task is None:
            raise ValidationError(f"Task with ID {task_id} not found")

        self.store.delete(task_id)
        return task

    def mark_complete(self, task_id: int) -> Task:
        """Mark a task as completed.

        Args:
            task_id: Task ID to mark complete

        Returns:
            Updated task

        Raises:
            ValidationError: If task not found
        """
        validate_task_id(task_id)
        task = self.store.get(task_id)
        if task is None:
            raise ValidationError(f"Task with ID {task_id} not found")

        task.completed = True
        self.store.update(task)
        return task

    def mark_incomplete(self, task_id: int) -> Task:
        """Mark a task as incomplete.

        Args:
            task_id: Task ID to mark incomplete

        Returns:
            Updated task

        Raises:
            ValidationError: If task not found
        """
        validate_task_id(task_id)
        task = self.store.get(task_id)
        if task is None:
            raise ValidationError(f"Task with ID {task_id} not found")

        task.completed = False
        self.store.update(task)
        return task

    def toggle_task(self, task_id: int) -> Task:
        """Toggle task completion status.

        Args:
            task_id: Task ID to toggle

        Returns:
            Updated task

        Raises:
            ValidationError: If task not found
        """
        validate_task_id(task_id)
        task = self.store.get(task_id)
        if task is None:
            raise ValidationError(f"Task with ID {task_id} not found")

        task.completed = not task.completed
        self.store.update(task)
        return task

    def get_tasks_by_status(self, completed: bool) -> List[Task]:
        """Get tasks filtered by completion status.

        Args:
            completed: True for completed tasks, False for incomplete

        Returns:
            List of filtered tasks sorted by ID
        """
        all_tasks = self.store.get_all()
        return [task for task in all_tasks if task.completed == completed]
