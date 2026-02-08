# [Task]: T047, [From]: specs/001-task-crud-api/spec.md#User-Story-6-Delete
# [From]: specs/001-task-crud-api/plan.md#Phase-8-User-Story-6
"""
Contract tests for DELETE /api/{user_id}/tasks/{task_id} endpoint (Delete Task).

Verifies:
- Response status code (204 No Content)
- Response body is empty (no content)
- HTTP status codes (204, 401, 403, 404)
- Authentication and authorization enforcement
- Error response formats
- UUID format validation
"""

from uuid import uuid4

from fastapi.testclient import TestClient


class TestDeleteTaskRequestSchema:
    """Test DELETE request schema and parameter validation."""

    def test_delete_task_with_valid_task_id_returns_204(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test DELETE request with valid task_id returns 204 No Content."""
        # [Task]: T047, [From]: specs/001-task-crud-api/spec.md#User-Story-6-Delete
        # Create a task first
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task for deletion"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Now delete the task
        response = client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

    def test_delete_task_response_body_is_empty(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that DELETE response has no content (empty body)."""
        # [Task]: T047, [From]: specs/001-task-crud-api/spec.md#User-Story-6-Delete
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task for deletion"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Delete the task
        response = client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204
        # Response should have no content
        assert response.text == "" or response.text is None or len(response.text) == 0

    def test_delete_task_invalid_uuid_format_returns_422(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that malformed UUID format returns 422 Unprocessable Entity."""
        # [Task]: T047, [From]: specs/001-task-crud-api/spec.md#Error-Handling
        response = client.delete(
            f"/api/{test_user_id}/tasks/invalid-uuid-format",
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestDeleteTaskAuthentication:
    """Test authentication and authorization for delete endpoint."""

    def test_delete_task_missing_jwt_returns_401(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that missing JWT returns 401 Unauthorized."""
        # [Task]: T047, [From]: specs/001-task-crud-api/spec.md#JWT-Token-Requirements
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to delete without JWT
        response = client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            # No Authorization header
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"

    def test_delete_task_invalid_jwt_returns_401(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
        invalid_auth_headers: dict,
    ):
        """Test that invalid JWT returns 401 Unauthorized."""
        # [Task]: T047, [From]: specs/001-task-crud-api/spec.md#JWT-Token-Requirements
        # Create a task with valid JWT
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to delete with invalid JWT
        response = client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=invalid_auth_headers,
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"

    def test_delete_task_mismatched_user_id_returns_403(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
        mismatched_auth_headers: dict,
    ):
        """Test that mismatched user_id in JWT returns 403 Forbidden."""
        # [Task]: T047, [From]: specs/001-task-crud-api/spec.md#Authorization-Rules
        # Create a task with first user
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to delete with mismatched user_id
        response = client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=mismatched_auth_headers,
        )
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "FORBIDDEN"

    def test_delete_task_other_user_task_returns_403(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
        mismatched_auth_headers: dict,
    ):
        """Test that trying to delete another user's task returns 403 Forbidden."""
        # [Task]: T047, [From]: specs/001-task-crud-api/spec.md#Authorization-Rules
        # Create a task for first user
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "User 1 private task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to delete from second user's perspective
        response = client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=mismatched_auth_headers,
        )
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "FORBIDDEN"


class TestDeleteTaskNotFound:
    """Test 404 Not Found scenarios."""

    def test_delete_task_nonexistent_returns_404(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that non-existent task_id returns 404 Not Found."""
        # [Task]: T047, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        nonexistent_task_id = str(uuid4())

        response = client.delete(
            f"/api/{test_user_id}/tasks/{nonexistent_task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"

    def test_delete_task_error_response_format(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test error response format for 404."""
        # [Task]: T047, [From]: specs/001-task-crud-api/spec.md#Error-Response
        nonexistent_task_id = str(uuid4())

        response = client.delete(
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
