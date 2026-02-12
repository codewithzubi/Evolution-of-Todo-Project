# MCP Tools Specification

## Overview

This document defines the 5 MCP (Model Context Protocol) tools that enable the AI agent to perform task management operations. These tools are called by the AI agent based on user intent extracted from natural language.

## Tool Definitions

### 1. add_task

**Purpose**: Create a new task for the user

**Parameters**:
- `user_id` (string, required): The authenticated user's ID
- `title` (string, required): Task title extracted from user message
- `description` (string, optional): Additional task details if provided
- `due_date` (string, optional): ISO 8601 date string if user mentions a deadline

**Returns**:
```json
{
  "success": true,
  "task": {
    "id": "uuid",
    "title": "string",
    "description": "string",
    "due_date": "ISO 8601 date",
    "status": "incomplete",
    "created_at": "ISO 8601 timestamp"
  }
}
```

**Example Usage**:
```
User: "Add a task to buy groceries tomorrow"
Agent calls: add_task(user_id="123", title="buy groceries", due_date="2026-02-12")
```

---

### 2. list_tasks

**Purpose**: Retrieve user's tasks with optional filtering

**Parameters**:
- `user_id` (string, required): The authenticated user's ID
- `status` (string, optional): Filter by "complete" or "incomplete" (default: all)
- `limit` (integer, optional): Maximum number of tasks to return (default: 50)

**Returns**:
```json
{
  "success": true,
  "tasks": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string",
      "due_date": "ISO 8601 date",
      "status": "incomplete",
      "created_at": "ISO 8601 timestamp",
      "completed_at": "ISO 8601 timestamp or null"
    }
  ],
  "count": 10
}
```

**Example Usage**:
```
User: "What tasks do I have?"
Agent calls: list_tasks(user_id="123")

User: "Show me my incomplete tasks"
Agent calls: list_tasks(user_id="123", status="incomplete")
```

---

### 3. complete_task

**Purpose**: Mark a task as complete

**Parameters**:
- `user_id` (string, required): The authenticated user's ID
- `task_id` (string, optional): Specific task ID if known
- `task_title` (string, optional): Task title for fuzzy matching if ID not known

**Returns**:
```json
{
  "success": true,
  "task": {
    "id": "uuid",
    "title": "string",
    "status": "complete",
    "completed_at": "ISO 8601 timestamp"
  }
}
```

**Error Cases**:
```json
{
  "success": false,
  "error": "multiple_matches",
  "matches": [
    {"id": "uuid1", "title": "task 1"},
    {"id": "uuid2", "title": "task 2"}
  ],
  "message": "Multiple tasks match. Please be more specific."
}
```

**Example Usage**:
```
User: "I finished buying groceries"
Agent calls: complete_task(user_id="123", task_title="buy groceries")

User: "Mark task abc-123 as done"
Agent calls: complete_task(user_id="123", task_id="abc-123")
```

---

### 4. update_task

**Purpose**: Modify task details

**Parameters**:
- `user_id` (string, required): The authenticated user's ID
- `task_id` (string, optional): Specific task ID if known
- `task_title` (string, optional): Task title for fuzzy matching if ID not known
- `new_title` (string, optional): Updated task title
- `new_description` (string, optional): Updated task description
- `new_due_date` (string, optional): Updated due date (ISO 8601)

**Returns**:
```json
{
  "success": true,
  "task": {
    "id": "uuid",
    "title": "string",
    "description": "string",
    "due_date": "ISO 8601 date",
    "status": "incomplete",
    "updated_at": "ISO 8601 timestamp"
  }
}
```

**Example Usage**:
```
User: "Change the due date of my report task to next Monday"
Agent calls: update_task(user_id="123", task_title="report", new_due_date="2026-02-17")

User: "Rename the shopping task to grocery shopping"
Agent calls: update_task(user_id="123", task_title="shopping", new_title="grocery shopping")
```

---

### 5. delete_task

**Purpose**: Remove a task permanently

**Parameters**:
- `user_id` (string, required): The authenticated user's ID
- `task_id` (string, optional): Specific task ID if known
- `task_title` (string, optional): Task title for fuzzy matching if ID not known
- `delete_all_completed` (boolean, optional): Delete all completed tasks (default: false)

**Returns**:
```json
{
  "success": true,
  "deleted_count": 1,
  "message": "Task deleted successfully"
}
```

**Example Usage**:
```
User: "Delete the grocery task"
Agent calls: delete_task(user_id="123", task_title="grocery")

User: "Remove all completed tasks"
Agent calls: delete_task(user_id="123", delete_all_completed=true)
```

---

## Error Handling

All tools return consistent error structures:

```json
{
  "success": false,
  "error": "error_code",
  "message": "Human-readable error message"
}
```

**Common Error Codes**:
- `not_found`: Task not found
- `multiple_matches`: Ambiguous task reference
- `unauthorized`: User doesn't own the task
- `validation_error`: Invalid parameters
- `database_error`: Database operation failed

## Security

- All tools validate `user_id` matches authenticated user
- Users can only access their own tasks
- Task IDs are UUIDs to prevent enumeration
- All database queries use parameterized statements
