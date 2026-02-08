# [Task]: T031, [From]: specs/001-task-crud-api/spec.md#User-Story-3-View
# [From]: specs/001-task-crud-api/plan.md#Phase-5-User-Story-3
"""
Integration tests for GET /api/{user_id}/tasks/{task_id} endpoint (View Task Detail).

Verifies:
- Single task retrieval with full details
- User_id ownership enforcement (403 for other users' tasks)
- 404 for non-existent tasks
- UUID format validation
- All fields returned in response
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from src.config import settings
from fastapi.testclient import TestClient
from jose import jwt


@pytest.mark.asyncio
class TestGetTaskBasicFunctionality:
    """Test basic single task retrieval."""

    async def test_get_task_returns_own_task(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test retrieving own task returns complete details."""
        # [Task]: T031, [From]: specs/001-task-crud-api/spec.md#User-Story-3-View
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={
                "title": "Complete project documentation",
                "description": "Write comprehensive API docs",
                "due_date": "2026-02-15T17:00:00Z",
            },
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        created_task = create_response.json()["data"]
        task_id = created_task["id"]

        # Get the task
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        retrieved_task = response.json()["data"]

        # Verify all fields match
        assert retrieved_task["id"] == created_task["id"]
        assert retrieved_task["user_id"] == created_task["user_id"]
        assert retrieved_task["title"] == created_task["title"]
        assert retrieved_task["description"] == created_task["description"]
        assert retrieved_task["due_date"] == created_task["due_date"]
        assert retrieved_task["completed"] == created_task["completed"]
        assert retrieved_task["completed_at"] == created_task["completed_at"]
        assert retrieved_task["created_at"] == created_task["created_at"]
        assert retrieved_task["updated_at"] == created_task["updated_at"]

    async def test_get_task_with_minimal_fields(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test retrieving task with only required title."""
        # [Task]: T031, [From]: specs/001-task-crud-api/spec.md#User-Story-3-View
        # Create task with minimal fields
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Minimal task"},
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

        # Verify fields
        assert task["title"] == "Minimal task"
        assert task["description"] is None
        assert task["due_date"] is None
        assert task["completed"] is False
        assert task["completed_at"] is None

    async def test_get_task_returns_all_fields(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that all required fields are returned."""
        # [Task]: T031, [From]: specs/001-task-crud-api/spec.md#User-Story-3-View
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Complete task"},
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

        # Verify all fields present
        required_fields = [
            "id",
            "user_id",
            "title",
            "description",
            "due_date",
            "completed",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        for field in required_fields:
            assert field in task, f"Missing field: {field}"


@pytest.mark.asyncio
class TestGetTaskOwnership:
    """Test ownership verification and access control."""

    async def test_get_task_other_user_returns_403(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that requesting another user's task returns 403 Forbidden."""
        # [Task]: T031, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
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

        # Try to get first user's task as second user
        response = client.get(
            f"/api/{other_user_id}/tasks/{task_id}",
            headers=other_auth_headers,
        )
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "FORBIDDEN"

    async def test_get_task_user_id_path_validation(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
        mismatched_auth_headers: dict,
    ):
        """Test that URL user_id must match JWT user_id."""
        # [Task]: T031, [From]: specs/001-task-crud-api/spec.md#Authorization-Rules
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try with mismatched user_id in path
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=mismatched_auth_headers,
        )
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "FORBIDDEN"


@pytest.mark.asyncio
class TestGetTaskNotFoundScenarios:
    """Test 404 scenarios."""

    async def test_get_task_nonexistent_task_returns_404(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that non-existent task_id returns 404."""
        # [Task]: T031, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        nonexistent_id = str(uuid4())

        response = client.get(
            f"/api/{test_user_id}/tasks/{nonexistent_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"
        assert data["data"] is None



@pytest.mark.asyncio
class TestGetTaskValidation:
    """Test input validation."""

    async def test_get_task_uuid_format_validation(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that invalid UUID format returns 422."""
        # [Task]: T031, [From]: specs/001-task-crud-api/spec.md#UUID-Validation
        response = client.get(
            f"/api/{test_user_id}/tasks/not-a-uuid",
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"

    async def test_get_task_uuid_format_partial_uuid(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that partial UUID format returns 422."""
        # [Task]: T031, [From]: specs/001-task-crud-api/spec.md#UUID-Validation
        response = client.get(
            f"/api/{test_user_id}/tasks/123e4567-e89b-12d3-a456",
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
