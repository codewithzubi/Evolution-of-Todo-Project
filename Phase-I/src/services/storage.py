from typing import Dict, List, Optional
from ..models.task import Task


class StorageManager:
    """
    In-memory storage manager for tasks.
    Uses a dictionary to store tasks with task ID as the key for O(1) lookup.
    """

    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1

    def add_task(self, task: Task) -> int:
        """
        Add a new task to storage.
        If the task ID is 0 or negative, assign an auto-incremented ID.
        """
        if task.id <= 0:
            task.id = self._next_id
            self._next_id += 1

        self._tasks[task.id] = task

        # Update next_id if the added task ID is higher
        if task.id >= self._next_id:
            self._next_id = task.id + 1

        return task.id

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by its ID."""
        return self._tasks.get(task_id)

    def update_task(self, task_id: int, **updates) -> bool:
        """
        Update a task with the given ID using the provided updates.
        Returns True if the task was updated, False if the task was not found.
        """
        if task_id not in self._tasks:
            return False

        task = self._tasks[task_id]

        # Apply updates
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)

        return True

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by its ID.
        Returns True if the task was deleted, False if the task was not found.
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        return list(self._tasks.values())

    def search_tasks(self, keyword: str) -> List[Task]:
        """
        Search tasks by keyword in title or description.
        Returns a list of tasks that contain the keyword (case-insensitive).
        """
        if not keyword:
            return []

        keyword = keyword.lower()
        matching_tasks = []

        for task in self._tasks.values():
            if (keyword in task.title.lower() or
                (task.description and keyword in task.description.lower())):
                matching_tasks.append(task)

        return matching_tasks

    def filter_tasks(self, criteria: Dict) -> List[Task]:
        """
        Filter tasks based on the given criteria.
        Criteria can include: status (completed/incomplete), priority, tags.
        """
        filtered_tasks = []

        for task in self._tasks.values():
            match = True

            # Filter by status (completed)
            if 'status' in criteria:
                if criteria['status'] == 'completed' and not task.completed:
                    match = False
                elif criteria['status'] == 'incomplete' and task.completed:
                    match = False

            # Filter by priority
            if 'priority' in criteria:
                if task.priority != criteria['priority']:
                    match = False

            # Filter by tags
            if 'tags' in criteria and isinstance(criteria['tags'], list):
                # Check if task has all specified tags
                for tag in criteria['tags']:
                    if tag not in task.tags:
                        match = False
                        break

            if match:
                filtered_tasks.append(task)

        return filtered_tasks

    def sort_tasks(self, sort_by: str, reverse: bool = False) -> List[Task]:
        """
        Sort tasks by the specified attribute.
        Supported sort attributes: 'due_date', 'priority', 'title'.
        """
        if sort_by not in ['due_date', 'priority', 'title']:
            raise ValueError(f"Invalid sort attribute: {sort_by}")

        def sort_key(task):
            value = getattr(task, sort_by)
            # Handle None values for due_date by using a very early date
            if sort_by == 'due_date' and value is None:
                from datetime import datetime
                return datetime.min
            return value

        return sorted(self._tasks.values(), key=sort_key, reverse=reverse)