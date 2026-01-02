# Data Model: Task Entity

**Phase**: I
**Branch**: `001-phase-i-in-memory-cli`
**Date**: 2025-12-28

---

## Overview

This document defines the Task entity for Phase-I in-memory todo application. The Task entity represents a single todo item with a unique identifier, title, optional description, and completion status.

---

## Task Entity

### Definition

The Task entity represents a single todo item with the following structure:

```
Task
├── id: int
├── title: str
├── description: str
└── completed: bool
```

### Field Definitions

#### id: int

**Description**: Unique identifier for the task

**Constraints**:
- Type: Integer
- Auto-generated: Yes
- Starting value: 1
- Increment: +1 for each new task
- Uniqueness: Guaranteed unique within application session
- Mutability: Immutable after creation
- Reuse: Never reused after deletion (no renumbering)

**Validation Rules**:
- Value must be positive integer (greater than 0)
- Value must not be reused from deleted tasks

**Rationale**: Integer IDs are user-friendly for CLI (easy to remember and type). Auto-increment ensures simplicity. No renumbering after deletion maintains stability and consistency with user expectations.

#### title: str

**Description**: Task title or summary

**Constraints**:
- Type: String
- Required: Yes
- Length: No maximum defined (system-dependent)
- Mutability: Modifiable after creation
- Default: None (must be provided on creation)

**Validation Rules**:
- Must not be empty (string length greater than 0)
- Must not be whitespace-only (after stripping, length greater than 0)
- Any Unicode characters allowed (no restrictions)
- Leading/trailing whitespace should be stripped on storage

**Rationale**: Title is primary identifier for users to recognize tasks. Non-empty validation ensures all tasks have meaningful names. Whitespace stripping improves data consistency.

#### description: str

**Description**: Additional details about the task

**Constraints**:
- Type: String
- Required: No
- Length: No maximum defined (system-dependent)
- Mutability: Modifiable after creation
- Default: Empty string ("") or None

**Validation Rules**:
- Can be empty (string length may be 0)
- Can be whitespace-only (allowes for empty descriptions)
- Any Unicode characters allowed (no restrictions)
- Leading/trailing whitespace should be stripped on storage (optional)

**Rationale**: Description provides optional context for tasks. Allowing empty and whitespace-only values supports tasks that need only a title.

#### completed: bool

**Description**: Task completion status

**Constraints**:
- Type: Boolean
- Required: No (has default)
- Mutability: Modifiable after creation
- Default: False (incomplete)

**Validation Rules**:
- Must be True or False only
- No other values accepted

**Rationale**: Completion status enables users to track progress. Defaulting to False (incomplete) aligns with typical todo workflow.

---

## State Transitions

### Task Lifecycle

```
┌─────────────┐
│   Created    │ id assigned, title set,
│   (completed  │ description optional,
│   = False)    │ completed = False
└─────┬───────┘
      │
      ├─── Update title ─────┐
      ├─── Update description ─┤
      └─── Toggle status ─────┤
                           │
                           │
                  ┌──────────┴──────────┐
                  │                     │
         ┌──────────┴───────┐  ┌───┴──────┐
         │ Completed (True)  │  │ Incomplete│
         │                  │  │ (False)   │
         └──────────────────┘  └────────────┘
```

### State Transition Rules

#### Title Updates

- Allowed in any state (completed or incomplete)
- New title must satisfy validation rules (non-empty, not whitespace-only)
- Description and completed status unchanged

#### Description Updates

- Allowed in any state (completed or incomplete)
- Can be set to empty string or whitespace
- Title and completed status unchanged

#### Completion Status Changes

- Three operations supported: set complete, set incomplete, toggle
- Can change between False and True states
- Title and description unchanged

#### Deletion

- Allowed in any state (completed or incomplete)
- Task is permanently removed from storage
- Task ID is not reused (no renumbering)

---

## Data Model Constraints

### In-Memory Storage

- Lifetime: Application runtime only
- Persistence: None (data lost on application exit)
- Access: Direct memory access, no serialization
- Thread Safety: Not required for Phase-I (single-user CLI)

### Scale Considerations

- Target volume: Up to 1000 tasks (from specification)
- Memory requirement: Negligible for 1000 small objects
- Performance: O(1) lookups by ID, O(n) iteration for view-all operations

---

## Validation Rules Summary

### Creation Validation

| Field | Required | Validation | Default |
|-------|----------|------------|---------|
| id | No | Auto-generated, positive integer | 1, 2, 3, ... |
| title | Yes | Non-empty, not whitespace-only | N/A (must provide) |
| description | No | None (any value accepted) | Empty string |
| completed | No | Boolean only | False |

### Update Validation

| Field | Allowed | Validation |
|-------|-----------|------------|
| title | Yes | Non-empty, not whitespace-only |
| description | Yes | None (any value accepted) |
| completed | Yes | Boolean only |

### Operation Validation

| Operation | ID Validation | Other Validation |
|-----------|---------------|------------------|
| Create | N/A | Title must be non-empty |
| View | N/A | N/A |
| Update | ID must exist | Title (if updated) non-empty |
| Delete | ID must exist | N/A |
| Complete | ID must exist | N/A |
| Incomplete | ID must exist | N/A |
| Toggle | ID must exist | N/A |

---

## Example Instances

### Example 1: Task with Title Only

```
Task {
    id: 1,
    title: "Buy groceries",
    description: "",
    completed: False
}
```

### Example 2: Task with Title and Description

```
Task {
    id: 2,
    title: "Call Mom",
    description: "Wish her happy birthday",
    completed: False
}
```

### Example 3: Completed Task

```
Task {
    id: 3,
    title: "Walk dog",
    description: "Morning walk around the park",
    completed: True
}
```

---

## Future Evolution Considerations

### Phase-II: File Persistence

Data model remains unchanged. Considerations for persistence:

- Serialization: Task entity can be serialized to JSON or similar formats
- File format: Single file or per-task files (decision for Phase-II)
- Loading: Task entity deserialization from file

### Phase-III: REST API

Data model remains unchanged. Considerations for API:

- JSON representation: Task entity can be represented as JSON for API responses
- Validation: Field validation rules remain identical
- Versioning: Consider version field if fields change in future phases

### Phase-IV: Event-Driven

Data model remains unchanged. Considerations for events:

- Event payloads: Task entity can be included in event data
- Snapshotting: Task state can be captured in event history

---

## Compliance

### Specification Alignment

- FR-002: Unique auto-incremented ID starting from 1 (Satisfied by id field)
- FR-009: Title non-empty and not whitespace-only (Satisfied by title validation rules)
- FR-010: Existing task IDs maintained after deletion (Satisfied by no renumbering)

### Constitutional Alignment

- Data model abstracted design enables migration to persistence in Phase-II
- Task entity definition (id, title, description, completed) preserved for future phases
- Validation rules portable across presentation layers
