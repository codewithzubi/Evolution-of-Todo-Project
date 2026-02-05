# [Task]: T048, [From]: specs/001-task-crud-api/spec.md#User-Story-6-Delete
# [From]: specs/001-task-crud-api/plan.md#Phase-8-User-Story-6
"""
Integration tests for DELETE /api/{user_id}/tasks/{task_id} endpoint (Delete Task).

Verifies:
- Hard delete: Task completely removed from database
- Task no longer retrievable after delete (GET returns 404)
- User isolation: Cannot delete another user's task (403)
- Multiple deletes: First succeeds (204), second fails (404)
- Database consistency: No orphaned records
- Other user's tasks unaffected by deletion
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from src.config import settings
from fastapi.testclient import TestClient
from jose import jwt


@pytest.mark.asyncio
class TestDeleteTaskBasicFunctionality:
    """Test basic task deletion functionality."""

    async def test_delete_task_returns_204_no_content(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that DELETE returns 204 No Content on successful deletion."""
        # [Task]: T048, [From]: specs/001-task-crud-api/spec.md#User-Story-6-Delete
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={
                "title": "Task to delete",
                "description": "This will be deleted",
            },
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
        assert response.text == "" or response.text is None

    async def test_delete_task_removes_from_database(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that deleted task is completely removed from database."""
        # [Task]: T048, [From]: specs/001-task-crud-api/spec.md#User-Story-6-Delete
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task for hard delete"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Delete the task
        delete_response = client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert delete_response.status_code == 204

        # Verify task is no longer retrievable
        get_response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404
        data = get_response.json()
        assert data["error"]["code"] == "NOT_FOUND"

    async def test_delete_task_no_longer_in_list(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that deleted task no longer appears in list endpoint."""
        # [Task]: T048, [From]: specs/001-task-crud-api/spec.md#User-Story-6-Delete
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task to be deleted"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Verify task appears in list
        list_response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert list_response.status_code == 200
        task_ids = [task["id"] for task in list_response.json()["data"]["items"]]
        assert task_id in task_ids

        # Delete the task
        delete_response = client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert delete_response.status_code == 204

        # Verify task no longer appears in list
        list_response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert list_response.status_code == 200
        task_ids = [task["id"] for task in list_response.json()["data"]["items"]]
        assert task_id not in task_ids


@pytest.mark.asyncio
class TestDeleteTaskOwnership:
    """Test ownership verification and access control."""

    async def test_delete_task_other_user_returns_403(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that deleting another user's task returns 403 Forbidden."""
        # [Task]: T048, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create a task for first user
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "User 1 private task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Create different user's JWT
        other_user_id = uuid4()
        payload = {
            "user_id": str(other_user_id),
            "email": f"{other_user_id}@example.com",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24),
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        other_auth_headers = {"Authorization": f"Bearer {token}"}

        # Try to delete first user's task as second user
        response = client.delete(
            f"/api/{other_user_id}/tasks/{task_id}",
            headers=other_auth_headers,
        )
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "FORBIDDEN"

        # Verify original task still exists for first user
        verify_response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert verify_response.status_code == 200

    async def test_delete_task_does_not_affect_other_users_tasks(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that deleting one user's task doesn't affect other users' tasks."""
        # [Task]: T048, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task for user 1
        user1_task_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "User 1 task"},
            headers=auth_headers,
        )
        assert user1_task_response.status_code == 201
        user1_task_id = user1_task_response.json()["data"]["id"]

        # Create task for user 2
        other_user_id = uuid4()
        payload = {
            "user_id": str(other_user_id),
            "email": f"{other_user_id}@example.com",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24),
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        other_auth_headers = {"Authorization": f"Bearer {token}"}

        user2_task_response = client.post(
            f"/api/{other_user_id}/tasks",
            json={"title": "User 2 task"},
            headers=other_auth_headers,
        )
        assert user2_task_response.status_code == 201
        user2_task_id = user2_task_response.json()["data"]["id"]

        # Delete user 1's task
        delete_response = client.delete(
            f"/api/{test_user_id}/tasks/{user1_task_id}",
            headers=auth_headers,
        )
        assert delete_response.status_code == 204

        # Verify user 2's task still exists
        verify_response = client.get(
            f"/api/{other_user_id}/tasks/{user2_task_id}",
            headers=other_auth_headers,
        )
        assert verify_response.status_code == 200
        assert verify_response.json()["data"]["id"] == user2_task_id


@pytest.mark.asyncio
class TestDeleteTaskIdempotency:
    """Test idempotency behavior (or lack thereof) for delete."""

    async def test_delete_task_twice_second_returns_404(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that deleting same task twice returns 404 second time."""
        # [Task]: T048, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task for double delete"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Delete the task first time
        first_delete = client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert first_delete.status_code == 204

        # Delete the task second time (should return 404)
        second_delete = client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert second_delete.status_code == 404
        data = second_delete.json()
        assert data["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
class TestDeleteTaskNotFoundScenarios:
    """Test 404 scenarios."""

    async def test_delete_task_nonexistent_task_returns_404(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that deleting non-existent task_id returns 404."""
        # [Task]: T048, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        nonexistent_id = str(uuid4())

        response = client.delete(
            f"/api/{test_user_id}/tasks/{nonexistent_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"
        assert data["data"] is None


@pytest.mark.asyncio
class TestDeleteTaskValidation:
    """Test input validation."""

    async def test_delete_task_uuid_format_validation(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that invalid UUID format returns 422."""
        # [Task]: T048, [From]: specs/001-task-crud-api/spec.md#UUID-Validation
        response = client.delete(
            f"/api/{test_user_id}/tasks/not-a-uuid",
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"

    async def test_delete_task_partial_uuid_format(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that partial UUID format returns 422."""
        # [Task]: T048, [From]: specs/001-task-crud-api/spec.md#UUID-Validation
        response = client.delete(
            f"/api/{test_user_id}/tasks/123e4567-e89b-12d3-a456",
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
