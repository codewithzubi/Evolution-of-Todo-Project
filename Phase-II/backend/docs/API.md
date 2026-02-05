# Task CRUD API Documentation

## Overview

The Task CRUD API is a RESTful service for managing user tasks with full CRUD (Create, Read, Update, Delete) functionality. The API provides JWT-based authentication, pagination support, and comprehensive error handling.

**Base URL**: `/api/{user_id}`

**Version**: 0.1.0

## Authentication

All endpoints require JWT (JSON Web Token) authentication via the `Authorization` header.

### Bearer Token Format

```
Authorization: Bearer <jwt_token>
```

### Token Claims

The JWT token must contain the following claims:

- `user_id` (string, UUID): The authenticated user's unique identifier
- `email` (string): The user's email address
- `iat` (integer): Token issued at timestamp
- `exp` (integer): Token expiration timestamp

### Example Token Creation

```python
from datetime import datetime, timedelta
from jose import jwt

payload = {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "iat": datetime.utcnow(),
    "exp": datetime.utcnow() + timedelta(hours=24),
}

token = jwt.encode(
    payload,
    "your_jwt_secret",
    algorithm="HS256"
)
```

## Task Data Model

### Task Object

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Complete project documentation",
  "description": "Write comprehensive API docs and examples",
  "due_date": "2026-02-15T10:00:00",
  "completed": false,
  "completed_at": null,
  "created_at": "2026-02-01T08:30:00",
  "updated_at": "2026-02-01T08:30:00"
}
```

### Field Descriptions

- `id` (UUID): Unique task identifier (auto-generated)
- `user_id` (UUID): ID of the task owner
- `title` (string): Task title (required, 1-255 characters)
- `description` (string, optional): Task description (max 2000 characters)
- `due_date` (ISO 8601 datetime, optional): Task due date
- `completed` (boolean): Whether the task is completed (default: false)
- `completed_at` (ISO 8601 datetime, optional): When the task was marked complete
- `created_at` (ISO 8601 datetime): Task creation timestamp
- `updated_at` (ISO 8601 datetime): Last update timestamp

## API Endpoints

### 1. Create Task

Create a new task for the authenticated user.

**Endpoint**: `POST /api/{user_id}/tasks`

**Authentication**: Required (Bearer token)

**Request Body**:

```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive API docs",
  "due_date": "2026-02-15T10:00:00"
}
```

**Request Fields**:

- `title` (required): Task title (1-255 characters)
- `description` (optional): Task description (max 2000 characters)
- `due_date` (optional): Due date in ISO 8601 format

**Response**: 201 Created

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Complete project documentation",
    "description": "Write comprehensive API docs",
    "due_date": "2026-02-15T10:00:00",
    "completed": false,
    "completed_at": null,
    "created_at": "2026-02-02T10:00:00",
    "updated_at": "2026-02-02T10:00:00"
  },
  "error": null
}
```

**Error Responses**:

- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: JWT user_id doesn't match URL user_id
- `422 Unprocessable Entity`: Invalid request data

**Example**:

```bash
curl -X POST "http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/tasks" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive API docs",
    "due_date": "2026-02-15T10:00:00"
  }'
```

---

### 2. List Tasks

Retrieve paginated list of all tasks for the authenticated user.

**Endpoint**: `GET /api/{user_id}/tasks`

**Authentication**: Required (Bearer token)

**Query Parameters**:

- `limit` (optional, default: 10, max: 100): Number of tasks per page
- `offset` (optional, default: 0): Number of tasks to skip

**Response**: 200 OK

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Complete project documentation",
      "description": "Write comprehensive API docs",
      "due_date": "2026-02-15T10:00:00",
      "completed": false,
      "completed_at": null,
      "created_at": "2026-02-02T10:00:00",
      "updated_at": "2026-02-02T10:00:00"
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total": 5,
    "has_more": false
  }
}
```

**Response Fields**:

- `items` (array): Array of task objects
- `pagination` (object):
  - `limit`: Number of items requested per page
  - `offset`: Number of items skipped
  - `total`: Total number of tasks
  - `has_more`: Whether more items exist beyond current page

**Error Responses**:

- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: JWT user_id doesn't match URL user_id
- `422 Unprocessable Entity`: Invalid limit or offset

**Example**:

```bash
# Get first 10 tasks
curl -X GET "http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/tasks?limit=10&offset=0" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Get next 10 tasks
curl -X GET "http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/tasks?limit=10&offset=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 3. Get Task Detail

Retrieve a specific task by ID.

**Endpoint**: `GET /api/{user_id}/tasks/{task_id}`

**Authentication**: Required (Bearer token)

**Path Parameters**:

- `user_id`: The task owner's ID
- `task_id`: The task's ID (UUID format)

**Response**: 200 OK

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Complete project documentation",
    "description": "Write comprehensive API docs",
    "due_date": "2026-02-15T10:00:00",
    "completed": false,
    "completed_at": null,
    "created_at": "2026-02-02T10:00:00",
    "updated_at": "2026-02-02T10:00:00"
  },
  "error": null
}
```

**Error Responses**:

- `400/422 Bad Request`: Invalid task_id format
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: Task doesn't belong to authenticated user
- `404 Not Found`: Task doesn't exist

**Example**:

```bash
curl -X GET "http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/tasks/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 4. Update Task (Full)

Fully update a task (all fields required).

**Endpoint**: `PUT /api/{user_id}/tasks/{task_id}`

**Authentication**: Required (Bearer token)

**Request Body**:

