from typing import List, Optional, Dict
from ..models.task import Task
from .storage import StorageManager
from ..utils.validators import validate_task_title, validate_task_description, validate_task_priority, validate_task_tags
from datetime import datetime


class TaskService:
    """
    Task business logic service that handles all task-related operations.
    """

    def __init__(self):
        self.storage = StorageManager()

    def add_task(self, title: str, description: str = "") -> Optional[Task]:
        """
        Create a new task with the given title and description.
        Auto-assigns an incrementing ID.
        Returns the created task or None if validation fails.
        """
        # Validate inputs
        if not validate_task_title(title):
            print(f"Error: Invalid title '{title}'. Title must be non-empty and less than or equal to 200 characters.")
            return None

        if not validate_task_description(description):
            print(f"Error: Description exceeds 1000 characters limit.")
            return None

        # Create a new task with auto-incremented ID
        new_task = Task(
            id=0,  # Will be auto-assigned by storage
            title=title,
            description=description,
            completed=False,
            priority="Medium",  # Default priority
            tags=[],  # Default empty tags list
            due_date=None,  # Default no due date
            recurring=None  # Default no recurring
        )

        # Add to storage and return the task with the assigned ID
        task_id = self.storage.add_task(new_task)
        return self.storage.get_task(task_id)

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Get a task by its ID.
        """
        return self.storage.get_task(task_id)

    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks.
        """
        return self.storage.get_all_tasks()

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by its ID.
        Returns True if the task was deleted, False if not found.
        """
        return self.storage.delete_task(task_id)

    def update_task(self, task_id: int, **updates) -> bool:
        """
        Update a task with the given ID using the provided updates.
        Returns True if the task was updated, False if not found.
        """
        # Validate updates if they're being made
        if 'title' in updates and not validate_task_title(updates['title']):
            print(f"Error: Invalid title '{updates['title']}'. Title must be non-empty and less than or equal to 200 characters.")
            return False

        if 'description' in updates and not validate_task_description(updates['description']):
            print(f"Error: Description exceeds 1000 characters limit.")
            return False

        if 'priority' in updates and not validate_task_priority(updates['priority']):
            print(f"Error: Invalid priority '{updates['priority']}'. Must be one of High, Medium, Low.")
            return False

        if 'tags' in updates and not validate_task_tags(updates['tags']):
            print(f"Error: Invalid tags '{updates['tags']}'. Tags cannot be empty, must be less than 50 chars each, and no duplicates.")
            return False

        return self.storage.update_task(task_id, **updates)

    def toggle_task_completion(self, task_id: int) -> bool:
        """
        Toggle the completion status of a task.
        Returns True if the task status was toggled, False if not found.
        """
        task = self.storage.get_task(task_id)
        if task:
            new_status = not task.completed
            return self.storage.update_task(task_id, completed=new_status)
        return False

    def search_tasks(self, keyword: str) -> List[Task]:
        """
        Search tasks by keyword in title or description.
        """
        return self.storage.search_tasks(keyword)

    def filter_tasks(self, criteria: Dict) -> List[Task]:
        """
        Filter tasks based on the given criteria.
        """
        return self.storage.filter_tasks(criteria)

    def sort_tasks(self, sort_by: str, reverse: bool = False) -> List[Task]:
        """
        Sort tasks by the specified attribute.
        """
        return self.storage.sort_tasks(sort_by, reverse)

    def set_task_priority(self, task_id: int, priority: str) -> bool:
        """
        Set the priority of a task.
        """
        if not validate_task_priority(priority):
            print(f"Error: Invalid priority '{priority}'. Must be one of High, Medium, Low.")
            return False

        return self.storage.update_task(task_id, priority=priority)

    def add_task_tags(self, task_id: int, tags: List[str]) -> bool:
        """
        Add tags to a task.
        """
        if not validate_task_tags(tags):
            print(f"Error: Invalid tags '{tags}'. Tags cannot be empty, must be less than 50 chars each, and no duplicates.")
            return False

        # Get current task to preserve existing tags
        task = self.storage.get_task(task_id)
        if not task:
            return False

        # Combine existing tags with new ones, removing duplicates
        all_tags = list(set(task.tags + tags))
        return self.storage.update_task(task_id, tags=all_tags)

    def set_task_due_date(self, task_id: int, due_date: datetime) -> bool:
        """
        Set the due date of a task.
        """
        return self.storage.update_task(task_id, due_date=due_date)

    def set_task_recurring(self, task_id: int, frequency: str) -> bool:
        """
        Set the recurring frequency of a task.
        """
        from ..utils.validators import validate_recurring_frequency
        if not validate_recurring_frequency(frequency):
            print(f"Error: Invalid recurring frequency '{frequency}'. Must be one of daily, weekly, monthly, or None.")
            return False

        return self.storage.update_task(task_id, recurring=frequency)