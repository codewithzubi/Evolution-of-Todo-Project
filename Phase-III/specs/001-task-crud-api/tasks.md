---
description: "Task CRUD API implementation tasks for Phase 2 of Evolution of Todo"
---

# Tasks: Task CRUD API

**Input**: Design documents from `/specs/001-task-crud-api/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md (planned), data-model.md (planned), contracts/ (planned)
**Status**: Ready for implementation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

**Format**: `[ID] [P?] [Story] Description with exact file path`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- **File paths**: Include exact backend/ structure from plan

---

## Overview: User Stories & Task Mapping

| User Story | Priority | Goal | Tasks |
|------------|----------|------|-------|
| US1: Create Task | P1 | POST endpoint to create new task | T012-T017 |
| US2: List Tasks | P1 | GET endpoint with pagination & filtering | T018-T023 |
| US3: View Task Detail | P1 | GET endpoint for single task | T024-T027 |
| US4: Update Task | P2 | PUT/PATCH endpoints for full/partial update | T028-T033 |
| US5: Mark Complete | P2 | PATCH endpoint to toggle task completion | T034-T039 |
| US6: Delete Task | P3 | DELETE endpoint for permanent deletion | T040-T043 |

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and FastAPI baseline structure

**Estimated Effort**: Medium complexity (dependencies, configuration, folders)

### Create Project Structure
- [x] T001 Create backend project directory structure: `backend/src/`, `backend/tests/`, `backend/.env.example`

### Initialize FastAPI & Dependencies
- [x] T002 Initialize `backend/pyproject.toml` with FastAPI, SQLModel, pytest, and dependencies
- [x] T003 [P] Create `backend/requirements.txt` pinning all versions (FastAPI, SQLModel, asyncpg, pydantic, python-jose, etc.)
- [x] T004 [P] Create `backend/.env.example` with placeholders: JWT_SECRET, DATABASE_URL, BETTER_AUTH_SECRET

### Setup Tooling & Configuration
- [x] T005 [P] Create `backend/pyproject.toml` with ruff config (line-length 100, target Python 3.11)
- [x] T006 [P] Create `backend/pytest.ini` for test discovery and async support
- [x] T007 [P] Create `backend/Dockerfile` with Python 3.11 base image
- [x] T008 Create `backend/.gitignore` excluding `.env`, `__pycache__`, `.pytest_cache`, etc.

**Checkpoint**: Project skeleton ready - foundational phase can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is 100% complete

### Database & ORM Setup
- [x] T009 Create `backend/src/database.py` with async SQLAlchemy engine, session factory, and Neon connection setup
- [x] T010 [P] Create `backend/src/config.py` for environment variable loading (JWT_SECRET, DATABASE_URL, BETTER_AUTH_SECRET)
- [x] T011 Create `backend/src/models/__init__.py` (empty init for models package)

### JWT Authentication Middleware
- [x] T012 Create `backend/src/api/middleware.py` with FastAPI middleware to:
  - Extract JWT token from `Authorization: Bearer <token>` header
  - Verify JWT signature using JWT_SECRET from config
  - Extract `user_id` claim and set in request state
  - Return 401 Unauthorized if token missing or invalid
  - Return 401 Unauthorized if token expired

### Request/Response Validation Layer
- [x] T013 Create `backend/src/api/schemas.py` with Pydantic models:
  - `TaskCreate` (title required, description optional, due_date optional)
  - `TaskUpdate` (all fields optional for PATCH)
  - `TaskResponse` (all fields including id, user_id, timestamps)
  - `PaginatedResponse` (items: List, pagination: {limit, offset, total, has_more})
  - `ErrorResponse` (code, message, details)

### Base FastAPI Application
- [x] T014 Create `backend/src/main.py` with:
  - FastAPI app initialization
  - Mount JWT middleware
  - Include routers (to be added per story)
  - Global exception handlers for 401, 403, 404, 422, 500
  - Startup/shutdown database connection handlers

### Error Handling & Logging
- [x] T015 [P] Create `backend/src/api/errors.py` with custom exception classes:
  - `UnauthorizedException` (401)
  - `ForbiddenException` (403)
  - `NotFoundException` (404)
  - `ValidationException` (422 with field details)

### Base Models Infrastructure
- [x] T016 Create `backend/src/models/base.py` with:
  - SQLModel base class with common fields (id: UUID, created_at, updated_at)
  - User model (id, email, name from Better Auth)
  - Base validation mixins for all entities

**Checkpoint**: Foundation ready ✅ - all user stories can now be implemented in parallel or sequentially

---

## Phase 3: User Story 1 - Create a New Task (Priority: P1) 🎯 MVP

**Goal**: Enable authenticated users to create new tasks with title, optional description, and due date. Task creation should return full task object with unique ID and timestamps.

**Independent Test**: Authenticated user sends POST /api/{user_id}/tasks with title, receives 201 Created with task object containing id, created_at, updated_at. Unauthenticated request receives 401. Missing title receives 422 with validation error.

### Tests for User Story 1 (Optional but Recommended - TDD Approach)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T017 [P] [US1] Create contract test file `backend/tests/contract/test_create_task.py` with:
  - Test POST request schema matches spec (title required, description optional, due_date optional)
  - Test response schema includes all required fields (id, user_id, created_at, updated_at)
  - Validate status code 201 Created
  - Test 401 Unauthorized for missing JWT token
  - Test 422 Unprocessable Entity for missing title (with field-level error details)

- [ ] T018 [P] [US1] Create integration test file `backend/tests/integration/test_create_task.py` with:
  - Test authenticated user can create task with title only
  - Test authenticated user can create task with title + description + due_date
  - Test task appears in database with correct user_id
  - Test timestamps are set automatically
  - Test different users cannot see each other's created tasks

### Implementation for User Story 1

- [ ] T019 [P] [US1] Create Task model in `backend/src/models/task.py`:
  - Fields: id (UUID), user_id (UUID FK), title (str 1-255), description (str optional max 2000), due_date (datetime optional), completed (bool default False), completed_at (datetime nullable), created_at, updated_at
  - Validation: title required and non-empty, description max 2000, due_date ISO 8601 format
  - Index on (user_id, created_at) for list queries
  - [Task]: T019, [From]: specs/001-task-crud-api/spec.md#Key-Entities

- [ ] T020 [US1] Create TaskService in `backend/src/services/task_service.py`:
  - `create_task(user_id: UUID, title: str, description: Optional[str], due_date: Optional[datetime]) -> Task`
  - Query-level filtering: all queries include `WHERE user_id = user_id`
  - Validate title non-empty, return 422 ValidationException if invalid
  - Set created_at and updated_at to current time automatically
  - Return full Task object
  - [Task]: T020, [From]: specs/001-task-crud-api/spec.md#FR-001

- [ ] T021 [US1] Create POST endpoint in `backend/src/api/tasks.py`:
  - Route: `POST /api/{user_id}/tasks`
  - Require JWT token (401 if missing)
  - Verify JWT user_id matches URL user_id (403 if mismatch)
  - Accept TaskCreate Pydantic model
  - Call TaskService.create_task()
  - Return 201 Created with TaskResponse
  - Handle ValidationException → 422 with field details
  - [Task]: T021, [From]: specs/001-task-crud-api/spec.md#FR-001

- [ ] T022 [US1] Add input validation to TaskCreate schema:
  - title: required (Field(min_length=1, max_length=255))
  - description: optional (Field(max_length=2000))
  - due_date: optional (datetime, validate ISO 8601 format)
  - Custom validator to return field-level error details on 422
  - [Task]: T022, [From]: specs/001-task-crud-api/spec.md#FR-011

- [ ] T023 [US1] Add error handling for create task endpoint:
  - Catch ValidationException from service, return 422 with field details
  - Catch database errors, return 500 with correlation ID
  - Log all task creation attempts with user_id, title, timestamp
  - [Task]: T023, [From]: specs/001-task-crud-api/spec.md#Error-Handling

**Checkpoint**: User Story 1 is fully functional ✅ - authenticated users can create tasks with validation and error handling

---

## Phase 4: User Story 2 - View All Their Tasks (Priority: P1)

**Goal**: Enable authenticated users to retrieve paginated list of all their tasks. Support offset-based pagination with limit/offset query parameters.

**Independent Test**: Authenticated user sends GET /api/{user_id}/tasks with limit=10&offset=0, receives 200 OK with paginated response including items, total count, has_more flag. Different user's request returns only their own tasks (no cross-contamination).

### Tests for User Story 2 (Optional)

- [x] T024 [P] [US2] Create contract test file `backend/tests/contract/test_list_tasks.py` with:
  - Test GET request accepts limit and offset query parameters
  - Test response schema includes items array and pagination metadata
  - Test status code 200 OK
  - Test 401 Unauthorized for missing JWT
  - Test 403 Forbidden if user_id in path doesn't match JWT user_id

- [x] T025 [P] [US2] Create integration test file `backend/tests/integration/test_list_tasks.py` with:
  - Test authenticated user with 5 tasks receives all 5 with pagination metadata
  - Test authenticated user with 0 tasks receives empty items array (not error)
  - Test with 100+ tasks, pagination returns 10 items per page
  - Test different users see only their own tasks
  - Test has_more flag is correct (true if more items exist beyond current page)
  - Test offset-based pagination (offset=10 returns items 11-20)

### Implementation for User Story 2

- [x] T026 [US2] Add list_tasks method to TaskService in `backend/src/services/task_service.py`:
  - `list_tasks(user_id: UUID, limit: int = 10, offset: int = 0) -> (List[Task], int total_count)`
  - Query-level filtering: `WHERE user_id = user_id ORDER BY created_at DESC LIMIT limit OFFSET offset`
  - Return list of Task objects + total count for pagination
  - [Task]: T026, [From]: specs/001-task-crud-api/spec.md#FR-002

- [x] T027 [US2] Create GET /api/{user_id}/tasks endpoint in `backend/src/api/tasks.py`:
  - Accept query parameters: limit (default 10, max 100), offset (default 0)
  - Require JWT token (401 if missing)
  - Verify JWT user_id matches URL user_id (403 if mismatch)
  - Call TaskService.list_tasks(user_id, limit, offset)
  - Return 200 OK with PaginatedResponse (items, pagination metadata)
  - Calculate has_more = (offset + limit) < total_count
  - [Task]: T027, [From]: specs/001-task-crud-api/spec.md#FR-002

- [x] T028 [US2] Add pagination validation:
  - Validate limit ≥ 1 and ≤ 100 (return 422 if invalid)
  - Validate offset ≥ 0 (return 422 if negative)
  - Test with 0 tasks (return empty array, not error)
  - [Task]: T028, [From]: specs/001-task-crud-api/spec.md#FR-002

- [x] T029 [US2] Optimize list_tasks query with indexes:
  - Create index on (user_id, created_at) for fast list retrieval
  - Verify query plan uses index (explain analyze)
  - [Task]: T029, [From]: specs/001-task-crud-api/plan.md#1.2-Data-Model-Design

**Checkpoint**: User Story 2 is fully functional ✅ - users can list all their tasks with pagination

---

## Phase 5: User Story 3 - View a Specific Task (Priority: P1)

**Goal**: Enable authenticated users to retrieve details of a specific task by ID. Return 404 if task doesn't exist or doesn't belong to user.

**Independent Test**: Authenticated user sends GET /api/{user_id}/tasks/{task_id} for their own task, receives 200 OK with full task object. Request for non-existent task receives 404. Request for another user's task receives 403 Forbidden.

### Tests for User Story 3 (Optional)

- [x] T030 [P] [US3] Create contract test file `backend/tests/contract/test_get_task.py` with:
  - Test GET request with valid task_id returns status 200
  - Test response schema includes all task fields
  - Test 401 Unauthorized for missing JWT
  - Test 403 Forbidden if task doesn't belong to authenticated user
  - Test 404 Not Found for non-existent task_id

- [x] T031 [P] [US3] Create integration test file `backend/tests/integration/test_get_task.py` with:
  - Test authenticated user retrieves their own task successfully
  - Test attempt to retrieve another user's task returns 403 (not 404 to avoid leaking info)
  - Test non-existent task_id returns 404
  - Test task_id format validation (UUID format)
  - Test returned object includes all fields: id, user_id, title, description, due_date, completed, completed_at, created_at, updated_at

### Implementation for User Story 3

- [x] T032 [US3] Add get_task method to TaskService in `backend/src/services/task_service.py`:
  - `get_task(user_id: UUID, task_id: UUID) -> Task`
  - Query checks task existence first, then validates ownership
  - Raises ForbiddenException if task exists but doesn't belong to user (403)
  - Raises NotFoundException if task doesn't exist (404)
  - Return Task object
  - [Task]: T032, [From]: specs/001-task-crud-api/spec.md#FR-003

- [x] T033 [US3] Create GET /api/{user_id}/tasks/{task_id} endpoint in `backend/src/api/tasks.py`:
  - Require JWT token (401 if missing)
  - Verify JWT user_id matches URL user_id (403 if mismatch)
  - Validate task_id is valid UUID format (422 if invalid)
  - Call TaskService.get_task(user_id, task_id)
  - Return 200 OK with TaskResponse
  - Catch ForbiddenException → 403, NotFoundException → 404
  - [Task]: T033, [From]: specs/001-task-crud-api/spec.md#FR-003

- [x] T034 [US3] Add error handling for get_task endpoint:
  - Validate task_id is UUID format (return 422 if malformed)
  - Catch ForbiddenException → 403 (task exists but doesn't belong to user)
  - Catch NotFoundException → 404 (task doesn't exist)
  - Log all task retrieval attempts with user_id, task_id
  - [Task]: T034, [From]: specs/001-task-crud-api/spec.md#Error-Handling

**Checkpoint**: User Story 3 is fully functional ✅ - users can view individual task details with proper access control

---

## Phase 6: User Story 4 - Update a Task (Priority: P2)

**Goal**: Enable authenticated users to update task fields (title, description, due_date, completed). Support both full update (PUT) and partial update (PATCH).

**Independent Test**: Authenticated user sends PUT /api/{user_id}/tasks/{task_id} with updated fields, receives 200 OK with updated task. PATCH with single field updates only that field. Request for another user's task receives 403. Invalid data receives 422.

### Tests for User Story 4 (Optional)

- [x] T035 [P] [US4] Create contract test file `backend/tests/contract/test_update_task.py` with:
  - Test PUT request with all fields updates task (status 200)
  - Test PATCH request with single field updates only that field
  - Test response includes all updated fields
  - Test 401 Unauthorized for missing JWT
  - Test 403 Forbidden if task doesn't belong to authenticated user
  - Test 422 Unprocessable Entity for invalid data (empty title, invalid date format)
  - Test 404 Not Found for non-existent task

- [x] T036 [P] [US4] Create integration test file `backend/tests/integration/test_update_task.py` with:
  - Test full update (PUT) changes all provided fields
  - Test partial update (PATCH) changes only provided fields, leaves others unchanged
  - Test updated_at timestamp is refreshed on update
  - Test cannot update user_id or id (immutable fields)
  - Test other users' tasks cannot be updated
  - Test title can be updated to new value
  - Test description can be cleared (set to null)
  - Test due_date can be updated or removed

### Implementation for User Story 4

- [x] T037 [US4] Add update_task and patch_task methods to TaskService:
  - `update_task(user_id: UUID, task_id: UUID, title: str, description: Optional[str], due_date: Optional[datetime], completed: bool) -> Task`
  - `patch_task(user_id: UUID, task_id: UUID, updates: Dict[str, Any]) -> Task`
  - Both query with `WHERE id = task_id AND user_id = user_id`
  - Validate title non-empty for both operations
  - Set updated_at to current time on update
  - Raise NotFoundException if task not found
  - [Task]: T037, [From]: specs/001-task-crud-api/spec.md#FR-004,FR-005

- [x] T038 [US4] Create PUT endpoint for full update in `backend/src/api/tasks.py`:
  - Route: `PUT /api/{user_id}/tasks/{task_id}`
  - Require JWT and user_id match (401/403)
  - Accept TaskUpdate Pydantic model (all fields required for PUT)
  - Call TaskService.update_task()
  - Return 200 OK with updated TaskResponse
  - [Task]: T038, [From]: specs/001-task-crud-api/spec.md#FR-004

- [x] T039 [US4] Create PATCH endpoint for partial update in `backend/src/api/tasks.py`:
  - Route: `PATCH /api/{user_id}/tasks/{task_id}`
  - Require JWT and user_id match (401/403)
  - Accept TaskUpdate Pydantic model (all fields optional for PATCH)
  - Extract only provided fields using `update_wrapper()` or similar
  - Call TaskService.patch_task() with only changed fields
  - Return 200 OK with updated TaskResponse
  - [Task]: T039, [From]: specs/001-task-crud-api/spec.md#FR-005

- [x] T040 [US4] Add validation for update/patch operations:
  - Title required and non-empty (422 if empty)
  - Description max 2000 chars (422 if exceeded)
  - Due_date valid ISO 8601 format (422 if invalid)
  - Return field-level error details in 422 response
  - [Task]: T040, [From]: specs/001-task-crud-api/spec.md#FR-011

- [x] T041 [US4] Add error handling for update/patch endpoints:
  - Catch NotFoundException → 404 Not Found
  - Catch ValidationException → 422 with field details
  - Log all update attempts with user_id, task_id, changed fields
  - [Task]: T041, [From]: specs/001-task-crud-api/spec.md#Error-Handling

**Checkpoint**: User Story 4 is fully functional ✅ - users can update tasks with PUT (full) and PATCH (partial) operations

---

## Phase 7: User Story 5 - Mark Task as Complete (Priority: P2)

**Goal**: Enable authenticated users to toggle task completion status. Set completed_at timestamp when marking complete, clear completed_at when marking incomplete.

**Independent Test**: Authenticated user sends PATCH /api/{user_id}/tasks/{task_id}/complete with {completed: true}, receives 200 OK with completed=true and completed_at timestamp. Sending {completed: false} clears completed_at. Request for another user's task receives 403.

### Tests for User Story 5 (Optional)

- [x] T042 [P] [US5] Create contract test file `backend/tests/contract/test_complete_task.py` with:
  - Test PATCH /tasks/{id}/complete with {completed: true} returns status 200
  - Test response includes completed=true and completed_at timestamp
  - Test PATCH with {completed: false} sets completed=false and completed_at=null
  - Test 401 Unauthorized for missing JWT
  - Test 403 Forbidden if task doesn't belong to authenticated user
  - Test 404 Not Found for non-existent task

- [x] T043 [P] [US5] Create integration test file `backend/tests/integration/test_complete_task.py` with:
  - Test mark incomplete task as complete sets completed=true and completed_at to current time
  - Test mark complete task as incomplete sets completed=false and completed_at to null
  - Test completed_at timestamp is exact (within 1 second)
  - Test toggling completion multiple times works correctly
  - Test other users cannot mark each other's tasks complete
  - Test other task fields unchanged when toggling completion

### Implementation for User Story 5

- [x] T044 [US5] Add mark_complete method to TaskService in `backend/src/services/task_service.py`:
  - `mark_complete(user_id: UUID, task_id: UUID) -> Task` - toggles completion status
  - Queries with `WHERE id = task_id AND user_id = user_id`
  - If incomplete: sets completed=true, completed_at=now()
  - If complete: sets completed=false, completed_at=null
  - Sets updated_at=now()
  - Raises ForbiddenException (403) if task belongs to different user
  - Raises NotFoundException (404) if task not found
  - [Task]: T044, [From]: specs/001-task-crud-api/spec.md#FR-006

- [x] T045 [US5] Create PATCH /api/{user_id}/tasks/{task_id}/complete endpoint in `backend/src/api/tasks.py`:
  - Route: `PATCH /api/{user_id}/tasks/{task_id}/complete`
  - Requires JWT and user_id match (401/403 if not)
  - Accepts `{completed: boolean}` request body
  - Toggles completion status via TaskService.mark_complete()
  - Returns 200 OK with updated TaskResponse including completed_at
  - [Task]: T045, [From]: specs/001-task-crud-api/spec.md#FR-006

- [x] T046 [US5] Add validation and error handling for mark complete endpoint:
  - Validates completed field is required boolean (422 if not)
  - Catches NotFoundException → 404 Not Found
  - Logs completion state changes with user_id, task_id, new_status
  - Error handling handled by FastAPI validation and service exceptions
  - [Task]: T046, [From]: specs/001-task-crud-api/spec.md#Error-Handling

**Checkpoint**: User Story 5 is fully functional ✅ - users can toggle task completion status with timestamp tracking

---

## Phase 8: User Story 6 - Delete a Task (Priority: P3)

**Goal**: Enable authenticated users to permanently delete tasks. Return 204 No Content on success (no response body). Return 403 if task doesn't belong to user.

**Independent Test**: Authenticated user sends DELETE /api/{user_id}/tasks/{task_id} for their own task, receives 204 No Content. Subsequent GET request for deleted task receives 404. Request for another user's task receives 403.

### Tests for User Story 6 (Optional)

- [x] T047 [P] [US6] Create contract test file `backend/tests/contract/test_delete_task.py` with:
  - Test DELETE request returns status 204 No Content (no response body)
  - Test 401 Unauthorized for missing JWT
  - Test 403 Forbidden if task doesn't belong to authenticated user
  - Test 404 Not Found for non-existent task
  - Test subsequent GET request for deleted task returns 404

- [x] T048 [P] [US6] Create integration test file `backend/tests/integration/test_delete_task.py` with:
  - Test authenticated user can delete their own task
  - Test deleted task no longer appears in list
  - Test deleted task ID is not reused (new tasks get new IDs)
  - Test other users cannot delete each other's tasks
  - Test deleting already-deleted task returns 404
  - Test deletion is permanent (verify database record removed)

### Implementation for User Story 6

- [x] T049 [US6] Add delete_task method to TaskService:
  - `delete_task(user_id: UUID, task_id: UUID) -> bool`
  - Query with `WHERE id = task_id AND user_id = user_id`
  - Hard delete (remove row from database)
  - Raise NotFoundException if task not found
  - Return True on successful deletion
  - [Task]: T049, [From]: specs/001-task-crud-api/spec.md#FR-007

- [x] T050 [US6] Create DELETE /api/{user_id}/tasks/{task_id} endpoint:
  - Route: `DELETE /api/{user_id}/tasks/{task_id}`
  - Require JWT and user_id match (401/403)
  - Call TaskService.delete_task(user_id, task_id)
  - Return 204 No Content (no response body)
  - [Task]: T050, [From]: specs/001-task-crud-api/spec.md#FR-007

- [x] T051 [US6] Add error handling for delete endpoint:
  - Catch NotFoundException → 404 Not Found
  - Log all deletion attempts with user_id, task_id, timestamp
  - [Task]: T051, [From]: specs/001-task-crud-api/spec.md#Error-Handling

**Checkpoint**: User Story 6 is fully functional ✅ - users can delete tasks permanently

---

## Phase 9: Unit Tests & Service Layer Coverage

**Purpose**: Comprehensive unit testing of business logic (service layer)

**Target Coverage**: >90% of service layer

- [x] T052 [P] Create unit test suite `backend/tests/unit/test_task_service.py`:
  - Test each TaskService method independently
  - Mock database layer
  - Test validation logic (title required, max lengths, date format)
  - Test user_id filtering (queries include WHERE user_id)
  - Test error handling (NotFoundException, ValidationException)
  - Test timestamp generation (created_at, updated_at, completed_at)
  - Run: `pytest tests/unit/test_task_service.py --cov=src/services --cov-fail-under=90`
  - [Task]: T052, [From]: specs/001-task-crud-api/plan.md#Acceptance-Criteria

- [ ] T053 [P] Create validation tests `backend/tests/unit/test_schemas.py`:
  - Test Pydantic model validation
  - Test required vs optional fields
  - Test field length constraints (title, description)
  - Test date format validation
  - Test field-level error messages on 422
  - Run: `pytest tests/unit/test_schemas.py --cov=src/api/schemas`

**Checkpoint**: Service layer coverage >90% ✅

---

## Phase 10: Integration Tests & API Coverage

**Purpose**: End-to-end testing of all API endpoints with real database

**Target Coverage**: >80% of API layer

- [ ] T054 [P] Create comprehensive integration test `backend/tests/integration/test_api_endpoints.py`:
  - Test all 7 endpoints (POST, GET list, GET detail, PUT, PATCH, PATCH complete, DELETE)
  - Test with authenticated user (valid JWT)
  - Test without JWT (401 Unauthorized)
  - Test with JWT for different user (403 Forbidden or 404)
  - Test status codes for each endpoint
  - Test response schemas match spec
  - Test data isolation (users don't see each other's tasks)
  - Run: `pytest tests/integration/test_api_endpoints.py --cov=src/api --cov-fail-under=80`
  - [Task]: T054, [From]: specs/001-task-crud-api/plan.md#Acceptance-Criteria

- [ ] T055 [P] Create error scenario tests `backend/tests/integration/test_error_handling.py`:
  - Test 400 Bad Request (malformed request)
  - Test 401 Unauthorized (missing/expired JWT)
  - Test 403 Forbidden (user doesn't own task)
  - Test 404 Not Found (non-existent task)
  - Test 422 Unprocessable Entity (validation error with field details)
  - Test 500 Internal Server Error (unexpected error with correlation ID)
  - Verify error response format: {data: null, error: {code, message, details}}
  - Run: `pytest tests/integration/test_error_handling.py`

- [ ] T056 [P] Create pagination tests `backend/tests/integration/test_pagination.py`:
  - Test with 0, 1, 5, 10, 100+ tasks
  - Test limit parameter (1-100 range)
  - Test offset parameter (correct sequencing)
  - Test has_more flag (accurate when more items exist)
  - Test total count is correct
  - Run: `pytest tests/integration/test_pagination.py`

**Checkpoint**: API coverage >80%, all endpoints tested ✅

---

## Phase 11: Contract Tests & OpenAPI Validation

**Purpose**: Validate API contracts against specification

- [ ] T057 Create OpenAPI specification generation:
  - FastAPI auto-generates OpenAPI spec at `/docs` and `/openapi.json`
  - Verify spec includes all 7 endpoints with correct HTTP methods
  - Verify all request/response schemas documented
  - Verify status codes documented (201, 200, 204, 400, 401, 403, 404, 422, 500)
  - Generate `backend/specs/openapi.yaml` from FastAPI app
  - [Task]: T057, [From]: specs/001-task-crud-api/plan.md#Phase-1-Design--Contracts

- [ ] T058 [P] Create contract validation test `backend/tests/contract/test_openapi_validation.py`:
  - Load generated OpenAPI spec
  - Validate all spec requirements are documented (FR-001 to FR-017)
  - Validate endpoint paths match spec paths
  - Validate request/response schemas match spec examples
  - Validate error codes are documented
  - Run: `pytest tests/contract/test_openapi_validation.py`

**Checkpoint**: API contracts validated ✅

---

## Phase 12: Documentation & Quickstart

**Purpose**: Complete documentation for API usage and testing

- [ ] T059 Create `backend/QUICKSTART.md` with:
  - Setup instructions (install dependencies, configure .env)
  - How to run the API locally
  - How to generate JWT tokens for testing
  - Curl examples for all 7 endpoints (successful requests + error cases)
  - Environment variables needed (JWT_SECRET, DATABASE_URL, BETTER_AUTH_SECRET)
  - Troubleshooting guide
  - [Task]: T059, [From]: specs/001-task-crud-api/plan.md#Phase-1-Design--Contracts

- [ ] T060 [P] Create API documentation `backend/docs/api.md` with:
  - Overview of Task CRUD API
  - Authentication section (JWT bearer tokens)
  - Data model documentation (Task entity with all fields)
  - Endpoint reference (all 7 endpoints with descriptions)
  - Error taxonomy (status codes, error codes, meanings)
  - Rate limiting notes (if applicable)
  - Pagination documentation
  - Example workflows (create → list → update → complete → delete)

- [ ] T061 [P] Update `backend/README.md` with:
  - Project overview
  - Technology stack (FastAPI, SQLModel, Neon PostgreSQL)
  - Development setup
  - Running tests (`pytest`, coverage report)
  - Running linting (`ruff check`)
  - Deployment instructions
  - Contributing guidelines

- [ ] T062 Create `backend/.env.example` template:
  - JWT_SECRET=your_secret_here
  - DATABASE_URL=postgresql+asyncpg://user:pass@neon.tech/dbname
  - BETTER_AUTH_SECRET=your_better_auth_secret
  - DEBUG=false
  - LOG_LEVEL=info

**Checkpoint**: Documentation complete ✅

---

## Phase 13: Code Quality & Final Validation

**Purpose**: Ensure code quality, coverage, and specification compliance

- [ ] T063 [P] Run linting and code quality checks:
  - `ruff check backend/src/ --line-length 100` (must pass with no errors)
  - `ruff format backend/src/` (format code consistently)
  - [Task]: T063, [From]: specs/001-task-crud-api/plan.md#Constitution-Alignment

- [ ] T064 [P] Run comprehensive test coverage:
  - `pytest backend/tests/ --cov=backend/src/ --cov-report=html --cov-fail-under=70`
  - Verify minimum 70% code coverage (target 80%+)
  - Generate HTML coverage report
  - [Task]: T064, [From]: specs/001-task-crud-api/plan.md#Acceptance-Criteria

- [ ] T065 Verify spec-to-code traceability:
  - Every function includes comment: `# [Task]: T-XXX, [From]: specs/001-task-crud-api/spec.md#FR-XXX`
  - Run grep to verify all code has task references
  - Generate traceability matrix (spec requirement → task → code)
  - [Task]: T065, [From]: specs/001-task-crud-api/plan.md#Constitution-Alignment

