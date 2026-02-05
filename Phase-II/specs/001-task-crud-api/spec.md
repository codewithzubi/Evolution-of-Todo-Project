# Feature Specification: Task CRUD API

**Feature Branch**: `001-task-crud-api`
**Created**: 2026-02-01
**Status**: Draft
**Input**: User description: Task CRUD API specification for backend Phase 2

---

## Feature Overview

The Task CRUD API provides secure, RESTful endpoints for managing user tasks. This API enables multi-user applications to create, retrieve, update, and delete tasks with full authentication and authorization enforcement. Each user can only access and modify their own tasks, ensuring data isolation in a shared system.

**Core Purpose:**
- Enable authenticated users to manage their personal tasks
- Provide complete CRUD (Create, Read, Update, Delete) operations
- Enforce row-level security: users access only their own data
- Support task lifecycle management (creation, completion, deletion)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a New Task (Priority: P1)

As an authenticated user, I want to create a new task with a title, optional description, and due date so that I can track work items I need to complete.

**Why this priority**: Core functionality; required for users to start managing tasks. MVP cannot function without task creation.

**Independent Test**: Can be fully tested by authenticated user submitting a task creation request and verifying the task appears in their task list with the provided details.

**Acceptance Scenarios**:

1. **Given** an authenticated user with valid JWT token, **When** they POST a new task with title and due date, **Then** the task is created and returned with a unique ID and creation timestamp.
2. **Given** an authenticated user, **When** they create a task with only a title (description and due_date optional), **Then** the task is created successfully with empty optional fields.
3. **Given** an authenticated user, **When** they attempt to create a task without a title, **Then** a validation error is returned with a clear error message.
4. **Given** an unauthenticated request, **When** attempting to create a task, **Then** a 401 Unauthorized error is returned.

---

### User Story 2 - View All Their Tasks (Priority: P1)

As an authenticated user, I want to retrieve a list of all my tasks with optional filtering and pagination so that I can see my complete task inventory.

**Why this priority**: Core functionality; essential for users to see what they need to work on. Enables task overview and planning.

**Independent Test**: Can be fully tested by authenticated user fetching their task list and verifying only their own tasks are returned, not other users' tasks.

**Acceptance Scenarios**:

1. **Given** an authenticated user with 5 tasks, **When** they GET their task list, **Then** all 5 tasks are returned with pagination metadata.
2. **Given** an authenticated user with no tasks, **When** they GET their task list, **Then** an empty list is returned (not an error).
3. **Given** an authenticated user with 100 tasks and default pagination of 10 items, **When** they GET the first page, **Then** 10 tasks are returned with next page indicator.
4. **Given** another authenticated user with different tasks, **When** the first user GETs their list, **Then** only the first user's tasks are returned (no cross-contamination).

---

### User Story 3 - View a Specific Task (Priority: P1)

As an authenticated user, I want to retrieve the details of a specific task by ID so that I can see its full information.

**Why this priority**: Core read operation; required for displaying task details to the user.

**Independent Test**: Can be fully tested by authenticated user fetching a specific task and verifying the complete task details are returned.

**Acceptance Scenarios**:

1. **Given** an authenticated user and a task ID that belongs to them, **When** they GET that task, **Then** the complete task details are returned.
2. **Given** an authenticated user and a task ID that does NOT belong to them, **When** they attempt to GET that task, **Then** a 403 Forbidden error is returned.
3. **Given** an authenticated user and a non-existent task ID, **When** they GET that task, **Then** a 404 Not Found error is returned.

---

### User Story 4 - Update a Task (Priority: P2)

As an authenticated user, I want to update a task's details (title, description, due date, completion status) so that I can keep my tasks current and accurate.

**Why this priority**: Important for task lifecycle; allows users to modify task information. P2 because creation and viewing are more critical for MVP.

**Independent Test**: Can be fully tested by authenticated user updating a task field and verifying the change is persisted and reflected on retrieval.

**Acceptance Scenarios**:

1. **Given** an authenticated user and a task they own, **When** they PUT a task with updated title and due_date, **Then** the task is updated with new values and returned.
2. **Given** an authenticated user and a task they own, **When** they PATCH only the title field, **Then** only title is updated; other fields remain unchanged.
3. **Given** an authenticated user and a task that does NOT belong to them, **When** they attempt to update it, **Then** a 403 Forbidden error is returned.
4. **Given** an authenticated user, **When** they attempt to update a task with invalid data (e.g., empty title), **Then** a validation error is returned.

---

### User Story 5 - Mark Task as Complete (Priority: P2)

As an authenticated user, I want to mark a task as complete (or incomplete) so that I can track my progress and maintain a record of completed work.

