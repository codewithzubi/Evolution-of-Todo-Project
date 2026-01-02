# Architecture Specification: Phase-I In-Memory Todo CLI

**Phase**: I
**Branch**: `001-phase-i-in-memory-cli`
**Date**: 2025-12-28
**Status**: Draft

---

## Overview

This architecture defines the structure for Phase-I in-memory todo command-line application. The design prioritizes clean separation of concerns, testability, and preparation for future evolution to file persistence and distributed systems.

---

## Architectural Principles

### Separation of Concerns

Application layers are strictly separated:
- Presentation Layer: Command-line interface and user interaction
- Business Logic Layer: Task management and validation
- Data Layer: In-memory task storage

### Reusability for Future Phases

Design decisions enable smooth evolution:
- Data model is abstracted, allowing persistence implementation in Phase-II
- Service layer can be adapted for API endpoints in Phase-III
- Command patterns remain consistent across CLI and potential web interfaces

---

## In-Memory Data Storage Model

### Task Storage Structure

Tasks are stored in an in-memory collection with the following characteristics:

- Collection type: Dictionary or list with index-based access
- Key: Task ID (auto-incremented integer starting from 1)
- Value: Task object containing id, title, description, completed
- Lifetime: Application runtime only (data lost on application exit)
- Thread safety: Not required for Phase-I (single-user CLI)

### ID Generation

- IDs are auto-incremented integers
- Sequence starts at 1 and increments by 1 for each new task
- IDs are never reused after task deletion
- ID counter persists for application lifetime

### Data Model

Task entity structure:

```
Task
├── id: int (unique, auto-generated, immutable)
├── title: str (required, non-empty, modifiable)
├── description: str (optional, can be empty, modifiable)
└── completed: bool (defaults to False, modifiable)
```

---

## CLI Interaction Flow

### Application Lifecycle

1. **Startup**:
   - Initialize empty task storage
   - Initialize ID counter to 1
   - Display welcome message
   - Enter command loop

2. **Command Processing**:
   - Read user input from stdin
   - Parse command and arguments
   - Validate command syntax
   - Dispatch to appropriate command handler
   - Execute business logic
   - Display result to user
   - Return to command loop

3. **Shutdown**:
   - User executes exit command or sends termination signal
   - Display farewell message
   - Terminate application (data is not persisted)

### Command Processing Pipeline

```
User Input
    ↓
Parser (extracts command and arguments)
    ↓
Validator (checks syntax and required arguments)
    ↓
Dispatcher (routes to handler)
    ↓
Command Handler (calls service layer)
    ↓
Service Layer (business logic and validation)
    ↓
Data Layer (in-memory operations)
    ↓
Result Formatter (prepares output)
    ↓
User Output
```

### Error Handling Flow

- Syntax errors: Display error and command usage, return to loop
- Validation errors: Display specific error message, return to loop
- Task not found: Display error with task ID, return to loop
- Unexpected errors: Display error message, continue operation if possible

---

## Separation of Concerns

### Layer Responsibilities

#### Presentation Layer (`/src/cli/`)

**Purpose**: Handle user interaction and command execution

**Responsibilities**:
- Parse command-line arguments
- Display formatted output to user
- Display error messages
- Route commands to service layer
- No business logic

**Components**:
- Command parser
- Command dispatcher
- Output formatter
- Error message handler

#### Business Logic Layer (`/src/services/`)

**Purpose**: Implement task management rules and validation

**Responsibilities**:
- Create, read, update, delete tasks
- Manage completion status
- Validate task data (title non-empty, ID exists)
- Enforce business rules
- No presentation logic

**Components**:
- Task service
- Validation logic
- Business rule enforcement

#### Data Layer (`/src/models/` or `/src/storage/`)

**Purpose**: Manage in-memory task storage

**Responsibilities**:
- Store and retrieve tasks
- Generate and manage task IDs
- Query tasks by various criteria (all, by ID, by status)
- No business or presentation logic

**Components**:
- Task data model
- In-memory storage manager
- ID generator

---

## Clean Python Project Structure

### Directory Layout