- [ ] T066 [P] Validate OpenAPI spec compliance:
  - Generate OpenAPI spec from running FastAPI app
  - Compare against spec.md requirements
  - Verify all endpoints documented
  - Verify all error codes documented
  - Verify response format consistent

- [ ] T067 Final integration test run:
  - Start FastAPI server with test database
  - Run full test suite: `pytest backend/tests/ -v`
  - Verify all tests pass (unit, integration, contract)
  - Verify no warnings or deprecations
  - [Task]: T067, [From]: specs/001-task-crud-api/plan.md#Acceptance-Criteria

**Checkpoint**: Code quality gates passed ✅ - ready for deployment

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) [BLOCKS all user stories]
    ↓ (after Phase 2 complete)
Phase 3 (US1), Phase 4 (US2), Phase 5 (US3) [Can run in parallel]
    ↓
Phase 6 (US4), Phase 7 (US5), Phase 8 (US6) [Can run in parallel after US1-US3]
    ↓
Phase 9 (Unit Tests)
    ↓
Phase 10 (Integration Tests)
    ↓
Phase 11 (Contract Tests)
    ↓
Phase 12 (Documentation)
    ↓
Phase 13 (Code Quality & Validation)
```

### Within Each User Story

Order: Tests (if TDD) → Models → Services → Endpoints → Error Handling → Integration

### Parallel Opportunities

- **Phase 1 Setup**: All [P] tasks can run in parallel (T002, T003, T004, T005, T006, T007)
- **Phase 2 Foundational**: All [P] tasks can run in parallel (T010, T013, T015)
- **Phase 3-5 User Stories**: All can start after Phase 2 complete, but sequence US1 → US2 → US3 recommended (P1 priority)
- **Phase 6-8 User Stories**: All can start after US1-US3 complete, recommended sequence US4 → US5 → US6
- **Tests**: All [P] test files can run in parallel

### Recommended Sequential Execution (Conservative MVP)

```
T001 → T002,T003,T004,T005,T006,T007,T008 →
T009,T010,T011,T012,T013,T014,T015,T016 →
T017,T018,T019,T020,T021,T022,T023 (US1) →
T024,T025,T026,T027,T028,T029 (US2) →
T030,T031,T032,T033,T034 (US3) →
T035,T036,T037,T038,T039,T040,T041 (US4) →
T042,T043,T044,T045,T046 (US5) →
T047,T048,T049,T050,T051 (US6) →
T052,T053,T054,T055,T056,T057,T058 →
T059,T060,T061,T062 →
T063,T064,T065,T066,T067
```

### Recommended Parallel Execution (Aggressive 2+ Team Members)

```
Parallel Phase 1 (Setup):
  T001 | T002,T003,T004,T005,T006,T007,T008

