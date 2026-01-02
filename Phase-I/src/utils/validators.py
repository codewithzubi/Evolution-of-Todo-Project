from typing import List, Union
import re


def validate_task_title(title: str) -> bool:
    """
    Validate task title.
    Returns True if title is valid, False otherwise.
    """
    if not title or not title.strip():
        return False
    if len(title.strip()) > 200:
        return False
    return True


def validate_task_description(description: str) -> bool:
    """
    Validate task description.
    Returns True if description is valid, False otherwise.
    """
    if description and len(description) > 1000:
        return False
    return True


def validate_task_priority(priority: str) -> bool:
    """
    Validate task priority.
    Returns True if priority is valid, False otherwise.
    """
    if not priority:
        return False
    valid_priorities = ["High", "Medium", "Low"]
    return priority in valid_priorities


def validate_task_tags(tags: List[str]) -> bool:
    """
    Validate task tags.
    Returns True if tags are valid, False otherwise.
    """
    if not tags:
        return True  # Empty tags list is valid

    for tag in tags:
        if not tag or not tag.strip():
            return False
        if len(tag.strip()) > 50:
            return False

    # Check for duplicate tags
    if len(tags) != len(set(tags)):
        return False

    return True


def validate_task_id(task_id: Union[str, int]) -> bool:
    """
    Validate task ID.
    Returns True if task ID is valid, False otherwise.
    """
    try:
        task_id = int(task_id)
        return task_id > 0
    except (ValueError, TypeError):
        return False


def validate_recurring_frequency(frequency: str) -> bool:
    """
    Validate recurring task frequency.
    Returns True if frequency is valid, False otherwise.
    """
    if not frequency:
        return True  # None is valid for non-recurring tasks
    valid_frequencies = ["daily", "weekly", "monthly"]
    return frequency in valid_frequencies


def validate_input_not_empty(input_str: str) -> bool:
    """
    Validate that input string is not empty or just whitespace.
    Returns True if input is valid, False otherwise.
    """
    if not input_str:
        return False
    if not input_str.strip():
        return False
    return True


def sanitize_input(input_str: str) -> str:
    """
    Sanitize input string by stripping leading/trailing whitespace.
    Returns the sanitized string.
    """
    if input_str is None:
        return ""
    return input_str.strip()


def is_valid_date_string(date_str: str) -> bool:
    """
    Check if a date string is in a recognizable format.
    Returns True if the date is valid, False otherwise.
    """
    if not date_str or not date_str.strip():
        return False

    # Import date parsing function from date_utils
    try:
        from .date_utils import validate_date_format
        return validate_date_format(date_str)
    except ImportError:
        # Fallback: basic date validation using regex
        date_pattern = r"\d{1,4}[-/]\d{1,2}[-/]\d{2,4}"
        return bool(re.match(date_pattern, date_str.strip()))