**Why this priority**: Important for productivity tracking; dedicated endpoint for common operation of checking off tasks.

**Independent Test**: Can be fully tested by authenticated user PATCH-completing a task and verifying its completed status changes.

**Acceptance Scenarios**:

1. **Given** an authenticated user with an incomplete task, **When** they PATCH the task's complete endpoint, **Then** the task is marked as completed with completion timestamp.
2. **Given** an authenticated user with a completed task, **When** they PATCH the complete endpoint again, **Then** the task is marked as incomplete.
3. **Given** an authenticated user and a task that does NOT belong to them, **When** they attempt to mark it complete, **Then** a 403 Forbidden error is returned.

---

### User Story 6 - Delete a Task (Priority: P3)

As an authenticated user, I want to delete a task permanently so that I can remove tasks I no longer need to track.

**Why this priority**: Important for data management; allows cleanup. P3 because core CRUD operations are more critical than deletion for initial MVP.

**Independent Test**: Can be fully tested by authenticated user deleting a task and verifying it no longer appears in their task list.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a task they own, **When** they DELETE that task, **Then** the task is deleted and a success response is returned.
2. **Given** an authenticated user after deleting a task, **When** they attempt to GET that deleted task, **Then** a 404 Not Found error is returned.
3. **Given** an authenticated user and a task that does NOT belong to them, **When** they attempt to delete it, **Then** a 403 Forbidden error is returned.

---

### Edge Cases

