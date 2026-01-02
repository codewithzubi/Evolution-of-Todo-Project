from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Task:
    """
    Represents a single task with all required attributes.

    Attributes:
        id: Auto-incrementing unique identifier for each task
        title: The title or name of the task (required, non-empty)
        description: Detailed description of the task (optional)
        completed: Status indicating if the task is completed (default: False)
        priority: Priority level of the task (High/Medium/Low, default: Medium)
        tags: List of tags/categories associated with the task (default: empty list)
        due_date: Date and time when the task is due (default: None)
        recurring: Frequency pattern for recurring tasks (daily/weekly/monthly/None, default: None)
    """
    id: int
    title: str
    description: str = ""
    completed: bool = False
    priority: str = "Medium"
    tags: List[str] = field(default_factory=list)
    due_date: Optional[datetime] = None
    recurring: Optional[str] = None

    def __post_init__(self):
        """Validate the task attributes after initialization."""
        # Validate title
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty or only whitespace")
        if len(self.title) > 200:
            raise ValueError("Title must be less than or equal to 200 characters")

        # Validate description
        if self.description and len(self.description) > 1000:
            raise ValueError("Description must be less than or equal to 1000 characters")

        # Validate priority
        valid_priorities = ["High", "Medium", "Low"]
        if self.priority not in valid_priorities:
            raise ValueError(f"Priority must be one of {valid_priorities}")

        # Validate tags
        if self.tags:
            for tag in self.tags:
                if not tag or not tag.strip():
                    raise ValueError("Tags cannot be empty or only whitespace")
                if len(tag) > 50:
                    raise ValueError("Each tag must be less than or equal to 50 characters")

            # Check for duplicate tags
            if len(self.tags) != len(set(self.tags)):
                raise ValueError("No duplicate tags allowed in the list")

        # Validate recurring
        if self.recurring and self.recurring not in ["daily", "weekly", "monthly"]:
            raise ValueError("Recurring must be one of 'daily', 'weekly', 'monthly', or None")