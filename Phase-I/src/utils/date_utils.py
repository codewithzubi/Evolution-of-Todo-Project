from datetime import datetime
from typing import Optional
import re


def parse_date(date_string: str) -> Optional[datetime]:
    """
    Parse a date string into a datetime object.
    Supports various formats like YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, etc.
    Returns None if the string cannot be parsed.
    """
    if not date_string or not date_string.strip():
        return None

    date_string = date_string.strip()

    # Common date formats
    formats = [
        "%Y-%m-%d",      # YYYY-MM-DD
        "%m/%d/%Y",      # MM/DD/YYYY
        "%d/%m/%Y",      # DD/MM/YYYY
        "%m-%d-%Y",      # MM-DD-YYYY
        "%d-%m-%Y",      # DD-MM-YYYY
        "%Y/%m/%d",      # YYYY/MM/DD
        "%B %d, %Y",     # Month DD, YYYY (e.g., January 1, 2023)
        "%d %B %Y",      # DD Month YYYY (e.g., 1 January 2023)
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    # Try to parse using regex for flexible formats
    # Look for patterns like DD/MM/YYYY or MM/DD/YYYY
    date_pattern = r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})"
    match = re.match(date_pattern, date_string)
    if match:
        day, month, year = map(int, match.groups())
        try:
            return datetime(year, month, day)
        except ValueError:
            pass

    # If none of the formats work, return None
    return None


def format_date(date_obj: Optional[datetime]) -> str:
    """
    Format a datetime object into a readable string.
    Returns empty string if date_obj is None.
    """
    if date_obj is None:
        return ""
    return date_obj.strftime("%Y-%m-%d")


def is_overdue(due_date: Optional[datetime]) -> bool:
    """
    Check if a due date is overdue (past due).
    Returns False if due_date is None.
    """
    if due_date is None:
        return False
    return due_date < datetime.now()


def get_next_occurrence(due_date: Optional[datetime], frequency: str) -> Optional[datetime]:
    """
    Calculate the next occurrence date based on the frequency.
    Frequency can be 'daily', 'weekly', or 'monthly'.
    """
    if due_date is None or frequency not in ['daily', 'weekly', 'monthly']:
        return None

    from datetime import timedelta

    if frequency == 'daily':
        return due_date + timedelta(days=1)
    elif frequency == 'weekly':
        return due_date + timedelta(weeks=1)
    elif frequency == 'monthly':
        # For monthly, add 30 days as an approximation
        # For more precise month calculation, a more complex algorithm would be needed
        return due_date + timedelta(days=30)

    return None


def validate_date_format(date_string: str) -> bool:
    """
    Validate if a date string is in a recognizable format.
    Returns True if the date can be parsed, False otherwise.
    """
    return parse_date(date_string) is not None