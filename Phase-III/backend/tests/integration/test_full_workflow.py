# [Task]: T053, [From]: specs/001-task-crud-api/plan.md#Phase-10
"""
End-to-end workflow tests for Task CRUD API.

Tests complete user journeys covering:
- Multiple tasks across complete lifecycle
- Pagination with various dataset sizes
- Concurrent operations
- Data isolation between users
"""

import pytest
from datetime import datetime, timedelta
from uuid import UUID

from src.api.schemas import TaskResponse, PaginatedResponse


@pytest.mark.integration
class TestCompleteTaskLifecycle:
    """Test complete task lifecycle from creation to deletion."""

    def test_create_list_get_update_complete_delete_workflow(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """
        [Task]: T053, [From]: specs/001-task-crud-api/spec.md#FR-001-FR-007

        Test complete task lifecycle:
        1. Create a new task
        2. List tasks and verify it appears
        3. Get task detail
        4. Update task fields
        5. Mark task complete
        6. Delete task
        7. Verify deletion
        """
        # Step 1: Create task
        create_payload = {
            "title": "Complete Phase 2 implementation",
            "description": "Finish all CRUD endpoints and tests",
            "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        }
        response_create = client.post(
            f"/api/{test_user_id}/tasks",
            json=create_payload,
            headers=auth_headers,
        )
        assert response_create.status_code == 201
        task_id = response_create.json()["data"]["id"]
        assert response_create.json()["data"]["title"] == create_payload["title"]
        assert response_create.json()["data"]["completed"] is False

        # Step 2: List tasks and verify
        response_list = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert response_list.status_code == 200
        tasks = response_list.json()["data"]["items"]
        assert len(tasks) >= 1
        assert any(t["id"] == task_id for t in tasks)

        # Step 3: Get task detail
        response_get = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response_get.status_code == 200
        task = response_get.json()["data"]
        assert task["id"] == task_id
        assert task["title"] == create_payload["title"]

        # Step 4: Update task (title)
        update_payload = {
            "title": "Updated: Complete Phase 2 implementation",
            "description": "Updated description with more details",
            "due_date": (datetime.utcnow() + timedelta(days=10)).isoformat(),
            "completed": False,
        }
        response_update = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json=update_payload,
            headers=auth_headers,
        )
        assert response_update.status_code == 200
        updated_task = response_update.json()["data"]
        assert updated_task["title"] == update_payload["title"]
        assert updated_task["description"] == update_payload["description"]

        # Step 5: Mark task complete
        complete_payload = {"completed": True}
        response_complete = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json=complete_payload,
            headers=auth_headers,
        )
        assert response_complete.status_code == 200
        completed_task = response_complete.json()["data"]
        assert completed_task["completed"] is True
        assert completed_task["completed_at"] is not None

        # Step 6: Delete task
        response_delete = client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response_delete.status_code == 204

        # Step 7: Verify deletion (should return 404)
        response_get_deleted = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response_get_deleted.status_code == 404


@pytest.mark.integration
class TestPaginationScenarios:
    """Test pagination with various dataset sizes."""

    def test_pagination_with_zero_tasks(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test pagination returns empty list with no tasks."""
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["items"] == []
        assert data["data"]["pagination"]["total"] == 0
        assert data["data"]["pagination"]["has_more"] is False

    def test_pagination_with_single_task(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test pagination with one task."""
        # Create a task
        client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Single task"},
            headers=auth_headers,
        )

        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 1
        assert data["data"]["pagination"]["total"] == 1
        assert data["data"]["pagination"]["has_more"] is False

    def test_pagination_with_multiple_pages(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test pagination correctly handles multiple pages."""
        # Create 25 tasks
        for i in range(25):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i+1}"},
                headers=auth_headers,
            )

        # Test first page (limit=10)
        response_page1 = client.get(
            f"/api/{test_user_id}/tasks?limit=10&offset=0",
            headers=auth_headers,
        )
        assert response_page1.status_code == 200
        page1 = response_page1.json()["data"]
        assert len(page1["items"]) == 10
        assert page1["pagination"]["total"] == 25
        assert page1["pagination"]["has_more"] is True

        # Test second page
        response_page2 = client.get(
            f"/api/{test_user_id}/tasks?limit=10&offset=10",
            headers=auth_headers,
        )
        assert response_page2.status_code == 200
        page2 = response_page2.json()["data"]
        assert len(page2["items"]) == 10
        assert page2["pagination"]["has_more"] is True

        # Test third page (incomplete)
        response_page3 = client.get(
            f"/api/{test_user_id}/tasks?limit=10&offset=20",
            headers=auth_headers,
        )
        assert response_page3.status_code == 200
        page3 = response_page3.json()["data"]
        assert len(page3["items"]) == 5
        assert page3["pagination"]["has_more"] is False

    def test_pagination_offset_boundaries(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test pagination with edge case offsets."""
        # Create 5 tasks
        for i in range(5):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i+1}"},
                headers=auth_headers,
            )

        # Offset beyond all items
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=10&offset=100",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["items"] == []
        assert data["data"]["pagination"]["total"] == 5


