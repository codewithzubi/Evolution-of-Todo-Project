# [Task]: T043, [From]: specs/001-task-crud-api/spec.md#User-Story-5-Mark-Complete
# [From]: specs/001-task-crud-api/plan.md#Phase-7-User-Story-5
"""
Integration tests for PATCH endpoint for marking tasks as complete.

Verifies:
- Marking incomplete task as complete sets completed=true and completed_at to current time
- Marking complete task as incomplete sets completed=false and clears completed_at
- completed_at timestamp accuracy (within 1 second of current time)
- Multiple toggle cycles work correctly
- User isolation enforced
- Other task fields unchanged during completion toggle
- Database persistence verified
"""

import time
from datetime import datetime, timedelta

from fastapi.testclient import TestClient


class TestMarkCompleteToggleBehavior:
    """Integration tests for toggling task completion status."""

    def test_mark_incomplete_task_as_complete_sets_completed_at(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test marking incomplete task as complete sets completed_at timestamp."""
        # [Task]: T043, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task (initially incomplete)
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task to complete"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]
        create_time = datetime.utcnow()

        # Mark as complete
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={"completed": True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()["data"]

        # Verify completed status and timestamp
        assert data["completed"] is True
        assert data["completed_at"] is not None

        # Verify timestamp is reasonable (within 2 seconds of create time)
        completed_at = datetime.fromisoformat(data["completed_at"].replace("Z", "+00:00"))
        assert (completed_at - create_time).total_seconds() >= 0
        assert (completed_at - create_time).total_seconds() < 2

    def test_mark_complete_task_as_incomplete_clears_completed_at(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test marking complete task as incomplete clears completed_at."""
        # [Task]: T043, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task and mark complete
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task to uncomplete"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Mark complete
        client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={"completed": True},
            headers=auth_headers,
        )

        # Mark incomplete
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={"completed": False},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()["data"]

        # Verify completed_at is cleared
        assert data["completed"] is False
        assert data["completed_at"] is None

    def test_mark_complete_toggle_cycle(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test toggling completion multiple times works correctly."""
        # [Task]: T043, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Toggle me"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Cycle: incomplete -> complete -> incomplete -> complete
        # 1. Mark complete
        response1 = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={"completed": True},
            headers=auth_headers,
        )
        assert response1.status_code == 200
        assert response1.json()["data"]["completed"] is True
        assert response1.json()["data"]["completed_at"] is not None

        # 2. Mark incomplete
        response2 = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={"completed": False},
            headers=auth_headers,
        )
        assert response2.status_code == 200
        assert response2.json()["data"]["completed"] is False
        assert response2.json()["data"]["completed_at"] is None

        # 3. Mark complete again
        response3 = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={"completed": True},
            headers=auth_headers,
        )
        assert response3.status_code == 200
        assert response3.json()["data"]["completed"] is True
        assert response3.json()["data"]["completed_at"] is not None

    def test_mark_complete_persisted_in_database(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test marking complete is persisted to database."""
        # [Task]: T043, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Persistent task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Mark complete
        client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={"completed": True},
            headers=auth_headers,
        )

        # Fetch task and verify persistence
        get_response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 200
        data = get_response.json()["data"]
        assert data["completed"] is True
        assert data["completed_at"] is not None


class TestMarkCompleteTaskIsolation:
    """Test user isolation for mark complete operations."""

    def test_cannot_complete_other_users_task(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
        mismatched_auth_headers: dict,
    ):
        """Test cannot mark another user's task complete."""
        # [Task]: T043, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task with user 1
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "User 1 task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to mark complete as user 2 (should fail)
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={"completed": True},
            headers=mismatched_auth_headers,
        )
        assert response.status_code == 403

        # Verify task is still incomplete
        get_response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 200
        assert get_response.json()["data"]["completed"] is False


class TestMarkCompletePreserveFields:
    """Test that other task fields are preserved during completion toggle."""

    def test_mark_complete_preserves_other_fields(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test marking complete doesn't change other task fields."""
        # [Task]: T043, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task with all fields
        original_title = "Important task"
        original_desc = "This is important"
        original_due = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"

        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={
                "title": original_title,
                "description": original_desc,
                "due_date": original_due,
            },
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]
        original_created_at = create_response.json()["data"]["created_at"]

        # Mark complete
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={"completed": True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()["data"]

        # Verify other fields preserved
        assert data["title"] == original_title
        assert data["description"] == original_desc
        assert data["due_date"] is not None  # Due date preserved
        assert data["created_at"] == original_created_at
        # updated_at should be newer
        assert data["updated_at"] >= original_created_at

    def test_mark_complete_updates_updated_at(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test marking complete updates the updated_at timestamp."""
        # [Task]: T043, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]
        original_updated_at = create_response.json()["data"]["updated_at"]

        # Wait a bit to ensure timestamp changes
        time.sleep(0.01)

        # Mark complete
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={"completed": True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()["data"]

        # Verify updated_at changed
        assert data["updated_at"] != original_updated_at
        assert data["updated_at"] > original_updated_at
