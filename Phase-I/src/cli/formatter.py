"""Output formatting utilities."""

from typing import List

from models.task import Task


def format_task(task: Task) -> str:
    """Format a single task for display.

    Args:
        task: Task to format

    Returns:
        Formatted task string
    """
    status = "COMPLETED" if task.completed else "INCOMPLETE"
    result = f"[{task.id}] [{status}] {task.title}"

    if task.description:
        result += f"\n    {task.description}"

    return result


def format_task_list(tasks: List[Task]) -> str:
    """Format a list of tasks for display.

    Args:
        tasks: List of tasks to format

    Returns:
        Formatted task list string with blank lines between tasks
    """
    if not tasks:
        return ""

    formatted_tasks = [format_task(task) for task in tasks]
    return "\n\n".join(formatted_tasks)
