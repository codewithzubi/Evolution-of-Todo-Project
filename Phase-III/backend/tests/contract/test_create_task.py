# [Task]: T017, [From]: specs/001-task-crud-api/spec.md#User-Story-1-Create
# [From]: specs/001-task-crud-api/plan.md#Phase-3-User-Story-1
"""
Contract tests for POST /api/{user_id}/tasks endpoint (Create Task).

Verifies:
- Request schema validation (POST request body)
- Response schema validation (201 Created response)
- HTTP status codes (201, 401, 403, 422)
- Error response formats
- Request/response structure compliance with spec
"""

from datetime import datetime, timedelta

from fastapi.testclient import TestClient


class TestCreateTaskRequestSchema:
    """Test POST request schema validation."""

    def test_create_task_with_title_only(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test creating task with title only (description and due_date optional)."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        payload = {
            "title": "Complete project documentation",
        }
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert data["data"]["title"] == "Complete project documentation"
        assert data["data"]["description"] is None
        assert data["data"]["due_date"] is None

    def test_create_task_with_all_fields(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test creating task with all fields provided."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        due_date = (datetime.utcnow() + timedelta(days=5)).isoformat() + "Z"
        payload = {
            "title": "Complete project documentation",
            "description": "Write comprehensive API docs for all endpoints",
            "due_date": due_date,
        }
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["title"] == "Complete project documentation"
        assert (
            data["data"]["description"]
            == "Write comprehensive API docs for all endpoints"
        )
        assert data["data"]["due_date"] is not None

    def test_create_task_missing_title_returns_422(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that missing title returns 422 Unprocessable Entity."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        payload = {
            "description": "Some description without title",
        }
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert data["data"] is None
        assert data["error"]["details"] is not None
        assert "title" in data["error"]["details"]

    def test_create_task_empty_title_returns_422(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that empty title returns 422 Unprocessable Entity."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#Requirements
        payload = {
            "title": "",
        }
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "title" in data["error"]["details"]

    def test_create_task_title_too_long_returns_422(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that title exceeding 255 chars returns 422."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#Requirements
        payload = {
            "title": "x" * 256,  # Exceeds 255 char limit
        }
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert "title" in data["error"]["details"]

    def test_create_task_description_too_long_returns_422(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that description exceeding 2000 chars returns 422."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#Requirements
        payload = {
            "title": "Valid title",
            "description": "x" * 2001,  # Exceeds 2000 char limit
        }
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert "description" in data["error"]["details"]

    def test_create_task_invalid_due_date_format_returns_422(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that invalid ISO 8601 due_date returns 422."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#Requirements
        payload = {
            "title": "Valid title",
            "due_date": "not-a-valid-date",
        }
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert "due_date" in data["error"]["details"]


class TestCreateTaskResponseSchema:
    """Test response schema and HTTP status codes."""

    def test_create_task_returns_201_status(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that successful creation returns 201 Created status."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#Create-Task-Response
        payload = {"title": "Test task"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 201

    def test_create_task_response_has_required_fields(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test response contains all required fields per spec."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#Create-Task-Response
        payload = {"title": "Test task"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()

        # Verify wrapper structure
        assert "data" in data
        assert "error" in data
        assert data["error"] is None

        # Verify task fields
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

    def test_create_task_response_has_correct_user_id(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test response user_id matches authenticated user."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#Authorization-Rules
        payload = {"title": "Test task"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 201
        task = response.json()["data"]
        assert str(task["user_id"]) == str(test_user_id)

    def test_create_task_response_has_unique_id(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test response contains unique task ID."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#Create-Task-Response
        payload = {"title": "Test task"}
        response1 = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        response2 = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response1.status_code == 201
        assert response2.status_code == 201

        task1_id = response1.json()["data"]["id"]
        task2_id = response2.json()["data"]["id"]
        assert task1_id != task2_id

    def test_create_task_response_has_timestamps(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test response includes created_at and updated_at timestamps."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#Requirements
        payload = {"title": "Test task"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        task = response.json()["data"]
        assert task["created_at"] is not None
        assert task["updated_at"] is not None
        assert task["completed"] is False
        assert task["completed_at"] is None

    def test_create_task_response_completed_defaults_false(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that new tasks have completed=False by default."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#Key-Entities
        payload = {"title": "Test task"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        task = response.json()["data"]
        assert task["completed"] is False
        assert task["completed_at"] is None


class TestCreateTaskAuthentication:
    """Test authentication and authorization for create endpoint."""

    def test_create_task_missing_jwt_returns_401(
        self,
        client: TestClient,
        test_user_id,
    ):
        """Test that missing JWT returns 401 Unauthorized."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        payload = {"title": "Test task"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            # No Authorization header
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"
        assert data["data"] is None

    def test_create_task_invalid_jwt_returns_401(
        self,
        client: TestClient,
        test_user_id,
        invalid_auth_headers: dict,
    ):
        """Test that invalid JWT returns 401 Unauthorized."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#JWT-Token-Requirements
        payload = {"title": "Test task"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=invalid_auth_headers,
        )
        assert response.status_code == 401

    def test_create_task_mismatched_user_id_returns_403(
        self,
        client: TestClient,
        test_user_id,
        mismatched_auth_headers: dict,
    ):
        """Test that mismatched user_id in JWT returns 403 Forbidden."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#Authorization-Rules
        payload = {"title": "Test task"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=mismatched_auth_headers,
        )
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "FORBIDDEN"
        assert data["data"] is None

    def test_create_task_missing_auth_header_returns_401(
        self,
        client: TestClient,
        test_user_id,
    ):
        """Test that missing Authorization header returns 401."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#JWT-Token-Requirements
        payload = {"title": "Test task"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers={},
        )
        assert response.status_code == 401

    def test_create_task_invalid_auth_scheme_returns_401(
        self,
        client: TestClient,
        test_user_id,
    ):
        """Test that invalid auth scheme (not Bearer) returns 401."""
        # [Task]: T017, [From]: specs/001-task-crud-api/spec.md#JWT-Token-Requirements
        payload = {"title": "Test task"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers={"Authorization": "Basic invalid"},
        )
        assert response.status_code == 401