Parallel Phase 2 (Foundational):
  T009 | T010,T013,T015 | T011 | T012 | T014,T016

Parallel User Stories (after Phase 2):
  Worker 1: US1 (T017-T023)
  Worker 2: US2 (T024-T029)
  Worker 3: US3 (T030-T034)

  After US1-US3:
  Worker 1: US4 (T035-T041)
  Worker 2: US5 (T042-T046)
  Worker 3: US6 (T047-T051)

Parallel Tests (after implementation):
  Worker 1: Unit Tests (T052,T053)
  Worker 2: Integration Tests (T054,T055,T056)
  Worker 3: Contract Tests (T057,T058)

Parallel Documentation & Validation:
  Worker 1: Documentation (T059,T060,T061,T062)
  Worker 2: Code Quality (T063,T064,T065,T066)
  Worker 3: Final Validation (T067)
```

---

## Implementation Strategy

### MVP Scope (Phase 1 Recommendation)

Focus on **User Story 1** (Create Task) + **User Story 2** (List Tasks) to validate architecture:

1. Complete Phase 1-2 (Setup + Foundational)
2. Complete Phase 3-4 (US1 + US2)
3. Minimal testing (contract test for each)
4. Deploy and validate with real users

This gives users core functionality (create tasks, view tasks) quickly.

### Incremental Delivery

After MVP (US1+US2):
- Add US3 (View Task Detail) - 3 tasks, 1 day
- Add US4 (Update Task) - 7 tasks, 2 days
- Add US5 (Mark Complete) - 5 tasks, 1 day
- Add US6 (Delete Task) - 3 tasks, 1 day

Each increment is independently testable and deployable.

### Quality Assurance

- **Code Coverage**: Start with >70%, goal is 80%+
- **Linting**: Ruff must pass (no manual fixes)
- **Documentation**: Generate OpenAPI spec + maintain QUICKSTART.md
- **Traceability**: Every function has [Task] comment linking to spec

---

## File Structure Summary

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app (T014)
│   ├── config.py                  # Environment config (T010)
│   ├── database.py                # Async Neon connection (T009)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # Base model + User (T016)
│   │   └── task.py                # Task model (T019)
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py        # CRUD logic (T020, T026, T032, T037, T044, T049)
│   └── api/
│       ├── __init__.py
│       ├── middleware.py          # JWT middleware (T012)
│       ├── schemas.py             # Pydantic models (T013)
│       ├── errors.py              # Custom exceptions (T015)
│       └── tasks.py               # Task endpoints (T021, T027, T033, T038, T039, T045, T050)
├── tests/
│   ├── conftest.py                # pytest fixtures
│   ├── unit/
│   │   ├── test_task_service.py   # Service tests (T052)
│   │   └── test_schemas.py        # Schema validation (T053)
│   ├── integration/
│   │   ├── test_api_endpoints.py  # Full API tests (T054)
│   │   ├── test_error_handling.py # Error scenarios (T055)
│   │   └── test_pagination.py     # Pagination tests (T056)
│   └── contract/
│       ├── test_create_task.py    # Contract: CREATE (T017)
│       ├── test_list_tasks.py     # Contract: LIST (T024)
│       ├── test_get_task.py       # Contract: GET (T030)
│       ├── test_update_task.py    # Contract: UPDATE (T035)
│       ├── test_mark_complete.py  # Contract: COMPLETE (T042)
│       ├── test_delete_task.py    # Contract: DELETE (T047)
│       └── test_openapi_validation.py  # OpenAPI spec (T058)
├── docs/
│   └── api.md                     # API documentation (T060)
├── .env.example                   # Environment template (T062)
├── .gitignore                     # Git ignore (T008)
├── Dockerfile                     # Container image (T007)
├── pyproject.toml                 # Project metadata (T002)
├── requirements.txt               # Dependencies (T003)
├── pytest.ini                     # Pytest config (T006)
├── QUICKSTART.md                  # Quick start guide (T059)
└── README.md                      # Project documentation (T061)
```

