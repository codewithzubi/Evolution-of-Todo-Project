"""Validation utilities for task operations."""


class ValidationError(Exception):
    """Custom exception for validation errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def validate_title(title: str) -> None:
    """Validate task title.

    Args:
        title: Title to validate

    Raises:
        ValidationError: If title is invalid
    """
    if title is None:
        raise ValidationError("Title is required")

    trimmed_title = title.strip()

    if not trimmed_title:
        raise ValidationError("Title cannot be empty")

    if len(trimmed_title) == 0:
        raise ValidationError("Title cannot be whitespace")


def validate_task_id(task_id: int) -> None:
    """Validate task ID.

    Args:
        task_id: Task ID to validate

    Raises:
        ValidationError: If task ID is invalid
    """
    if task_id <= 0:
        raise ValidationError(f"Task ID must be positive integer")


def validate_update_fields(title: str = None, description: str = None) -> None:
    """Validate that at least one field is provided for update.

    Args:
        title: New title (optional)
        description: New description (optional)

    Raises:
        ValidationError: If no fields are provided
    """
    if title is None and description is None:
        raise ValidationError("At least title or description must be provided")
