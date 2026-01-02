# Implementation Tasks: Phase-I In-Memory Todo CLI

**Phase**: I
**Branch**: `001-phase-i-in-memory-cli`
**Date**: 2025-12-28

---

## Overview

This document defines the implementation tasks for Phase-I in-memory todo command-line application. Tasks are organized by dependency order and grouped by user story priorities (P1 first, then P2).

**Task Format**: `- [ ] [TaskID] [P?] [Story?] Description with file path`

**Task ID Convention**: T001, T002, T003, ...
**Parallel Marker**: [P] indicates tasks that can be executed in parallel
**Story Labels**: [US1] through [US5] for user story phases

---

## Task Organization

### Phase 1: Setup
Shared infrastructure and project scaffolding (blocking all other phases)

### Phase 2: Foundational
Blocking prerequisites for all user stories (Task entity, storage, validation)

### Phase 3: User Story 1 - Create and View Tasks (P1)
Core CRUD operations - MVP candidate

### Phase 4: User Story 2 - Mark Tasks as Complete (P1)
Task completion management

### Phase 5: User Story 3 - Update Task Details (P2)
Task modification capabilities

### Phase 6: User Story 4 - Delete Tasks (P2)
Task removal functionality

### Phase 7: User Story 5 - View Filtered Task Lists (P2)
Filtering capabilities

### Phase 8: Polish & Cross-Cutting
Error handling, edge cases, validation, acceptance

---

## Phase 1: Setup

- [X] [T001] Create project directory structure under `/src` including subdirectories: `models/`, `storage/`, `services/`, `cli/`, `utils/`
  - Path: `src/`
  - Completion: All directories created, visible via `tree src` or `ls -R src`

- [X] [T002] [P] Create Task data model file with Task class containing id, title, description, completed fields
  - Path: `src/models/task.py`
  - Completion: Task class defined with proper type hints, includes `__init__`, `__repr__` methods

- [X] [T003] [P] Create in-memory storage module with InMemoryTaskStore class using dictionary for O(1) lookups
  - Path: `src/storage/in_memory_store.py`
  - Completion: InMemoryTaskStore class with add, get, get_all, update, delete, exists methods

- [X] [T004] Create main application entry point with command loop and basic welcome message
  - Path: `src/main.py`
  - Completion: Application runs, displays welcome message, enters command loop, handles EOF gracefully

---

## Phase 2: Foundational

- [X] [T005] [P] Implement task validation utilities with title validation (non-empty, not whitespace-only)
  - Path: `src/utils/validators.py`
  - Completion: validate_title, validate_task_id functions implemented with proper error messages

- [X] [T006] [P] Implement task service layer with business logic for create, retrieve, update, delete operations
  - Path: `src/services/task_service.py`
  - Completion: TaskService class delegating to storage layer, applying validation

- [X] [T007] Implement argparse-based command parser for create, view, update, delete, complete, incomplete, toggle, help commands
  - Path: `src/cli/parser.py`
  - Completion: ArgParser configured with all 8 commands and their arguments

- [X] [T008] Create command handlers module with stub handlers for all 8 CLI commands
  - Path: `src/cli/commands.py`
  - Completion: Handler functions defined for create_cmd, view_cmd, update_cmd, delete_cmd, complete_cmd, incomplete_cmd, toggle_cmd, help_cmd

- [X] [T009] Create output formatter module with format_task, format_task_list functions following contract specifications
  - Path: `src/cli/formatter.py`
  - Completion: Task output matches format `[<id>] [<status>] <title>` with indented description

---

## Phase 3: User Story 1 - Create and View Tasks (P1)

**User Story**: As a user, I want to create tasks and view them so that I can track my todo items.

- [X] [T010] [P] [US1] Implement create command handler to accept title and optional description, validate title, delegate to service layer
  - Path: `src/cli/commands.py` - create_cmd function
  - Completion: create_cmd calls TaskService.create_task, returns created task ID

- [X] [T011] [P] [US1] Implement view command handler to retrieve all tasks, delegate to formatter for output
  - Path: `src/cli/commands.py` - view_cmd function
  - Completion: view_cmd calls TaskService.get_all_tasks, formats and displays task list

- [X] [T012] [US1] Implement TaskService.create_task method to generate auto-incremented ID starting from 1, create Task object, add to storage
  - Path: `src/services/task_service.py`
  - Completion: create_task generates unique ID, validates title, returns Task with completed=False

- [X] [T013] [US1] Implement InMemoryTaskStore.add method to insert Task object with ID key into dictionary
  - Path: `src/storage/in_memory_store.py`
  - Completion: add method stores task at dictionary key = task.id, returns task

- [X] [T014] [US1] Implement InMemoryTaskStore.get_all method to retrieve all tasks as list sorted by ID
  - Path: `src/storage/in_memory_store.py`
  - Completion: get_all returns list of Task objects in ascending ID order

