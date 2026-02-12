# Data Model: Task CRUD Operations

**Feature**: 002-task-crud
**Date**: 2026-02-09
**Status**: Phase 1 Complete

## Overview

This document defines the data entities, relationships, validation rules, and state transitions for task management operations. The data model enforces user-scoped security through foreign key relationships and supports all 5 core CRUD operations.

## Entities

### Task Entity

**Purpose**: Represents a todo item owned by a user

**SQLModel Schema**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Task(SQLModel, table=True):
    """Task entity for todo items"""
    __tablename__ = "tasks"

    # Primary Key
    id: int | None = Field(default=None, primary_key=True)

    # Foreign Key (User Ownership)
    user_id: int = Field(foreign_key="user.id", index=True, nullable=False)

    # Task Content
    title: str = Field(max_length=200, nullable=False)
    description: str | None = Field(default=None, max_length=1000, nullable=True)

    # Task State
    is_completed: bool = Field(default=False, nullable=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

**Database Indexes**:
- Primary key index on `id` (automatic)
- Index on `user_id` for fast user-specific queries
- Composite index on `(user_id, created_at)` for sorted user queries

**Field Descriptions**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | int | PRIMARY KEY, AUTO_INCREMENT | Unique task identifier |
| user_id | int | FOREIGN KEY (user.id), NOT NULL, INDEXED | Owner of the task (enforces data isolation) |
| title | str | NOT NULL, MAX_LENGTH=200 | Task title (required) |
| description | str | NULL, MAX_LENGTH=1000 | Task description (optional) |
| is_completed | bool | NOT NULL, DEFAULT=false | Completion status (false=Pending, true=Completed) |
| created_at | datetime | NOT NULL, DEFAULT=now() | Task creation timestamp (UTC) |
| updated_at | datetime | NOT NULL, DEFAULT=now() | Last update timestamp (UTC) |

---

### User Entity (Reference)

**Purpose**: Represents authenticated users who own tasks

**Note**: User entity is defined in 001-user-auth feature. Included here for relationship reference only.

**Relevant Fields**:
```python
class User(SQLModel, table=True):
    """User entity from authentication system"""
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Relationships

### User → Tasks (One-to-Many)

**Relationship**: One user has many tasks

**Foreign Key**: `tasks.user_id` → `users.id`

**Cascade Behavior**:
- **ON DELETE CASCADE**: When user is deleted, all their tasks are deleted
- **ON UPDATE CASCADE**: When user.id changes (unlikely), task.user_id updates

**SQLModel Relationship** (optional, for ORM convenience):
```python
from sqlmodel import Relationship

class User(SQLModel, table=True):
    # ... existing fields ...
    tasks: list["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    # ... existing fields ...
    user: User = Relationship(back_populates="tasks")
```

**Query Pattern**:
```python
# Get all tasks for a user
tasks = session.exec(
    select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
).all()

# Get user with all their tasks (if using Relationship)
user = session.get(User, user_id)
user_tasks = user.tasks  # Lazy loaded
```

---

## Validation Rules

### Task Creation (POST /api/tasks)

**Required Fields**:
- `title`: Must be provided, cannot be empty string

**Optional Fields**:
- `description`: Can be null or empty string

**Validation Rules**:
1. **Title Length**: 1-200 characters
   - Error: "Title is required" (if empty)
   - Error: "Title must be 200 characters or less" (if >200)

2. **Description Length**: 0-1000 characters
   - Error: "Description must be 1000 characters or less" (if >1000)

3. **User ID**: Must match authenticated user from JWT
   - Automatically set from JWT claims, not user-provided

4. **Initial State**: Always created with `is_completed=false`

**Pydantic Request Model**:
```python
from pydantic import BaseModel, Field, validator

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)

    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title is required')
        return v.strip()
```

---

### Task Update (PUT /api/tasks/{task_id})

**Updatable Fields**:
- `title`: Can be changed
- `description`: Can be changed or set to null

**Non-Updatable Fields**:
- `id`: Immutable
- `user_id`: Immutable (cannot transfer task ownership)
- `is_completed`: Use PATCH /toggle endpoint instead
- `created_at`: Immutable
- `updated_at`: Automatically updated on save

**Validation Rules**:
1. **Title Length**: 1-200 characters (same as creation)
2. **Description Length**: 0-1000 characters (same as creation)
3. **Ownership**: Task must belong to authenticated user
   - Error: 403 Forbidden if user_id doesn't match JWT

**Pydantic Request Model**:
```python
class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)

    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title is required')
        return v.strip()
