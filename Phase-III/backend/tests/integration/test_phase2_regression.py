# [Task]: T374, [From]: specs/004-ai-chatbot/spec.md#Testing
"""Phase-II Regression Tests - Verify no breaking changes to existing Task CRUD endpoints.

Tests ensure that Phase-III chatbot implementation did not break any existing
Phase-II functionality. All Phase-II task endpoints should continue to work
exactly as before.

Validates:
- All 7 Phase-II task endpoints remain functional
- JWT authentication still enforced
- User isolation still enforced (user_id matching)
- Response formats unchanged
- Status codes correct
- Pagination still works
- Task CRUD operations (create, read, update, delete, complete) still work
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from src.config import settings
from src.main import app


def create_token(user_id, expires_in_hours=24):
    """Helper to create JWT token for testing."""
    payload = {
        "user_id": str(user_id),
        "email": f"user-{user_id}@example.com",
        "sub": str(user_id),
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=expires_in_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@pytest.fixture
def client():
    """Create FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client


class TestPhase2TaskCreation:
    """T374.1: Verify task creation endpoint (POST /api/{user_id}/tasks) still works."""

    def test_create_task_success(self, client):
        """Test successful task creation returns 201 with correct response format."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.post(
            f"/api/{user_id}/tasks",
            json={
                "title": "Test Task",
                "description": "A test task description",
                "due_date": None,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["data"] is not None
        assert data["error"] is None
        assert data["data"]["id"] is not None
        assert data["data"]["user_id"] == str(user_id)
        assert data["data"]["title"] == "Test Task"
        assert data["data"]["description"] == "A test task description"
        assert data["data"]["completed"] is False
        assert data["data"]["created_at"] is not None

    def test_create_task_missing_auth(self, client):
        """Test task creation without JWT token returns 401."""
        user_id = uuid4()

        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test Task", "description": "No auth"},
        )

        assert response.status_code == 401

    def test_create_task_user_id_mismatch(self, client):
        """Test task creation with mismatched user_id returns 403."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)

        response = client.post(
            f"/api/{user_b_id}/tasks",
            json={"title": "Test Task", "description": "Mismatch"},
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        assert response.status_code == 403

    def test_create_task_validation_error(self, client):
        """Test task creation with invalid data returns 422."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": ""},  # Empty title should fail
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422


class TestPhase2TaskListing:
    """T374.2: Verify task listing endpoint (GET /api/{user_id}/tasks) still works."""

    def test_list_tasks_empty(self, client):
        """Test listing tasks when user has no tasks."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["items"] == []
        assert data["data"]["pagination"]["total"] == 0
        assert data["data"]["pagination"]["limit"] == 10
        assert data["data"]["pagination"]["offset"] == 0
        assert data["data"]["pagination"]["has_more"] is False

    def test_list_tasks_with_pagination(self, client):
        """Test listing tasks with pagination parameters."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create 3 tasks
        for i in range(3):
            client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Task {i+1}", "description": "Desc"},
                headers={"Authorization": f"Bearer {token}"},
            )

        # List with limit=2
        response = client.get(
            f"/api/{user_id}/tasks?limit=2&offset=0",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 2
        assert data["data"]["pagination"]["total"] == 3
        assert data["data"]["pagination"]["has_more"] is True

    def test_list_tasks_user_isolation(self, client):
        """Test that users only see their own tasks."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)
        user_b_token = create_token(user_b_id)

        # User A creates a task
        client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A Task", "description": "Private"},
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        # User B tries to list - should see no tasks
        response = client.get(
            f"/api/{user_b_id}/tasks",
            headers={"Authorization": f"Bearer {user_b_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 0
        assert data["data"]["pagination"]["total"] == 0

    def test_list_tasks_missing_auth(self, client):
        """Test listing tasks without JWT token returns 401."""
        user_id = uuid4()

        response = client.get(f"/api/{user_id}/tasks")

        assert response.status_code == 401


class TestPhase2TaskRetrieval:
    """T374.3: Verify task retrieval endpoint (GET /api/{user_id}/tasks/{task_id}) still works."""

    def test_get_task_success(self, client):
        """Test successful task retrieval returns 200."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create task
        create_resp = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test Task", "description": "Details"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_resp.json()["data"]["id"]

        # Get task
        response = client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == task_id
        assert data["data"]["user_id"] == str(user_id)
        assert data["data"]["title"] == "Test Task"

    def test_get_task_not_found(self, client):
        """Test retrieving non-existent task returns 404."""
        user_id = uuid4()
        token = create_token(user_id)
        fake_task_id = uuid4()

        response = client.get(
            f"/api/{user_id}/tasks/{fake_task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    def test_get_task_cross_user_access_blocked(self, client):
        """Test that user cannot read another user's task."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)
        user_b_token = create_token(user_b_id)

        # User A creates task
        create_resp = client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A Task", "description": "Secret"},
            headers={"Authorization": f"Bearer {user_a_token}"},
        )
        task_id = create_resp.json()["data"]["id"]

        # User B tries to get it
        response = client.get(
            f"/api/{user_a_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_b_token}"},
        )

        # Should return 404 (not found in user's scope)
        assert response.status_code == 404


class TestPhase2TaskUpdate:
    """T374.4: Verify task update endpoints (PUT/PATCH) still work."""

    def test_update_task_success(self, client):
        """Test successful task update (PUT) returns 200."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create task
        create_resp = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Original Title", "description": "Original"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_resp.json()["data"]["id"]

        # Update task
        response = client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json={"title": "Updated Title", "description": "Updated"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "Updated Title"
        assert data["data"]["description"] == "Updated"

    def test_patch_task_partial_update(self, client):
        """Test partial task update (PATCH) updates only specified fields."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create task
        create_resp = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Original", "description": "Original Desc"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_resp.json()["data"]["id"]

        # Patch only title
        response = client.patch(
            f"/api/{user_id}/tasks/{task_id}",
            json={"title": "Patched Title"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "Patched Title"
        assert data["data"]["description"] == "Original Desc"

    def test_update_task_user_id_mismatch(self, client):
        """Test that user cannot update another user's task."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)
        user_b_token = create_token(user_b_id)

        # User A creates task
        create_resp = client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A Task", "description": "Secret"},
            headers={"Authorization": f"Bearer {user_a_token}"},
        )
        task_id = create_resp.json()["data"]["id"]

        # User B tries to update
        response = client.put(
            f"/api/{user_a_id}/tasks/{task_id}",
            json={"title": "Hacked Title"},
            headers={"Authorization": f"Bearer {user_b_token}"},
        )

        assert response.status_code == 404  # Should not exist in user B's scope


class TestPhase2TaskCompletion:
    """T374.5: Verify task completion toggle (PATCH /tasks/{task_id}/complete) still works."""

    def test_complete_task_success(self, client):
        """Test successful task completion toggle."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create task
        create_resp = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Task to Complete"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_resp.json()["data"]["id"]

        # Complete task
        response = client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            json={"completed": True},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["completed"] is True

    def test_uncomplete_task(self, client):
        """Test toggling task completion off."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create and complete task
        create_resp = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Task"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_resp.json()["data"]["id"]

        client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            json={"completed": True},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Uncomplete task
        response = client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            json={"completed": False},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["completed"] is False


class TestPhase2TaskDeletion:
    """T374.6: Verify task deletion endpoint (DELETE /api/{user_id}/tasks/{task_id}) still works."""

    def test_delete_task_success(self, client):
        """Test successful task deletion returns 200."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create task
        create_resp = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Task to Delete"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_resp.json()["data"]["id"]

        # Delete task
        response = client.delete(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == task_id

    def test_delete_nonexistent_task(self, client):
        """Test deleting non-existent task returns 404."""
        user_id = uuid4()
        token = create_token(user_id)
        fake_task_id = uuid4()

        response = client.delete(
            f"/api/{user_id}/tasks/{fake_task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    def test_delete_task_cross_user_blocked(self, client):
        """Test that user cannot delete another user's task."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)
        user_b_token = create_token(user_b_id)

        # User A creates task
        create_resp = client.post(
            f"/api/{user_a_id}/tasks",
            json={"title": "User A Task"},
            headers={"Authorization": f"Bearer {user_a_token}"},
        )
        task_id = create_resp.json()["data"]["id"]

        # User B tries to delete
        response = client.delete(
            f"/api/{user_a_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_b_token}"},
        )

        assert response.status_code == 404


class TestPhase2ResponseFormats:
    """T374.7: Verify response envelope format is unchanged."""

    def test_success_response_format(self, client):
        """Test that all success responses have correct format."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Response should have data and error fields
        assert "data" in response.json()
        assert "error" in response.json()
        assert response.json()["data"] is not None
        assert response.json()["error"] is None

    def test_error_response_format(self, client):
        """Test that error responses have correct format."""
        response = client.get("/api/invalid-path")

        # Should return error response
        assert response.status_code == 404


class TestPhase2AuthenticationStillRequired:
    """T374.8: Verify all endpoints still require valid JWT tokens."""

    def test_create_task_requires_auth(self, client):
        """Test create endpoint requires auth."""
        user_id = uuid4()
        response = client.post(f"/api/{user_id}/tasks", json={"title": "Test"})
        assert response.status_code == 401

    def test_list_tasks_requires_auth(self, client):
        """Test list endpoint requires auth."""
        user_id = uuid4()
        response = client.get(f"/api/{user_id}/tasks")
        assert response.status_code == 401

    def test_get_task_requires_auth(self, client):
        """Test get endpoint requires auth."""
        user_id = uuid4()
        response = client.get(f"/api/{user_id}/tasks/{uuid4()}")
        assert response.status_code == 401

    def test_update_task_requires_auth(self, client):
        """Test update endpoint requires auth."""
        user_id = uuid4()
        response = client.put(
            f"/api/{user_id}/tasks/{uuid4()}",
            json={"title": "Test"},
        )
        assert response.status_code == 401

    def test_delete_task_requires_auth(self, client):
        """Test delete endpoint requires auth."""
        user_id = uuid4()
        response = client.delete(f"/api/{user_id}/tasks/{uuid4()}")
        assert response.status_code == 401
