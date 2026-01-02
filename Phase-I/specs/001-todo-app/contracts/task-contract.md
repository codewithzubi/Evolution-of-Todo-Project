# API Contract: Task Management

## Overview
This document defines the API contracts for the task management functionality in the Python console-based Todo application.

## Task Operations

### Add Task
- **Function**: `add_task(title: str, description: str = "") -> int`
- **Purpose**: Creates a new task with the given title and description
- **Parameters**:
  - `title` (str): Task title (required, non-empty)
  - `description` (str): Task description (optional)
- **Returns**: int (the ID of the newly created task)
- **Side Effects**: Task is added to in-memory storage with auto-generated ID
- **Validation**: Title must be non-empty and <= 200 characters

### Get Task
- **Function**: `get_task(task_id: int) -> Task or None`
- **Purpose**: Retrieves a task by its ID
- **Parameters**:
  - `task_id` (int): Unique identifier of the task
- **Returns**: Task object if found, None otherwise
- **Validation**: task_id must be a positive integer

### Update Task
- **Function**: `update_task(task_id: int, **updates) -> bool`
- **Purpose**: Updates fields of an existing task
- **Parameters**:
  - `task_id` (int): Unique identifier of the task to update
  - `**updates` (kwargs): Fields to update (title, description, completed, priority, tags, due_date, recurring)
- **Returns**: bool (True if update successful, False if task not found)
- **Validation**: Updates must conform to Task entity validation rules

### Delete Task
- **Function**: `delete_task(task_id: int) -> bool`
- **Purpose**: Removes a task from storage
- **Parameters**:
  - `task_id` (int): Unique identifier of the task to delete
- **Returns**: bool (True if deletion successful, False if task not found)
- **Validation**: task_id must be a positive integer

### Get All Tasks
- **Function**: `get_all_tasks() -> list[Task]`
- **Purpose**: Retrieves all tasks from storage
- **Parameters**: None
- **Returns**: List of all Task objects in storage
- **Validation**: None

### Search Tasks
- **Function**: `search_tasks(keyword: str) -> list[Task]`
- **Purpose**: Finds tasks containing the keyword in title or description
- **Parameters**:
  - `keyword` (str): Search term to match against title and description
- **Returns**: List of Task objects matching the keyword
- **Validation**: keyword must be non-empty

### Filter Tasks
- **Function**: `filter_tasks(criteria: dict) -> list[Task]`
- **Purpose**: Filters tasks based on specified criteria
- **Parameters**:
  - `criteria` (dict): Dictionary with filtering options (status, priority, tags, etc.)
- **Returns**: List of Task objects matching the criteria
- **Validation**: Criteria must be valid filtering options

### Sort Tasks
- **Function**: `sort_tasks(sort_by: str, reverse: bool = False) -> list[Task]`
- **Purpose**: Sorts tasks by the specified attribute
- **Parameters**:
  - `sort_by` (str): Attribute to sort by (due_date, priority, title)
  - `reverse` (bool): Whether to sort in descending order (default: False)
- **Returns**: List of Task objects sorted by the specified attribute
- **Validation**: sort_by must be a valid attribute for sorting