- [X] [T015] [US1] Wire create and view commands to parser and main loop in main.py
  - Path: `src/main.py`
  - Completion: Running `python src/main.py` allows creating tasks with `create <title> [-m <description>]` and viewing with `view`

---

## Phase 4: User Story 2 - Mark Tasks as Complete (P1)

**User Story**: As a user, I want to mark tasks as complete or incomplete so that I can track my progress.

- [X] [T016] [P] [US2] Implement complete command handler to mark task as completed
  - Path: `src/cli/commands.py` - complete_cmd function
  - Completion: complete_cmd validates ID, calls TaskService.mark_complete, returns success message

- [X] [T017] [P] [US2] Implement incomplete command handler to mark task as incomplete
  - Path: `src/cli/commands.py` - incomplete_cmd function
  - Completion: incomplete_cmd validates ID, calls TaskService.mark_incomplete, returns success message

- [X] [T018] [US2] Implement TaskService.mark_complete method to update task.completed to True
  - Path: `src/services/task_service.py`
  - Completion: mark_complete retrieves task by ID, sets completed=True, saves to storage

- [X] [T019] [US2] Implement TaskService.mark_incomplete method to update task.completed to False
  - Path: `src/services/task_service.py`
  - Completion: mark_incomplete retrieves task by ID, sets completed=False, saves to storage

- [X] [T020] [US2] Implement InMemoryTaskStore.update method to modify existing task in dictionary
  - Path: `src/storage/in_memory_store.py`
  - Completion: update method replaces task at dictionary key with updated Task object

- [X] [T021] [US2] Wire complete and incomplete commands to parser and main loop in main.py
  - Path: `src/main.py`
  - Completion: Running `complete <id>` and `incomplete <id>` commands work correctly

---

## Phase 5: User Story 3 - Update Task Details (P2)

**User Story**: As a user, I want to update task title and description so that I can correct mistakes or add details.

- [X] [T022] [P] [US3] Implement update command handler to accept task ID, optional title, optional description
  - Path: `src/cli/commands.py` - update_cmd function
  - Completion: update_cmd validates at least one field provided, calls TaskService.update_task

- [X] [T023] [US3] Implement TaskService.update_task method to modify title, description, or both
  - Path: `src/services/task_service.py`
  - Completion: update_task validates ID exists, validates title if provided, updates fields

- [X] [T024] [US3] Wire update command to parser with --title and --description flags
  - Path: `src/cli/parser.py` - update command configuration
  - Completion: Parser accepts `update <id> --title <title>` and `update <id> --description <description>`

- [X] [T025] [US3] Add validation for update requiring at least one of title or description
  - Path: `src/utils/validators.py` - validate_update_fields function
  - Completion: Validation ensures at least one field provided for update operation

---

## Phase 6: User Story 4 - Delete Tasks (P2)

**User Story**: As a user, I want to delete tasks so that I can remove completed or unwanted items.

- [X] [T026] [P] [US4] Implement delete command handler to remove task by ID
  - Path: `src/cli/commands.py` - delete_cmd function
  - Completion: delete_cmd validates ID exists, calls TaskService.delete_task, returns success message

- [X] [T027] [US4] Implement TaskService.delete_task method to remove task from storage
  - Path: `src/services/task_service.py`
  - Completion: delete_task retrieves task by ID, removes from storage, returns task

- [X] [T028] [US4] Implement InMemoryTaskStore.delete method to remove task from dictionary
  - Path: `src/storage/in_memory_store.py`
  - Completion: delete method removes task at dictionary key, does not reuse ID

- [X] [T029] [US4] Wire delete command to parser and main loop in main.py
  - Path: `src/main.py`
  - Completion: Running `delete <id>` command removes task, ID never reused

---

## Phase 7: User Story 5 - View Filtered Task Lists (P2)

**User Story**: As a user, I want to view only completed or incomplete tasks so that I can focus on specific subsets.

- [X] [T030] [P] [US5] Implement toggle command handler to flip task completion status
  - Path: `src/cli/commands.py` - toggle_cmd function
  - Completion: toggle_cmd validates ID, calls TaskService.toggle_task, returns new status

- [X] [T031] [P] [US5] Implement TaskService.toggle_task method to flip completed status (True→False, False→True)
  - Path: `src/services/task_service.py`
  - Completion: toggle_task retrieves task, flips completed boolean, saves to storage

- [X] [T032] [US5] Implement filtered view functionality for --completed and --incomplete flags
  - Path: `src/cli/commands.py` - view_cmd function update
  - Completion: view_cmd accepts filter flags, filters task list before formatting

- [X] [T033] [US5] Implement TaskService.get_tasks_by_status method to retrieve filtered task list
  - Path: `src/services/task_service.py`
  - Completion: get_tasks_by_status accepts status parameter, returns matching tasks

- [X] [T034] [US5] Wire toggle command and filter flags to parser in main.py
  - Path: `src/cli/parser.py` - view and toggle command configuration
  - Completion: Parser accepts `view --completed`, `view --incomplete`, `toggle <id>`