- What happens when a user's JWT token has expired? (Should return 401; client must refresh token)
- How does the system handle concurrent requests to update the same task? (Last write wins; document in API behavior)
- What happens if a user attempts to access a task with an invalid task ID format? (Return 400 Bad Request with validation error)
- How does pagination behave with filtering applied? (Offset-based pagination applies after filtering)
- What happens when a user deletes a task and immediately tries to recreate a task with the same data? (Should succeed; creates new task with new ID)

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a POST endpoint at `/api/{user_id}/tasks` to create a new task for the authenticated user.
- **FR-002**: System MUST provide a GET endpoint at `/api/{user_id}/tasks` to retrieve all tasks for the authenticated user with pagination support (default 10 items per page, offset-based).
- **FR-003**: System MUST provide a GET endpoint at `/api/{user_id}/tasks/{task_id}` to retrieve a specific task's complete details.
- **FR-004**: System MUST provide a PUT endpoint at `/api/{user_id}/tasks/{task_id}` to fully update a task's fields (title, description, due_date, completed).
- **FR-005**: System MUST provide a PATCH endpoint at `/api/{user_id}/tasks/{task_id}` to partially update a task's fields.
- **FR-006**: System MUST provide a PATCH endpoint at `/api/{user_id}/tasks/{task_id}/complete` to toggle task completion status and record completion timestamp.
- **FR-007**: System MUST provide a DELETE endpoint at `/api/{user_id}/tasks/{task_id}` to permanently delete a task.
- **FR-008**: All endpoints MUST require a valid JWT token in the Authorization header (format: `Authorization: Bearer <token>`).
- **FR-009**: System MUST verify the JWT token's user ID matches the `{user_id}` in the URL path; if not, return 403 Forbidden.
- **FR-010**: System MUST validate that the user requesting a task owns that task before allowing any access (GET, PUT, PATCH, DELETE).
- **FR-011**: System MUST enforce that task creation requires a non-empty title (max 255 characters) and optional description (max 2000 characters) and due_date (ISO 8601 format).
- **FR-012**: System MUST return a 401 Unauthorized error when a request lacks a valid JWT token or the token is expired.
- **FR-013**: System MUST return a 403 Forbidden error when a user attempts to access, modify, or delete a task that does not belong to them.
- **FR-014**: System MUST return a 404 Not Found error when a user attempts to access a task ID that does not exist (or doesn't belong to them).
- **FR-015**: System MUST return a 422 Unprocessable Entity error with detailed validation messages when request data is invalid (e.g., missing required fields, invalid format).
- **FR-016**: System MUST populate `created_at` and `updated_at` timestamps on task creation and updates automatically.
- **FR-017**: System MUST store and return a `completed_at` timestamp when a task is marked complete; set to null if task is marked incomplete.

### Key Entities *(include if feature involves data)*

- **Task**: Represents a user's to-do item with properties: id (UUID), user_id (UUID), title (string, required), description (string, optional), due_date (ISO 8601 datetime, optional), completed (boolean, default false), completed_at (datetime, nullable), created_at (datetime, auto), updated_at (datetime, auto). Relationships: belongs to User.
- **User**: Represents an authenticated user with properties: id (UUID), email (string), name (string). Relationships: has many Tasks.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All endpoints respond with valid JSON in documented format within 500ms for 95th percentile latency under normal load.
- **SC-002**: Authentication validation occurs before any task data is accessed; unauthorized requests receive 401/403 errors without data leakage.
- **SC-003**: A user can create, retrieve, update, and delete a task in under 3 seconds (cumulative) through valid API calls.
- **SC-004**: System correctly enforces row-level security: a user attempting to access another user's task receives 403 Forbidden 100% of the time (zero unauthorized access).
- **SC-005**: Validation errors provide clear, actionable error messages identifying which fields failed validation and why (e.g., "title: required field").
- **SC-006**: Pagination allows users to efficiently retrieve 100+ tasks without performance degradation; list operations remain under 500ms even with large datasets.
- **SC-007**: API documentation is complete with working curl/HTTP examples for all endpoints, demonstrating both success and error scenarios.

---

## API Endpoints Summary

| HTTP Method | Endpoint | Purpose | Auth Required |
|-------------|----------|---------|----------------|
| POST | `/api/{user_id}/tasks` | Create new task | ✅ JWT |
| GET | `/api/{user_id}/tasks` | List all user tasks (paginated) | ✅ JWT |
| GET | `/api/{user_id}/tasks/{task_id}` | Get task details | ✅ JWT |
| PUT | `/api/{user_id}/tasks/{task_id}` | Update entire task | ✅ JWT |
| PATCH | `/api/{user_id}/tasks/{task_id}` | Partial update task | ✅ JWT |
| PATCH | `/api/{user_id}/tasks/{task_id}/complete` | Toggle completion status | ✅ JWT |
| DELETE | `/api/{user_id}/tasks/{task_id}` | Delete task | ✅ JWT |

---

## Request/Response Schemas

### Create Task Request (POST `/api/{user_id}/tasks`)

```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive API docs for all endpoints",
  "due_date": "2026-02-15T17:00:00Z"
}
```

**Fields**:
- `title` (required, string, max 255): Task title
- `description` (optional, string, max 2000): Detailed task description
- `due_date` (optional, ISO 8601 datetime): When task is due

### Create Task Response (201 Created)

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "title": "Complete project documentation",
    "description": "Write comprehensive API docs for all endpoints",
    "due_date": "2026-02-15T17:00:00Z",
    "completed": false,
    "completed_at": null,
    "created_at": "2026-02-01T10:30:00Z",
    "updated_at": "2026-02-01T10:30:00Z"
  },
  "error": null
}
```

### List Tasks Response (GET `/api/{user_id}/tasks?limit=10&offset=0`)

```json
{
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "title": "Complete project documentation",
        "description": "Write comprehensive API docs for all endpoints",
        "due_date": "2026-02-15T17:00:00Z",
        "completed": false,
        "completed_at": null,
        "created_at": "2026-02-01T10:30:00Z",
        "updated_at": "2026-02-01T10:30:00Z"
      }
    ],
    "pagination": {
      "limit": 10,
      "offset": 0,
      "total": 42,
      "has_more": true
    }
  },
  "error": null
}
```

### Update Task Request (PUT `/api/{user_id}/tasks/{task_id}`)

```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "due_date": "2026-02-20T17:00:00Z",
  "completed": false
}
```

**Fields**:
- `title` (required, string, max 255): New task title
- `description` (optional, string, max 2000): New description
- `due_date` (optional, ISO 8601 datetime): New due date
- `completed` (optional, boolean): Completion status

### Partial Update Request (PATCH `/api/{user_id}/tasks/{task_id}`)

```json
{
  "title": "Updated task title"
}
```

**Fields**: Any subset of task fields to update; others remain unchanged.

### Mark Complete Request (PATCH `/api/{user_id}/tasks/{task_id}/complete`)

```json
{
  "completed": true
}
```

**Fields**:
- `completed` (required, boolean): Set to true to mark complete, false to mark incomplete

### Mark Complete Response (200 OK)

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "title": "Complete project documentation",
    "description": "Write comprehensive API docs for all endpoints",
    "due_date": "2026-02-15T17:00:00Z",
    "completed": true,
    "completed_at": "2026-02-01T14:45:00Z",
    "created_at": "2026-02-01T10:30:00Z",
    "updated_at": "2026-02-01T14:45:00Z"
  },
  "error": null
}
```

### Delete Task Response (204 No Content)

```
No response body; successful deletion returns HTTP 204.
```

### Error Response (Example: 401 Unauthorized)

```json
{
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Missing or invalid JWT token",
    "details": null
  }
}
```

### Error Response (Example: 403 Forbidden)

```json
{
  "data": null,
  "error": {
    "code": "FORBIDDEN",
    "message": "You do not have permission to access this task",
    "details": null
  }
}
```

