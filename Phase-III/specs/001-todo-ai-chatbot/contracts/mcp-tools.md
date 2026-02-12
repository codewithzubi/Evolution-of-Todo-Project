# MCP Tools Contract Specification

**Version**: 1.0.0
**Feature**: Todo AI Chatbot
**Purpose**: Define MCP tools for AI agent to interact with todo operations

## Tool Definitions

### 1. add_task

**Description**: Create a new task for the user

**Parameters**:
```yaml
user_id:
  type: string
  format: uuid
  required: true
  description: Authenticated user's ID from JWT token

title:
  type: string
  required: true
  minLength: 1
  maxLength: 200
  description: Task title extracted from user message

description:
  type: string
  required: false
  maxLength: 2000
  description: Additional task details if provided

due_date:
  type: string
  format: date
  required: false
  description: ISO 8601 date string if user mentions a deadline
```

**Returns**:
```yaml
type: object
properties:
  success:
    type: boolean
  task:
    type: object
    properties:
      id: string (uuid)
      title: string
      description: string
      due_date: string (date)
      status: string (enum: incomplete)
      created_at: string (datetime)
```

**Example**:
```json
// Input
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "buy groceries",
  "due_date": "2026-02-12"
}

// Output
{
  "success": true,
  "task": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "buy groceries",
    "description": null,
    "due_date": "2026-02-12",
    "status": "incomplete",
    "created_at": "2026-02-11T22:00:00Z"
  }
}
```

---

### 2. list_tasks

**Description**: Retrieve user's tasks with optional filtering

**Parameters**:
```yaml
user_id:
  type: string
  format: uuid
  required: true
  description: Authenticated user's ID from JWT token

status:
  type: string
  enum: [complete, incomplete, all]
  required: false
  default: all
  description: Filter tasks by completion status

limit:
  type: integer
  required: false
  default: 50
  minimum: 1
  maximum: 100
  description: Maximum number of tasks to return
```

**Returns**:
```yaml
type: object
properties:
  success:
    type: boolean
  tasks:
    type: array
    items:
      type: object
      properties:
        id: string (uuid)
        title: string
        description: string
        due_date: string (date, nullable)
        status: string (enum: complete, incomplete)
        created_at: string (datetime)
        completed_at: string (datetime, nullable)
  count:
    type: integer
    description: Total number of tasks returned
```

**Example**:
```json
// Input
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "incomplete"
}

// Output
{
  "success": true,
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "buy groceries",
      "description": null,
      "due_date": "2026-02-12",
      "status": "incomplete",
      "created_at": "2026-02-11T22:00:00Z",
      "completed_at": null
    }
  ],
  "count": 1
}
```

---

### 3. complete_task

**Description**: Mark a task as complete or incomplete

**Parameters**:
```yaml
user_id:
  type: string
  format: uuid
  required: true
  description: Authenticated user's ID from JWT token

task_id:
  type: string
  format: uuid
  required: false
  description: Specific task ID if known (mutually exclusive with task_title)

task_title:
  type: string
  required: false
  description: Task title for fuzzy matching if ID not known

mark_complete:
  type: boolean
  required: false
  default: true
  description: True to mark complete, false to mark incomplete
```

**Returns**:
```yaml
type: object
properties:
  success:
    type: boolean
  task:
    type: object
    properties:
      id: string (uuid)
      title: string
      status: string (enum: complete, incomplete)
      completed_at: string (datetime, nullable)
```

**Error Cases**:
```yaml
# Multiple matches found
{
  "success": false,
  "error": "multiple_matches",
  "matches": [
    {"id": "uuid1", "title": "task 1"},
    {"id": "uuid2", "title": "task 2"}
  ],
  "message": "Multiple tasks match 'meeting'. Please be more specific."
}

# Task not found
{
  "success": false,
  "error": "not_found",
  "message": "Task not found"
}
```

