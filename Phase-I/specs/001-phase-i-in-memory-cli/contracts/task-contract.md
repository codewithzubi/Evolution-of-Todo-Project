# Task Entity Contract

**Phase**: I
**Branch**: `001-phase-i-in-memory-cli`
**Date**: 2025-12-28

---

## Overview

This contract defines the Task entity interface for Phase-I in-memory todo application. The contract specifies Task structure, behavior, validation rules, and usage patterns.

---

## Entity Structure

### Task Object

```
Task {
    id: int,
    title: str,
    description: str,
    completed: bool
}
```

### Field Specifications

| Field | Type | Required | Mutable | Default | Constraints |
|-------|------|----------|----------|------------|
| id | int | No | No (auto-generated) | Positive integer, unique |
| title | str | Yes | None (must provide) | Non-empty, not whitespace-only |
| description | str | No | Empty string | Any value accepted |
| completed | bool | No | False | True or False only |

---

## Behavior Specification

### Creation Behavior

**Input**: title (required), description (optional)

**Output**: Task object with:
- id: Auto-generated unique positive integer
- title: Provided title (whitespace trimmed)
- description: Provided description or empty string
- completed: False

**Validation**:
- Title must not be empty after whitespace trim
- Title must not be whitespace-only after trim
- Description may be any value (including empty or whitespace)

**Example**:
```
Input: title="Buy groceries", description="Milk, eggs, bread"
Output: Task(id=1, title="Buy groceries", description="Milk, eggs, bread", completed=False)
```

### Update Behavior

**Input**: task_id (required), title (optional), description (optional)

**Output**: Updated Task object with:
- id: Unchanged
- title: New value if provided, unchanged otherwise (whitespace trimmed)
- description: New value if provided, unchanged otherwise
- completed: Unchanged

**Validation**:
- Task with task_id must exist
- If title provided: must not be empty after whitespace trim
- If title provided: must not be whitespace-only after trim
- If description provided: any value accepted
- At least one of title or description must be provided

**Example**:
```
Input: task_id=2, title="Buy snacks", description=not provided
Output: Task(id=2, title="Buy snacks", description="Milk, eggs, bread", completed=False)
```

### Deletion Behavior

**Input**: task_id (required)

**Output**: None (task removed)

**Validation**:
- Task with task_id must exist
- Task ID is not reused after deletion

**Example**:
```
Input: task_id=3
Output: None (task with ID 3 removed from storage)
```

### Completion Behavior

**Input**: task_id (required), status (required, True/False or "toggle")

**Output**: Updated Task object with:
- id: Unchanged
- title: Unchanged
- description: Unchanged
- completed: New status value

**Validation**:
- Task with task_id must exist
- Status must be True or False (for complete/incomplete commands)
- Toggle flips current status (True becomes False, False becomes True)

**Example (Complete)**:
```
Input: task_id=1, status=True
Output: Task(id=1, title="Buy groceries", description="Milk, eggs, bread", completed=True)
```

**Example (Incomplete)**:
```
Input: task_id=1, status=False
Output: Task(id=1, title="Buy groceries", description="Milk, eggs, bread", completed=False)
```

**Example (Toggle)**:
```
Input: task_id=1, status="toggle"
Before: Task(id=1, completed=False)
Output: Task(id=1, completed=True)
```

---

## Validation Rules

### Field-Level Validation

#### id Validation

- Type must be int
- Value must be greater than 0
- Value must be unique within session

#### title Validation

- Type must be str
- Length must be greater than 0
- After whitespace trim: length must be greater than 0
- All Unicode characters allowed

#### description Validation

- Type must be str
- No length restrictions
- Any Unicode characters allowed
- Can be empty string
- Can be whitespace-only

#### completed Validation

- Type must be bool
- Value must be True or False

### Operation-Level Validation

#### Creation Validation

| Condition | Validation | Error Message |
|-----------|------------|--------------|
| Title is None or not provided | Required field | "Error: Title is required" |
| Title is empty string | Non-empty | "Error: Title cannot be empty" |
| Title is whitespace-only | Not whitespace | "Error: Title cannot be whitespace" |

#### Update Validation

| Condition | Validation | Error Message |
|-----------|------------|--------------|
| Task ID not found | Exists | "Error: Task with ID <id> not found" |
| Both title and description not provided | At least one field | "Error: At least title or description must be provided" |
| Title provided is empty | Non-empty | "Error: Title cannot be empty" |
| Title provided is whitespace-only | Not whitespace | "Error: Title cannot be whitespace" |

#### Deletion Validation

| Condition | Validation | Error Message |
|-----------|------------|--------------|
| Task ID not found | Exists | "Error: Task with ID <id> not found" |

#### Completion Validation

| Condition | Validation | Error Message |
|-----------|------------|--------------|
| Task ID not found | Exists | "Error: Task with ID <id> not found" |

---

## Error Taxonomy

| Error Code | Error Message | Category | Severity |
|-----------|--------------|----------|----------|
| ERR-001 | Title is required | Required Field | Fatal |
| ERR-002 | Title cannot be empty | Validation | Fatal |
| ERR-003 | Title cannot be whitespace | Validation | Fatal |
| ERR-004 | Task with ID <id> not found | Not Found | Fatal |
| ERR-005 | At least title or description must be provided | Required Field | Fatal |

---

## Output Format

### Task Display Format

For task list output, each Task is displayed in following format:

```
[<id>] <status> <title>
    <description>
```

Where:
- `<id>` is task ID
- `<status>` is `[COMPLETED]` or `[INCOMPLETE]`
- `<title>` is task title
- `<description>` is task description (omitted if empty)

### Examples

#### Task with Description

```
[1] [INCOMPLETE] Buy groceries
    Milk, eggs, bread
```

#### Task without Description

```
[2] [COMPLETED] Call Mom
```

---

## Invariants

1. **ID Uniqueness**: Each task ID is unique within application session
2. **ID Permanence**: Task IDs are never reused after deletion
3. **ID Immutability**: Task ID cannot be changed after creation
4. **Title Non-Empty**: Title is never empty or whitespace-only in valid Task
5. **Type Safety**: All fields maintain their specified types
6. **Completion Boolean**: Completed field is always True or False

---

## Performance Expectations

- Creation: O(1) - ID generation and dictionary insertion
- Retrieval by ID: O(1) - Dictionary lookup
- Retrieval all: O(n) - Iteration over all values
- Update: O(1) - Dictionary lookup and field assignment
- Deletion: O(1) - Dictionary lookup and deletion

---

## Future Considerations

### Phase-II: Persistence

Contract remains compatible with file-based persistence:
- Task structure serializable to JSON
- Validation rules identical
- ID generation strategy identical

### Phase-III: REST API

Contract provides clear data model for API:
- Task object maps to JSON resource
- Validation rules apply to API payloads
- Error messages suitable for HTTP responses

---

## Compliance

### Specification Alignment

- FR-002: Unique auto-incremented ID starting from 1
- FR-009: Title non-empty and not whitespace-only
- FR-010: Existing task IDs maintained after deletion

### Constitutional Alignment

- Data model abstracted for persistence evolution (Phase-II)
- Validation rules portable across presentation layers
- Task entity definition preserved for all phases