@pytest.mark.integration
class TestMultiUserIsolation:
    """Test data isolation between different users."""

    def test_multiple_users_cannot_see_each_others_tasks(
        self, client, test_user_id: UUID, auth_headers: dict, other_user_id, other_user_auth_headers
    ):
        """Test that users only see their own tasks."""
        # User 1 creates 3 tasks
        task_ids_user1 = []
        for i in range(3):
            response = client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"User1 Task {i+1}"},
                headers=auth_headers,
            )
            task_ids_user1.append(response.json()["data"]["id"])

        # User 2 creates 2 tasks
        task_ids_user2 = []
        for i in range(2):
            response = client.post(
                f"/api/{other_user_id}/tasks",
                json={"title": f"User2 Task {i+1}"},
                headers=other_user_auth_headers,
            )
            task_ids_user2.append(response.json()["data"]["id"])

        # User 1 lists their tasks - should see only 3
        response_user1 = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        user1_tasks = response_user1.json()["data"]["items"]
        assert len(user1_tasks) == 3
        assert all(t["id"] in task_ids_user1 for t in user1_tasks)

        # User 2 lists their tasks - should see only 2
        response_user2 = client.get(
            f"/api/{other_user_id}/tasks",
            headers=other_user_auth_headers,
        )
        user2_tasks = response_user2.json()["data"]["items"]
        assert len(user2_tasks) == 2
        assert all(t["id"] in task_ids_user2 for t in user2_tasks)

    def test_user_cannot_access_other_user_task(
        self, client, test_user_id: UUID, auth_headers: dict, other_user_id, other_user_auth_headers
    ):
        """Test that users cannot GET other users' tasks."""
        # User 1 creates a task
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Private task"},
            headers=auth_headers,
        )
        task_id = response.json()["data"]["id"]

        # User 2 attempts to access User 1's task - should get 403 or 404
        response = client.get(
            f"/api/{other_user_id}/tasks/{task_id}",
            headers=other_user_auth_headers,
        )
        assert response.status_code in (403, 404)

    def test_user_cannot_update_other_user_task(
        self, client, test_user_id: UUID, auth_headers: dict, other_user_id, other_user_auth_headers
    ):
        """Test that users cannot update other users' tasks."""
        # User 1 creates a task
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Original title"},
            headers=auth_headers,
        )
        task_id = response.json()["data"]["id"]

        # User 2 attempts to update User 1's task
        response = client.patch(
            f"/api/{other_user_id}/tasks/{task_id}",
            json={"title": "Hacked title"},
            headers=other_user_auth_headers,
        )
        assert response.status_code in (403, 404)

        # Verify task wasn't changed
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response.json()["data"]["title"] == "Original title"

    def test_user_cannot_delete_other_user_task(
        self, client, test_user_id: UUID, auth_headers: dict, other_user_id, other_user_auth_headers
    ):
        """Test that users cannot delete other users' tasks."""
        # User 1 creates a task
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Task to protect"},
            headers=auth_headers,
        )
        task_id = response.json()["data"]["id"]

        # User 2 attempts to delete User 1's task
        response = client.delete(
            f"/api/{other_user_id}/tasks/{task_id}",
            headers=other_user_auth_headers,
        )
        assert response.status_code in (403, 404)

        # Verify task still exists
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["data"]["id"] == task_id


@pytest.mark.integration
class TestConcurrentOperations:
    """Test API behavior with concurrent operations."""

    def test_concurrent_create_operations(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test creating multiple tasks rapidly."""
        # Create 10 tasks rapidly
        task_ids = []
        for i in range(10):
            response = client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Concurrent Task {i+1}"},
                headers=auth_headers,
            )
            assert response.status_code == 201
            task_ids.append(response.json()["data"]["id"])

        # Verify all tasks are in database
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        tasks = response.json()["data"]["items"]
        assert len(tasks) >= 10

    def test_concurrent_read_operations(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test reading tasks concurrently."""
        # Create a task
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )
        task_id = response.json()["data"]["id"]

        # Get task multiple times concurrently
        for _ in range(5):
            response = client.get(
                f"/api/{test_user_id}/tasks/{task_id}",
                headers=auth_headers,
            )
            assert response.status_code == 200
            assert response.json()["data"]["id"] == task_id

    def test_concurrent_mixed_operations(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test mix of CRUD operations."""
        # Create tasks
        task_ids = []
        for i in range(5):
            response = client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i+1}"},
                headers=auth_headers,
            )
            task_ids.append(response.json()["data"]["id"])

        # Perform mixed operations
        # Update first task
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_ids[0]}",
            json={"title": "Updated Task 1"},
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Get second task
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_ids[1]}",
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Complete third task
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_ids[2]}/complete",
            json={"completed": True},
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Delete fourth task
        response = client.delete(
            f"/api/{test_user_id}/tasks/{task_ids[3]}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # Verify final state
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        tasks = response.json()["data"]["items"]
        assert len(tasks) >= 4  # At least 4 tasks exist


@pytest.mark.integration
class TestResponseFormats:
    """Test response format consistency across endpoints."""

    def test_create_response_format(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test POST response has correct structure."""
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()

        # Verify envelope format
        assert "data" in data
        assert "error" in data
        assert data["error"] is None

        # Verify task structure
        task = data["data"]
        assert "id" in task
        assert "user_id" in task
        assert "title" in task
        assert "created_at" in task
        assert "updated_at" in task

    def test_list_response_format(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test GET list response has correct structure."""
        # Create a task first
        client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )

        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        # Verify pagination structure
        assert "items" in data["data"]
        assert "pagination" in data["data"]
        assert "limit" in data["data"]["pagination"]
        assert "offset" in data["data"]["pagination"]
        assert "total" in data["data"]["pagination"]
        assert "has_more" in data["data"]["pagination"]

    def test_error_response_format(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test error response has correct structure."""
        response = client.get(
            f"/api/{test_user_id}/tasks/invalid-uuid",
            headers=auth_headers,
        )
        assert response.status_code in (400, 422)
        data = response.json()

        # Verify error envelope
        assert "data" in data
        assert data["data"] is None
        assert "error" in data
        error = data["error"]
        assert "code" in error
        assert "message" in error