---

## Summary

**Total Tasks**: 67 (T001-T067)

**Task Breakdown**:
- Setup & Infrastructure: T001-T016 (16 tasks)
- User Story 1 (Create): T017-T023 (7 tasks)
- User Story 2 (List): T024-T029 (6 tasks)
- User Story 3 (Get Detail): T030-T034 (5 tasks)
- User Story 4 (Update): T035-T041 (7 tasks)
- User Story 5 (Mark Complete): T042-T046 (5 tasks)
- User Story 6 (Delete): T047-T051 (5 tasks)
- Testing & Quality: T052-T067 (16 tasks)

**Parallel Opportunities**:
- Phase 1 Setup: 7 tasks can run in parallel [P]
- Phase 2 Foundational: 3 tasks can run in parallel [P]
- User Stories: Can be started in parallel after Phase 2, but recommend sequential (P1 → P2 → P3)
- Tests: Multiple test files can run in parallel

**MVP Scope**: US1 + US2 (13 tasks from Phases 1-4) = Minimum viable product
**Full Scope**: All 6 user stories (51 tasks from Phases 1-8) = Complete Task CRUD API
**Quality**: 16 tasks dedicated to testing, documentation, and code quality validation

All tasks include exact file paths, agent assignments, acceptance criteria, and spec references for autonomous execution by Claude Code agents.