### Error Response (Example: 422 Unprocessable Entity)

```json
{
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "title": ["Field required"],
      "due_date": ["Invalid ISO 8601 datetime format"]
    }
  }
}
```

---

## Authentication & Authorization

### JWT Token Requirements

- **Token Format**: `Authorization: Bearer <JWT_TOKEN>`
- **Token Structure**: JWT contains claims including `user_id`, `email`, and standard claims (iss, exp, iat)
- **Verification**: Backend must verify token signature using shared secret key (from `.env` variable `JWT_SECRET`)
- **Expiration**: Tokens are valid for 7 days; clients must handle 401 responses and refresh tokens

### Authorization Rules

1. **User ID Matching**: The `user_id` claim in the JWT token MUST match the `{user_id}` in the URL path. If mismatch, return 403 Forbidden.
2. **Ownership Verification**: Before returning or modifying a task, the system MUST verify `task.user_id == jwt_claim.user_id`. If not, return 403 Forbidden.
3. **No Data Leakage**: Queries MUST filter by authenticated `user_id` to ensure no cross-user data access occurs.

---

## Error Handling & Status Codes

| Status | Code | Scenario | Example Message |
|--------|------|----------|------------------|
| 201 | Created | Task successfully created | (Response body contains new task) |
| 204 | No Content | Task successfully deleted | (No response body) |
| 400 | Bad Request | Invalid request format or parameters | `"Invalid task ID format"` |
| 401 | Unauthorized | Missing or expired JWT token | `"Missing or invalid JWT token"` |
| 403 | Forbidden | User lacks permission (not task owner) | `"You do not have permission to access this task"` |
| 404 | Not Found | Task ID does not exist or is deleted | `"Task not found"` |
| 422 | Unprocessable Entity | Validation error (invalid data) | `"Request validation failed"` with field-level details |
| 500 | Internal Server Error | Unexpected server error | `"Internal server error"` (with correlation ID for logging) |

---

## Security Considerations

### Must-Have Security Controls

- **JWT Middleware**: All endpoints (except login/signup) must validate JWT in Authorization header before processing any request.
- **Token Verification**: Always verify JWT signature using the secret key from `.env`; never trust unverified tokens.
- **User ID Validation**: All queries must filter by authenticated user ID; never return tasks for other users.
- **Secrets Management**: JWT secret key MUST NOT be hardcoded; store in `.env` file and never commit to version control.
- **HTTPS Enforcement**: All API calls MUST use HTTPS in production to prevent token interception.
- **Input Validation**: Validate all request fields (title length, date format, etc.) before processing; return 422 with field-level errors.
- **Error Messages**: Error responses MUST NOT leak information (e.g., don't say "User 123 has no tasks for that ID"; say "Task not found").
- **Rate Limiting**: Recommended: Implement rate limiting to prevent brute force attacks and abuse (max 100 requests per minute per user).
- **Audit Logging**: Log all task mutations (create, update, delete) with timestamp, user ID, and action for security auditing.

---

## Assumptions

- **Soft Deletes Not Required for MVP**: Tasks are hard-deleted immediately; audit logging is optional but recommended.
- **No Concurrent Editing Conflict Resolution**: If two users attempt to update the same task simultaneously, last write wins (no conflict resolution).
- **Task Dates Are Optional**: Due dates and completion dates are nullable and optional unless the user provides them.
- **Simple Task Model**: Tasks have no subtasks, dependencies, or priority levels in this MVP; scope limited to basic CRUD.
- **No Notification System**: Task creation/completion does not trigger notifications; that is a future enhancement.
- **No Collaborative Tasks**: Tasks belong to a single user; no sharing or collaboration in MVP scope.
- **JWT Token Refresh**: Frontend is responsible for obtaining and refreshing JWT tokens; backend validates and uses them.
- **No Bulk Operations**: API does not support bulk create/update/delete in MVP; operations are per-task.

---

## Acceptance Criteria Checklist

- ✅ All 7 API endpoints are implemented and respond with correct HTTP status codes
- ✅ All endpoints require JWT authentication; unauthenticated requests receive 401
- ✅ All endpoints enforce ownership validation; cross-user access receives 403
- ✅ Request/response schemas match documented formats exactly
- ✅ Validation errors return 422 with field-level details
- ✅ Pagination works correctly with `limit` and `offset` query parameters
- ✅ Task timestamps (`created_at`, `updated_at`, `completed_at`) are managed automatically
- ✅ All edge cases listed above are handled gracefully
- ✅ API documentation includes curl/HTTP examples for all endpoints
- ✅ Security controls (JWT, ownership validation, secrets) are implemented