```
src/
├── __init__.py
├── main.py                 # Application entry point
├── models/
│   ├── __init__.py
│   └── task.py             # Task data model
├── storage/
│   ├── __init__.py
│   └── in_memory_store.py   # In-memory storage implementation
├── services/
│   ├── __init__.py
│   └── task_service.py      # Task management business logic
├── cli/
│   ├── __init__.py
│   ├── commands.py           # Command handler implementations
│   ├── parser.py            # Command-line parser
│   └── formatter.py         # Output formatting
└── utils/
    ├── __init__.py
    └── validators.py        # Validation utilities
```

### Module Responsibilities

#### `main.py`

Application entry point. Responsibilities:
- Initialize application components
- Handle application lifecycle (startup, command loop, shutdown)
- Top-level exception handling

#### `models/task.py`

Task data model definition. Responsibilities:
- Define Task entity structure
- Provide task creation interface
- No business logic

#### `storage/in_memory_store.py`

In-memory storage implementation. Responsibilities:
- Maintain task collection
- Generate task IDs
- Provide CRUD operations
- Query operations (all, by ID, by status)

#### `services/task_service.py`

Task management service. Responsibilities:
- Coordinate storage operations
- Validate task operations
- Enforce business rules
- Provide task CRUD and completion management

#### `cli/commands.py`

Command handlers. Responsibilities:
- Implement each command (create, view, update, delete, complete, etc.)
- Call service layer for operations
- Format results for output
- Handle command-specific errors

#### `cli/parser.py`

Command-line parser. Responsibilities:
- Parse user input into command and arguments
- Validate command syntax
- Extract flags and options

#### `cli/formatter.py`

Output formatter. Responsibilities:
- Format task lists for display
- Format individual tasks for display
- Format error messages
- Format help text

#### `utils/validators.py`

Validation utilities. Responsibilities:
- Validate task titles
- Validate task IDs
- Validate command arguments
- Provide reusable validation logic

---

## Data Flow Examples

### Create Task Flow

```
User: create "Buy groceries" -m "Milk, eggs, bread"
    ↓
Parser: command="create", title="Buy groceries", description="Milk, eggs, bread"
    ↓
Validator: title is non-empty (valid)
    ↓
Handler: calls service.create_task(title="Buy groceries", description="Milk, eggs, bread")
    ↓
Service: validates title, generates ID=1, creates task, stores
    ↓
Storage: saves Task(id=1, title="Buy groceries", description="Milk, eggs, bread", completed=False)
    ↓
Service: returns created task
    ↓
Handler: formats success message
    ↓
User: "Task created with ID 1"
```

### View Task Flow

```
User: view
    ↓
Parser: command="view", filters={}
    ↓
Handler: calls service.get_all_tasks()
    ↓
Service: calls storage.get_all()
    ↓
Storage: returns [task1, task2, task3]
    ↓
Service: returns tasks
    ↓
Handler: formats task list
    ↓
User: "[1] [INCOMPLETE] Buy groceries\n    Milk, eggs, bread\n[2] [COMPLETED] Call Mom\n    ..."
```

---

## Non-Functional Considerations

### Performance

- Task list display must be instantaneous for up to 1000 tasks
- Command execution must complete within 5 seconds for any operation
- Memory usage must be reasonable (no unbounded growth)

### Reliability

- Application must handle invalid input gracefully
- Application must continue operation after errors
- Application must display clear error messages

### Maintainability

- Code must follow PEP 8 style guidelines
- Code must have docstrings for all public functions
- Code must be organized by clear module boundaries

---

## Evolution Path to Future Phases

### Phase-II: File Persistence

- Replace `storage/in_memory_store.py` with file-based storage
- Add serialization/deserialization layer
- Retain service and CLI layers unchanged
- Maintain same Task model

### Phase-III: REST API

- Extract service layer for API use
- Add new presentation layer (REST API)
- Retain CLI as alternative interface
- Maintain same data model and service interface

### Phase-IV: Event-Driven

- Add event publishing to operations
- Retain in-memory or file-based storage as needed
- Maintain service interface with event hooks
- CLI remains as command interface

### Phase-V: Cloud-Native

- Containerize application
- Add observability (logging, metrics)
- Retain core architecture
- Service layer adapts to cloud infrastructure

---

## Constraints and Assumptions

### Constraints

- Storage is strictly in-memory (no files, no databases)
- Single-user application (no user authentication)
- CLI only (no web or graphical interface)
- No external dependencies beyond Python standard library

### Assumptions

- Application runs on Python 3.13+
- System console supports UTF-8 encoding
- User interacts via terminal or command prompt
- Application runs until explicitly exited