---

## Phase 8: Polish & Cross-Cutting

- [X] [T035] [P] Implement comprehensive error handling across all command handlers
  - Path: `src/cli/commands.py`
  - Completion: All handlers catch validation errors, display user-friendly error messages with usage

- [X] [T036] [P] Implement help command with general help and command-specific help
  - Path: `src/cli/commands.py` - help_cmd function
  - Completion: help displays all commands, help <command> displays specific command syntax and examples

- [X] [T037] [P] Add edge case handling: view with no tasks displays "No tasks found" message
  - Path: `src/cli/commands.py` - view_cmd function
  - Completion: Empty task list returns informative message with creation hint

- [X] [T038] Add edge case handling: filtered view with no matching tasks displays "No tasks match specified criteria"
  - Path: `src/cli/commands.py` - view_cmd function
  - Completion: Empty filtered results display appropriate message

- [X] [T039] Add edge case handling: duplicate task creation allowed, ID never reused after deletion
  - Path: `src/services/task_service.py` and `src/storage/in_memory_store.py`
  - Completion: create_task always generates new ID, delete does not renumber existing IDs

- [X] [T040] Add whitespace trimming to title on storage in Task creation
  - Path: `src/models/task.py` or `src/services/task_service.py`
  - Completion: Title stripped of leading/trailing whitespace before validation and storage

- [X] [T041] [P] Implement proper error messages matching command contract specifications
  - Path: `src/cli/commands.py` and `src/utils/validators.py`
  - Completion: All error messages match contract: "Error: <description>. Usage: <command-syntax>"

- [X] [T042] [P] Add graceful exit handling for Ctrl+C and EOF signals in main loop
  - Path: `src/main.py`
  - Completion: Application displays "Goodbye!" and exits cleanly on interrupt

---

## Task Dependencies

### Critical Path (Must Execute Sequentially):
T001 → T002 → T005 → T006 → T007 → T008 → T009 → T015 → T021 → T025 → T029 → T034 → T042

### Parallel Execution Groups:
- Group 1: T002, T003, T004 (can run after T001)
- Group 2: T005, T006 (can run after Phase 1)
- Group 3: T010, T011 (can run after T009)
- Group 4: T016, T017 (can run after T021)
- Group 5: T022 (can run after T021)
- Group 6: T026 (can run after T029)
- Group 7: T030, T031 (can run after T034)
- Group 8: T035, T036, T037, T038 (can run after Phase 7)

---

## Completion Checklist

Phase-I implementation is complete when:

- [ ] All 42 tasks are checked off
- [ ] Application runs with `python src/main.py`
- [ ] All 8 commands work: create, view, update, delete, complete, incomplete, toggle, help
- [ ] All validation rules enforced (title non-empty, IDs exist)
- [ ] All error messages match command contract specifications
- [ ] Task display format matches quickstart guide examples
- [ ] Task IDs auto-increment from 1, never reused
- [ ] View filtering works with --completed and --incomplete flags
- [ ] Application exits gracefully on Ctrl+C or EOF

---

## Acceptance Criteria Mapping

### User Story 1: Create and View Tasks
- Tasks: T010, T011, T012, T013, T014, T015
- Acceptance: User can create tasks with title and optional description, view all tasks in formatted output

### User Story 2: Mark Tasks as Complete
- Tasks: T016, T017, T018, T019, T020, T021
- Acceptance: User can mark tasks complete or incomplete, status persists in session

### User Story 3: Update Task Details
- Tasks: T022, T023, T024, T025
- Acceptance: User can update title, description, or both with proper validation

### User Story 4: Delete Tasks
- Tasks: T026, T027, T028, T029
- Acceptance: User can delete tasks, IDs never reused

### User Story 5: View Filtered Task Lists
- Tasks: T030, T031, T032, T033, T034
- Acceptance: User can toggle task status, filter view by completion status

---

## Compliance

### Specification Alignment

- FR-001 to FR-010: Task CRUD requirements covered in US1, US3, US4 tasks
- FR-011 to FR-019: Task completion requirements covered in US2, US5 tasks
- FR-020 to FR-029: CLI interface requirements covered in T007, T008, T009, T036
- SC-001 to SC-011: Success criteria validated in Phase 8 tasks (T035-T042)

### Constitutional Alignment

- Manual coding forbidden: All tasks designed for Claude Code implementation
- Spec-driven development: All tasks derived from specifications and contracts
- AI-native engineering: Tasks leverage Python standard library, no external dependencies
- Phase sequential completion: All tasks strictly Phase-I scope, no future-phase leakage

---

## Next Steps

After all tasks complete:

1. Run acceptance tests: Execute command workflows from quickstart.md
2. Validate against spec.md: Verify all functional requirements met
3. Create ADR for any significant deviations encountered during implementation
4. Execute `/sp.implement` to begin implementation via Claude Code
