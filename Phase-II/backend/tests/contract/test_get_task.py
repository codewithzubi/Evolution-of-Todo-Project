# [Task]: T030, [From]: specs/001-task-crud-api/spec.md#User-Story-3-View
# [From]: specs/001-task-crud-api/plan.md#Phase-5-User-Story-3
"""
Contract tests for GET /api/{user_id}/tasks/{task_id} endpoint (View Task Detail).

Verifies:
- Response schema validation (includes all task fields)
- HTTP status codes (200, 401, 403, 404)
- Authentication and authorization enforcement
- Error response formats
- UUID format validation
"""

from uuid import uuid4

from fastapi.testclient import TestClient


class TestGetTaskRequestSchema:
    """Test GET request schema and parameter validation."""

    def test_get_task_with_valid_task_id_returns_200(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test GET request with valid task_id returns 200 OK."""
        # [Task]: T030, [From]: specs/001-task-crud-api/spec.md#User-Story-3-View
        # Create a task first
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task for retrieval"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Now get the task
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_get_task_invalid_uuid_format_returns_400(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that malformed UUID format returns 400 Bad Request."""
        # [Task]: T030, [From]: specs/001-task-crud-api/spec.md#Error-Handling
        response = client.get(
            f"/api/{test_user_id}/tasks/invalid-uuid-format",
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestGetTaskResponseSchema:
    """Test response schema and field validation."""

    def test_get_task_response_includes_all_required_fields(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test response includes all task fields."""
        # [Task]: T030, [From]: specs/001-task-crud-api/spec.md#Task-Response-Fields
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task with all fields"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Get the task
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "data" in data
        assert "error" in data
        assert data["error"] is None

        # Verify all task fields
        task = data["data"]
        assert "id" in task
        assert "user_id" in task
        assert "title" in task
        assert "description" in task
        assert "due_date" in task
        assert "completed" in task
        assert "completed_at" in task
        assert "created_at" in task
        assert "updated_at" in task

    def test_get_task_response_has_correct_data_types(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that response fields have correct data types."""
        # [Task]: T030, [From]: specs/001-task-crud-api/spec.md#Task-Response-Fields
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Type test task", "description": "Test description"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Get the task
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        task = response.json()["data"]

        # Verify types
        assert isinstance(task["id"], str)
        assert isinstance(task["user_id"], str)
        assert isinstance(task["title"], str)
        assert task["description"] is None or isinstance(task["description"], str)
        assert task["due_date"] is None or isinstance(task["due_date"], str)
        assert isinstance(task["completed"], bool)
        assert task["completed_at"] is None or isinstance(task["completed_at"], str)
        assert isinstance(task["created_at"], str)
        assert isinstance(task["updated_at"], str)


class TestGetTaskAuthentication:
    """Test authentication and authorization for get endpoint."""

    def test_get_task_missing_jwt_returns_401(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that missing JWT returns 401 Unauthorized."""
        # [Task]: T030, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to get without JWT
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            # No Authorization header
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"

    def test_get_task_invalid_jwt_returns_401(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
        invalid_auth_headers: dict,
    ):
        """Test that invalid JWT returns 401 Unauthorized."""
        # [Task]: T030, [From]: specs/001-task-crud-api/spec.md#JWT-Token-Requirements
        # Create a task with valid JWT
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to get with invalid JWT
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=invalid_auth_headers,
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"

    def test_get_task_mismatched_user_id_returns_403(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
        mismatched_auth_headers: dict,
    ):
        """Test that mismatched user_id in JWT returns 403 Forbidden."""
        # [Task]: T030, [From]: specs/001-task-crud-api/spec.md#Authorization-Rules
        # Create a task with first user
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to get with mismatched user_id
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=mismatched_auth_headers,
        )
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "FORBIDDEN"


class TestGetTaskNotFound:
    """Test 404 Not Found scenarios."""

    def test_get_task_nonexistent_returns_404(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that non-existent task_id returns 404 Not Found."""
        # [Task]: T030, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        nonexistent_task_id = str(uuid4())

        response = client.get(
            f"/api/{test_user_id}/tasks/{nonexistent_task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"

    def test_get_task_error_response_format(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test error response format for 404."""
        # [Task]: T030, [From]: specs/001-task-crud-api/spec.md#Error-Response
        nonexistent_task_id = str(uuid4())

        response = client.get(
            f"/api/{test_user_id}/tasks/{nonexistent_task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404
        data = response.json()

        # Verify error response structure
        assert "data" in data
        assert "error" in data
        assert data["data"] is None
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert data["error"]["code"] == "NOT_FOUND"
