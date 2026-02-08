# [Task]: T042, [From]: specs/001-task-crud-api/spec.md#User-Story-5-Mark-Complete
# [From]: specs/001-task-crud-api/plan.md#Phase-7-User-Story-5
"""
Contract tests for PATCH endpoint for marking tasks as complete.

Verifies:
- PATCH /api/{user_id}/tasks/{task_id}/complete: Toggle completion status
- Request schema validation (completed field is boolean)
- Response schema validation (200 OK response with updated task)
- HTTP status codes (200, 401, 403, 404, 422)
- Error response formats
- Completion timestamp handling (sets completed_at when complete, clears when incomplete)
"""

from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient


class TestMarkCompleteTaskPATCH:
    """Test PATCH /api/{user_id}/tasks/{task_id}/complete for toggling completion."""

    def test_patch_complete_incomplete_task_returns_200(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH /complete on incomplete task returns 200 with completed=true."""
        # [Task]: T042, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial incomplete task
        create_payload = {
            "title": "Task to complete",
            "description": "Complete this task",
            "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        }
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json=create_payload,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]
        initial_completed = create_response.json()["data"]["completed"]
        assert initial_completed is False

        # Mark as complete with PATCH
        complete_payload = {"completed": True}
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json=complete_payload,
            headers=auth_headers,
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["data"]["completed"] is True
        assert data["data"]["completed_at"] is not None

    def test_patch_complete_task_back_to_incomplete_returns_200(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH /complete on complete task returns 200 with completed=false."""
        # [Task]: T042, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task and mark it complete
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task to uncomplete"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Mark as complete
        client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={"completed": True},
            headers=auth_headers,
        )

        # Mark back as incomplete
        uncomplete_payload = {"completed": False}
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json=uncomplete_payload,
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["completed"] is False
        assert data["data"]["completed_at"] is None

    def test_patch_complete_response_includes_all_fields(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH /complete response includes all required TaskResponse fields."""
        # [Task]: T042, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Complete me", "description": "A test task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Mark as complete
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={"completed": True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()["data"]

        # Verify all required fields present
        assert "id" in data
        assert "user_id" in data
        assert "title" in data
        assert "description" in data
        assert "due_date" in data
        assert "completed" in data
        assert "completed_at" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_patch_complete_with_invalid_body_returns_422(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH /complete with invalid body returns 422."""
        # [Task]: T042, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task to complete"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to mark complete with invalid body (missing completed field)
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={},  # Missing completed field
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"


class TestMarkCompleteTaskAuthentication:
    """Test authentication and authorization for mark complete endpoint."""

    def test_patch_complete_missing_jwt_returns_401(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH /complete without JWT returns 401."""
        # [Task]: T042, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task to complete"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to mark complete without JWT
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={"completed": True},
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"

    def test_patch_complete_other_user_task_returns_403(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
        mismatched_auth_headers: dict,
    ):
        """Test PATCH /complete other user's task returns 403."""
        # [Task]: T042, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task with user 1
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "User 1 task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to mark complete as user 2
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={"completed": True},
            headers=mismatched_auth_headers,
        )
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "FORBIDDEN"


class TestMarkCompleteTaskNotFound:
    """Test 404 responses for mark complete endpoint."""

    def test_patch_complete_nonexistent_task_returns_404(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH /complete nonexistent task returns 404."""
        # [Task]: T042, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        nonexistent_task_id = uuid4()
        response = client.patch(
            f"/api/{test_user_id}/tasks/{nonexistent_task_id}/complete",
            json={"completed": True},
            headers=auth_headers,
        )
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"
