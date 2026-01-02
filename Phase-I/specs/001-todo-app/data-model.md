# Data Model: Python Console-based Todo Application

## Overview
This document defines the data model for the Python console-based Todo application, including entity definitions, relationships, and validation rules.

## Task Entity

### Fields
- **id** (int): Auto-incrementing unique identifier for each task
  - Type: Integer
  - Constraints: Positive integer, auto-generated, unique
  - Required: Yes

- **title** (str): The title or name of the task
  - Type: String
  - Constraints: Maximum 200 characters, non-empty
  - Required: Yes

- **description** (str): Detailed description of the task
  - Type: String
  - Constraints: Maximum 1000 characters
  - Required: No (can be empty)

- **completed** (bool): Status indicating if the task is completed
  - Type: Boolean
  - Default: False
  - Required: Yes

- **priority** (str): Priority level of the task
  - Type: String
  - Values: "High", "Medium", "Low"
  - Default: "Medium"
  - Required: Yes

- **tags** (list[str]): List of tags/categories associated with the task
  - Type: List of strings
  - Constraints: Each tag maximum 50 characters, no duplicates
  - Default: Empty list
  - Required: No

- **due_date** (datetime): Date and time when the task is due
  - Type: datetime object or None
  - Constraints: Must be a valid datetime in the future (for future tasks)
  - Default: None
  - Required: No

- **recurring** (str): Frequency pattern for recurring tasks
  - Type: String or None
  - Values: "daily", "weekly", "monthly", or None
  - Default: None
  - Required: No

### Validation Rules
1. **Title Validation**:
   - Cannot be empty or only whitespace
   - Must be less than or equal to 200 characters

2. **Description Validation**:
   - If provided, must be less than or equal to 1000 characters

3. **Priority Validation**:
   - Must be one of "High", "Medium", or "Low" (case-insensitive)
   - Defaults to "Medium" if not provided

4. **Tags Validation**:
   - Each tag must be less than or equal to 50 characters
   - No duplicate tags allowed in the list
   - All tags must be non-empty after stripping whitespace

5. **Due Date Validation**:
   - If provided, must be a valid datetime object
   - Past due dates are allowed (for overdue tasks)

6. **Recurring Validation**:
   - If provided, must be one of "daily", "weekly", or "monthly" (case-insensitive)
   - If not one of these values, defaults to None

### State Transitions
- **Completion**: A task can transition from incomplete (completed=False) to complete (completed=True) and back
- **Priority Change**: Priority can be changed from any valid value to any other valid value
- **Tag Management**: Tags can be added, removed, or modified at any time
- **Due Date**: Can be set, updated, or cleared at any time

### Relationships
- Tasks are independent entities with no direct relationships to other entities
- However, tasks can be grouped logically by tags, priority, or due date for filtering and sorting purposes