**Example**:
```json
// Input
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_title": "buy groceries",
  "mark_complete": true
}

// Output
{
  "success": true,
  "task": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "buy groceries",
    "status": "complete",
    "completed_at": "2026-02-11T22:05:00Z"
  }
}
```

---

### 4. update_task

**Description**: Modify task details (title, description, due date)

**Parameters**:
```yaml
user_id:
  type: string
  format: uuid
  required: true
  description: Authenticated user's ID from JWT token

task_id:
  type: string
  format: uuid
  required: false
  description: Specific task ID if known (mutually exclusive with task_title)

task_title:
  type: string
  required: false
  description: Task title for fuzzy matching if ID not known

new_title:
  type: string
  required: false
  minLength: 1
  maxLength: 200
  description: Updated task title

new_description:
  type: string
  required: false
  maxLength: 2000
  description: Updated task description

new_due_date:
  type: string
  format: date
  required: false
  description: Updated due date (ISO 8601)
```

**Returns**:
```yaml
type: object
properties:
  success:
    type: boolean
  task:
    type: object
    properties:
      id: string (uuid)
      title: string
      description: string
      due_date: string (date, nullable)
      status: string
      updated_at: string (datetime)
```

**Example**:
```json
// Input
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_title": "report",
  "new_due_date": "2026-02-17"
}

// Output
{
  "success": true,
  "task": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "finish report",
    "description": null,
    "due_date": "2026-02-17",
    "status": "incomplete",
    "updated_at": "2026-02-11T22:10:00Z"
  }
}
```

---

### 5. delete_task

**Description**: Remove a task permanently

**Parameters**:
```yaml
user_id:
  type: string
  format: uuid
  required: true
  description: Authenticated user's ID from JWT token

task_id:
  type: string
  format: uuid
  required: false
  description: Specific task ID if known (mutually exclusive with task_title)

task_title:
  type: string
  required: false
  description: Task title for fuzzy matching if ID not known

delete_all_completed:
  type: boolean
  required: false
  default: false
  description: Delete all completed tasks (ignores task_id/task_title)
```

**Returns**:
```yaml
type: object
properties:
  success:
    type: boolean
  deleted_count:
    type: integer
    description: Number of tasks deleted
  message:
    type: string
    description: Confirmation message
```

**Example**:
```json
// Input (single task)
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_title": "grocery"
}

// Output
{
  "success": true,
  "deleted_count": 1,
  "message": "Task 'buy groceries' deleted successfully"
}

// Input (all completed)
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "delete_all_completed": true
}

// Output
{
  "success": true,
  "deleted_count": 5,
  "message": "5 completed tasks deleted successfully"
}
```

---

## Common Error Responses

All tools return consistent error structures:

```yaml
type: object
properties:
  success:
    type: boolean
    example: false
  error:
    type: string
    description: Error code
  message:
    type: string
    description: Human-readable error message
```

**Error Codes**:
- `not_found`: Task not found
- `multiple_matches`: Ambiguous task reference (multiple matches)
- `unauthorized`: User doesn't own the task
- `validation_error`: Invalid parameters
- `database_error`: Database operation failed

**Example Error**:
```json
{
  "success": false,
  "error": "not_found",
  "message": "Task 'nonexistent' not found"
}
```

---

## Security Requirements

1. **User Isolation**: All tools MUST filter by `user_id` from JWT claims
2. **Ownership Validation**: Tools MUST verify user owns the task before operations
3. **Parameter Validation**: All parameters validated via Pydantic models
4. **SQL Injection Prevention**: Use SQLModel parameterized queries only
5. **Error Messages**: Never expose internal details (IDs, stack traces) to agent

---

## Implementation Notes

- Tools wrap existing task service methods (no business logic duplication)
- Fuzzy matching for task_title uses case-insensitive LIKE query
- Multiple matches return error with list of candidates for clarification
- All database operations use async SQLModel methods
- Tool execution errors logged for debugging but sanitized for agent
