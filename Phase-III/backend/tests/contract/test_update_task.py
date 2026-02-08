# [Task]: T035, [From]: specs/001-task-crud-api/spec.md#User-Story-4-Update
# [From]: specs/001-task-crud-api/plan.md#Phase-6-User-Story-4
"""
Contract tests for PUT/PATCH endpoints for updating tasks.

Verifies:
- PUT /api/{user_id}/tasks/{task_id}: Full update with all fields required
- PATCH /api/{user_id}/tasks/{task_id}: Partial update with optional fields
- Request schema validation (PUT vs PATCH)
- Response schema validation (200 OK response)
- HTTP status codes (200, 401, 403, 404, 422)
- Error response formats
- Request/response structure compliance with spec
"""

from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient


class TestUpdateTaskPUT:
    """Test PUT /api/{user_id}/tasks/{task_id} for full update."""

    def test_put_update_all_fields_returns_200(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PUT with all fields updates task and returns 200."""
        # [Task]: T035, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_payload = {
            "title": "Original title",
            "description": "Original description",
            "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        }
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json=create_payload,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Update with PUT (all fields required)
        update_payload = {
            "title": "Updated title",
            "description": "Updated description",
            "due_date": (datetime.utcnow() + timedelta(days=5)).isoformat() + "Z",
            "completed": False,
        }
        response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json=update_payload,
            headers=auth_headers,
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["data"]["title"] == "Updated title"
        assert data["data"]["description"] == "Updated description"
        assert data["data"]["completed"] is False

    def test_put_missing_required_field_returns_422(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PUT missing required field returns 422."""
        # [Task]: T035, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_payload = {
            "title": "Original title",
        }
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json=create_payload,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to update with PUT missing title (required in PUT)
        update_payload = {
            "description": "Updated description",
            "due_date": (datetime.utcnow() + timedelta(days=5)).isoformat() + "Z",
            "completed": False,
        }
        response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json=update_payload,
            headers=auth_headers,
        )
        # PUT should not accept missing required fields, but Pydantic will handle this
        # We expect 422 only if title is validated as required
        # For PUT, title IS required, so missing it should be 422
        # But the current TaskUpdate schema has title as required, so this will fail
        # at Pydantic level before hitting the endpoint
        assert response.status_code == 422

    def test_put_empty_title_returns_422(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PUT with empty title returns 422."""
        # [Task]: T035, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_payload = {
            "title": "Original title",
        }
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json=create_payload,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to update with empty title
        update_payload = {
            "title": "",
            "description": "Updated description",
            "due_date": (datetime.utcnow() + timedelta(days=5)).isoformat() + "Z",
            "completed": False,
        }
        response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json=update_payload,
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert data["data"] is None

    def test_put_invalid_date_format_returns_422(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PUT with invalid date format returns 422."""
        # [Task]: T035, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_payload = {
            "title": "Original title",
        }
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json=create_payload,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to update with invalid date
        update_payload = {
            "title": "Updated title",
            "description": "Updated description",
            "due_date": "not-a-date",
            "completed": False,
        }
        response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json=update_payload,
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestUpdateTaskPATCH:
    """Test PATCH /api/{user_id}/tasks/{task_id} for partial update."""

    def test_patch_single_field_returns_200(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH with single field updates only that field and returns 200."""
        # [Task]: T035, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_payload = {
            "title": "Original title",
            "description": "Original description",
            "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        }
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json=create_payload,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]
        original_desc = create_response.json()["data"]["description"]

        # Update only title with PATCH
        update_payload = {
            "title": "Updated title",
        }
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}",
            json=update_payload,
            headers=auth_headers,
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["data"]["title"] == "Updated title"
        assert data["data"]["description"] == original_desc

    def test_patch_multiple_fields_returns_200(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH with multiple fields updates only those fields."""
        # [Task]: T035, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_payload = {
            "title": "Original title",
            "description": "Original description",
            "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        }
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json=create_payload,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]
        original_due_date = create_response.json()["data"]["due_date"]

        # Update title and description with PATCH
        update_payload = {
            "title": "Updated title",
            "description": "Updated description",
        }
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}",
            json=update_payload,
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "Updated title"
        assert data["data"]["description"] == "Updated description"
        assert data["data"]["due_date"] == original_due_date

    def test_patch_no_fields_returns_200_noop(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH with no fields returns 200 (no-op)."""
        # [Task]: T035, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_payload = {
            "title": "Original title",
        }
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json=create_payload,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Update with empty PATCH (no fields)
        update_payload = {}
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}",
            json=update_payload,
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == task_id

    def test_patch_empty_title_returns_422(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH with empty title returns 422."""
        # [Task]: T035, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_payload = {
            "title": "Original title",
        }
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json=create_payload,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to update with empty title
        update_payload = {
            "title": "",
        }
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}",
            json=update_payload,
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestUpdateTaskAuthentication:
    """Test authentication and authorization for update endpoints."""

    def test_put_missing_jwt_returns_401(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PUT without JWT returns 401."""
        # [Task]: T035, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to update without JWT
        update_payload = {
            "title": "Updated title",
            "description": None,
            "due_date": None,
            "completed": False,
        }
        response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json=update_payload,
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"

    def test_patch_missing_jwt_returns_401(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH without JWT returns 401."""
        # [Task]: T035, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to update without JWT
        update_payload = {
            "title": "Updated title",
        }
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}",
            json=update_payload,
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"

    def test_put_other_user_task_returns_403(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
        mismatched_auth_headers: dict,
    ):
        """Test PUT other user's task returns 403."""
        # [Task]: T035, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task with user 1
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "User 1 task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to update as user 2
        update_payload = {
            "title": "Updated title",
            "description": None,
            "due_date": None,
            "completed": False,
        }
        response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json=update_payload,
            headers=mismatched_auth_headers,
        )
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "FORBIDDEN"

    def test_patch_other_user_task_returns_403(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
        mismatched_auth_headers: dict,
    ):
        """Test PATCH other user's task returns 403."""
        # [Task]: T035, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task with user 1
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "User 1 task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to update as user 2
        update_payload = {
            "title": "Updated title",
        }
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}",
            json=update_payload,
            headers=mismatched_auth_headers,
        )
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "FORBIDDEN"


class TestUpdateTaskNotFound:
    """Test 404 responses for update endpoints."""

    def test_put_nonexistent_task_returns_404(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PUT nonexistent task returns 404."""
        # [Task]: T035, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        nonexistent_task_id = uuid4()
        update_payload = {
            "title": "Updated title",
            "description": None,
            "due_date": None,
            "completed": False,
        }
        response = client.put(
            f"/api/{test_user_id}/tasks/{nonexistent_task_id}",
            json=update_payload,
            headers=auth_headers,
        )
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"

    def test_patch_nonexistent_task_returns_404(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH nonexistent task returns 404."""
        # [Task]: T035, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        nonexistent_task_id = uuid4()
        update_payload = {
            "title": "Updated title",
        }
        response = client.patch(
            f"/api/{test_user_id}/tasks/{nonexistent_task_id}",
            json=update_payload,
            headers=auth_headers,
        )
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"