```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "due_date": "2026-02-20T10:00:00",
  "completed": false
}
```

**Response**: 200 OK (returns updated task object)

**Error Responses**:

- `400/422 Bad Request`: Invalid task_id or request data
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: Task doesn't belong to authenticated user
- `404 Not Found`: Task doesn't exist

**Example**:

```bash
curl -X PUT "http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/tasks/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated task title",
    "description": "Updated description",
    "due_date": "2026-02-20T10:00:00",
    "completed": false
  }'
```

---

### 5. Update Task (Partial)

Partially update a task (only provided fields are updated).

**Endpoint**: `PATCH /api/{user_id}/tasks/{task_id}`

**Authentication**: Required (Bearer token)

**Request Body** (any combination of fields):

```json
{
  "title": "Just update the title"
}
```

**Response**: 200 OK (returns updated task object)

**Error Responses**:

- `400/422 Bad Request`: Invalid task_id or request data
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: Task doesn't belong to authenticated user
- `404 Not Found`: Task doesn't exist

**Example**:

```bash
# Update only the title
curl -X PATCH "http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/tasks/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"title": "New title"}'
```

---

### 6. Mark Task Complete/Incomplete

Toggle task completion status.

**Endpoint**: `PATCH /api/{user_id}/tasks/{task_id}/complete`

**Authentication**: Required (Bearer token)

**Request Body**:

```json
{
  "completed": true
}
```

**Response**: 200 OK

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Complete project documentation",
    "description": "Write comprehensive API docs",
    "due_date": "2026-02-15T10:00:00",
    "completed": true,
    "completed_at": "2026-02-02T11:00:00",
    "created_at": "2026-02-02T10:00:00",
    "updated_at": "2026-02-02T11:00:00"
  },
  "error": null
}
```

**Note**: When `completed` is set to `true`, `completed_at` is automatically set to the current timestamp. When set to `false`, `completed_at` is cleared.

**Error Responses**:

- `400/422 Bad Request`: Invalid task_id or request body
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: Task doesn't belong to authenticated user
- `404 Not Found`: Task doesn't exist

**Example**:

```bash
# Mark task as complete
curl -X PATCH "http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/tasks/550e8400-e29b-41d4-a716-446655440000/complete" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

---

### 7. Delete Task

Permanently delete a task.

**Endpoint**: `DELETE /api/{user_id}/tasks/{task_id}`

**Authentication**: Required (Bearer token)

**Response**: 204 No Content (empty response body)

**Error Responses**:

- `400/422 Bad Request`: Invalid task_id format
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: Task doesn't belong to authenticated user
- `404 Not Found`: Task doesn't exist

**Example**:

```bash
curl -X DELETE "http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/tasks/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Error Responses

All error responses follow a consistent format:

```json
{
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": ["error description"],
      "other_field": ["error description"]
    }
  }
}
```

### Error Codes

| Status Code | Code | Meaning |
|-------------|------|---------|
| 400 | BAD_REQUEST | Malformed request |
| 401 | UNAUTHORIZED | Missing or invalid JWT token |
| 403 | FORBIDDEN | User doesn't have permission |
| 404 | NOT_FOUND | Resource doesn't exist |
| 422 | VALIDATION_ERROR | Request validation failed |
| 500 | INTERNAL_SERVER_ERROR | Unexpected server error |

### Example Error Responses

**Validation Error (422)**:

```json
{
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "title": ["Field required"],
      "description": ["Ensure this value has at most 2000 characters"]
    }
  }
}
```

**Unauthorized (401)**:

```json
{
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid JWT token: Signature verification failed",
    "details": null
  }
}
```

**Not Found (404)**:

```json
{
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found",
    "details": null
  }
}
```

---

## Example Workflows

### Complete Task Lifecycle

```bash
# 1. Create a task
CREATE_RESPONSE=$(curl -X POST "http://localhost:8000/api/user123/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review pull requests",
    "description": "Review and approve all pending PRs",
    "due_date": "2026-02-05T17:00:00"
  }')
TASK_ID=$(echo $CREATE_RESPONSE | jq -r '.data.id')

# 2. List all tasks
curl -X GET "http://localhost:8000/api/user123/tasks?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"

# 3. Get specific task details
curl -X GET "http://localhost:8000/api/user123/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"

# 4. Update task
curl -X PATCH "http://localhost:8000/api/user123/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated: Review and approve all critical PRs first"}'

# 5. Mark task complete
curl -X PATCH "http://localhost:8000/api/user123/tasks/$TASK_ID/complete" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# 6. Delete task
curl -X DELETE "http://localhost:8000/api/user123/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Rate Limiting

Currently, the API does not enforce rate limiting. This may be implemented in future versions.

---

## Pagination

All list endpoints support offset-based pagination:

- **limit**: Items per page (default: 10, max: 100)
- **offset**: Number of items to skip (default: 0, must be ≥ 0)
- **has_more**: Boolean indicating if more items exist

**Example**: Get items 21-30

```bash
curl -X GET "http://localhost:8000/api/user123/tasks?limit=10&offset=20" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Timestamps

All timestamps are in ISO 8601 format (UTC):

```
2026-02-02T10:30:45.123456
```

---

## Status Codes Summary

- **201 Created**: Task successfully created (POST)
- **200 OK**: Success (GET, PATCH, PUT)
- **204 No Content**: Success with no response body (DELETE)
- **400 Bad Request**: Malformed request
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource doesn't exist
- **422 Unprocessable Entity**: Validation failed
- **500 Internal Server Error**: Server error