```

---

### Task Toggle (PATCH /api/tasks/{task_id}/toggle)

**State Transition**:
- `is_completed=false` → `is_completed=true` (Pending → Completed)
- `is_completed=true` → `is_completed=false` (Completed → Pending)

**Validation Rules**:
1. **Ownership**: Task must belong to authenticated user
   - Error: 403 Forbidden if user_id doesn't match JWT
2. **Existence**: Task must exist
   - Error: 404 Not Found if task doesn't exist

**No Request Body**: Toggle is idempotent based on current state

---

### Task Deletion (DELETE /api/tasks/{task_id})

**Validation Rules**:
1. **Ownership**: Task must belong to authenticated user
   - Error: 403 Forbidden if user_id doesn't match JWT
2. **Existence**: Task must exist
   - Error: 404 Not Found if task doesn't exist

**Deletion Behavior**:
- Hard delete (permanent removal from database)
- No soft delete or archive
- No undo functionality

---

## State Transitions

### Task Lifecycle

```
[Created] → is_completed=false (Pending)
    ↓
[Toggle] → is_completed=true (Completed)
    ↓
[Toggle] → is_completed=false (Pending)
    ↓
[Delete] → [Removed from database]
```

**State Diagram**:
```
┌─────────────┐
│   Created   │
│ (Pending)   │
└──────┬──────┘
       │
       ↓
┌─────────────┐      Toggle      ┌─────────────┐
│   Pending   │ ←──────────────→ │  Completed  │
│ (orange)    │                  │  (green)    │
└──────┬──────┘                  └──────┬──────┘
       │                                │
       │          Delete                │
       └────────────┬───────────────────┘
                    ↓
              ┌──────────┐
              │ Deleted  │
              │(permanent)│
              └──────────┘
```

**Valid Transitions**:
- Pending → Completed (toggle checkbox)
- Completed → Pending (toggle checkbox)
- Pending → Deleted (delete action)
- Completed → Deleted (delete action)

**Invalid Transitions**:
- None (all states can transition to any other state)

---

## Pydantic Response Models

### TaskResponse (Single Task)

```python
from pydantic import BaseModel
from datetime import datetime

class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel
```

### TaskListResponse (Multiple Tasks)

```python
class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int
```

---

## Database Migration

**Alembic Migration Script** (pseudo-code):

```python
def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Indexes
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('ix_tasks_user_id_created_at', 'tasks', ['user_id', 'created_at'])

def downgrade():
    op.drop_index('ix_tasks_user_id_created_at', 'tasks')
    op.drop_index('ix_tasks_user_id', 'tasks')
    op.drop_table('tasks')
```

---

## Query Patterns

### List All Tasks for User (with Filter)

```python
# All tasks
tasks = session.exec(
    select(Task)
    .where(Task.user_id == current_user.id)
    .order_by(Task.created_at.desc())
).all()

# Pending tasks only
pending_tasks = session.exec(
    select(Task)
    .where(Task.user_id == current_user.id, Task.is_completed == False)
    .order_by(Task.created_at.desc())
).all()

# Completed tasks only
completed_tasks = session.exec(
    select(Task)
    .where(Task.user_id == current_user.id, Task.is_completed == True)
    .order_by(Task.created_at.desc())
).all()
```

### Create Task

```python
new_task = Task(
    user_id=current_user.id,
    title=task_data.title,
    description=task_data.description,
    is_completed=False,
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
session.add(new_task)
session.commit()
session.refresh(new_task)
return new_task
```

### Toggle Task Completion

```python
task = session.get(Task, task_id)
if not task or task.user_id != current_user.id:
    raise HTTPException(status_code=404, detail="Task not found")

task.is_completed = not task.is_completed
task.updated_at = datetime.utcnow()
session.add(task)
session.commit()
session.refresh(task)
return task
```

### Update Task

```python
task = session.get(Task, task_id)
if not task or task.user_id != current_user.id:
    raise HTTPException(status_code=404, detail="Task not found")

task.title = task_data.title
task.description = task_data.description
task.updated_at = datetime.utcnow()
session.add(task)
session.commit()
session.refresh(task)
return task
```

### Delete Task

```python
task = session.get(Task, task_id)
if not task or task.user_id != current_user.id:
    raise HTTPException(status_code=404, detail="Task not found")

session.delete(task)
session.commit()
return {"message": "Task deleted successfully"}
```

---

## Data Integrity Constraints

1. **Foreign Key Constraint**: tasks.user_id → users.id (CASCADE on delete)
2. **NOT NULL Constraints**: id, user_id, title, is_completed, created_at, updated_at
3. **Length Constraints**: title (200 chars), description (1000 chars)
4. **Default Values**: is_completed=false, created_at=now(), updated_at=now()
5. **User Isolation**: All queries MUST filter by user_id from JWT

---

## Summary

- **2 Entities**: Task (new), User (from 001-user-auth)
- **1 Relationship**: User → Tasks (one-to-many)
- **5 Operations**: Create, Read (with filter), Update, Toggle, Delete
- **User-Scoped Security**: Foreign key + query filtering ensures 100% data isolation
- **Validation**: Title required (1-200 chars), description optional (0-1000 chars)
- **State Management**: Boolean flag for completion status (Pending/Completed)
- **Performance**: Indexed queries support 1000+ tasks without degradation
