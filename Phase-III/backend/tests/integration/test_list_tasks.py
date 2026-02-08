# [Task]: T025, [From]: specs/001-task-crud-api/spec.md#User-Story-2-List
# [From]: specs/001-task-crud-api/plan.md#Phase-4-User-Story-2
"""
Integration tests for GET /api/{user_id}/tasks endpoint (List Tasks).

Verifies:
- Tasks are listed in correct order (created_at DESC)
- User_id isolation (each user only sees their own tasks)
- Pagination with offset and limit works correctly
- Empty task list returns empty array (not error)
- Large dataset pagination (100+ tasks)
- has_more flag is calculated correctly
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from src.config import settings
from src.models.task import Task
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestListTasksBasicFunctionality:
    """Test basic list functionality."""

    async def test_list_tasks_empty_returns_empty_array(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that user with no tasks gets empty array (not error)."""
        # [Task]: T025, [From]: specs/001-task-crud-api/spec.md#User-Story-2-List
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["items"] == []
        assert data["data"]["pagination"]["total"] == 0
        assert data["data"]["pagination"]["has_more"] is False

    async def test_list_tasks_single_task(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test listing single task."""
        # [Task]: T025, [From]: specs/001-task-crud-api/spec.md#User-Story-2-List
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Single task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        created_task = create_response.json()["data"]

        # List tasks
        list_response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert list_response.status_code == 200
        data = list_response.json()
        assert len(data["data"]["items"]) == 1
        assert data["data"]["items"][0]["id"] == created_task["id"]
        assert data["data"]["items"][0]["title"] == "Single task"

    async def test_list_tasks_multiple_tasks(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test listing multiple tasks."""
        # [Task]: T025, [From]: specs/001-task-crud-api/spec.md#User-Story-2-List
        # Create multiple tasks
        task_titles = ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5"]
        created_ids = []

        for title in task_titles:
            response = client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": title},
                headers=auth_headers,
            )
            assert response.status_code == 201
            created_ids.append(response.json()["data"]["id"])

        # List tasks
        list_response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert list_response.status_code == 200
        data = list_response.json()
        assert len(data["data"]["items"]) == 5
        assert data["data"]["pagination"]["total"] == 5

        # Verify all tasks are present
        listed_ids = [task["id"] for task in data["data"]["items"]]
        for task_id in created_ids:
            assert task_id in listed_ids


@pytest.mark.asyncio
class TestListTasksOrdering:
    """Test that tasks are returned in correct order."""

    async def test_list_tasks_ordered_by_created_at_desc(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test tasks are ordered by created_at DESC (newest first)."""
        # [Task]: T025, [From]: specs/001-task-crud-api/spec.md#User-Story-2-List
        # Create tasks with slight delays to ensure ordering
        task_titles = ["First", "Second", "Third"]

        for title in task_titles:
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": title},
                headers=auth_headers,
            )

        # List and verify order (newest first)
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        items = response.json()["data"]["items"]

        # Should be in reverse order of creation (DESC)
        assert items[0]["title"] == "Third"
        assert items[1]["title"] == "Second"
        assert items[2]["title"] == "First"

        # Verify timestamps are ordered
        for i in range(len(items) - 1):
            current_time = datetime.fromisoformat(
                items[i]["created_at"].replace("Z", "+00:00")
            )
            next_time = datetime.fromisoformat(
                items[i + 1]["created_at"].replace("Z", "+00:00")
            )
            assert current_time >= next_time


@pytest.mark.asyncio
class TestListTasksPagination:
    """Test pagination functionality."""

    async def test_list_tasks_pagination_limit_respected(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that limit parameter restricts number of items."""
        # [Task]: T025, [From]: specs/001-task-crud-api/spec.md#Pagination
        # Create 5 tasks
        for i in range(5):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        # Request with limit=2
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=2",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 2
        assert data["data"]["pagination"]["limit"] == 2
        assert data["data"]["pagination"]["total"] == 5

    async def test_list_tasks_pagination_offset_works(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that offset skips correct number of items."""
        # [Task]: T025, [From]: specs/001-task-crud-api/spec.md#Pagination
        # Create 5 tasks
        created_ids = []
        for i in range(5):
            response = client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )
            created_ids.append(response.json()["data"]["id"])

        # Request with offset=2
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=10&offset=2",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 3  # Items 3, 4, 5
        assert data["data"]["pagination"]["offset"] == 2

        # Verify we're getting the right items (offset 2 means skip 2)
        returned_ids = [task["id"] for task in data["data"]["items"]]
        # Tasks are ordered by created_at DESC, so newest first
        # created_ids in creation order: [Task 0, Task 1, Task 2, Task 3, Task 4]
        # list response order (DESC): [Task 4, Task 3, Task 2, Task 1, Task 0]
        # offset=2 skips 2, so we get: [Task 2, Task 1, Task 0]
        expected_ids = list(reversed(created_ids))  # DESC order: [4, 3, 2, 1, 0]
        assert returned_ids == expected_ids[2:]  # Skip 2, get [2, 1, 0]

    async def test_list_tasks_pagination_has_more_true_when_more_items(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test has_more is true when more items exist beyond current page."""
        # [Task]: T025, [From]: specs/001-task-crud-api/spec.md#Pagination
        # Create 5 tasks
        for i in range(5):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        # Request with limit=2 (shows items 0-1, has_more should be true)
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=2&offset=0",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["has_more"] is True

    async def test_list_tasks_pagination_has_more_false_at_end(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test has_more is false when no more items exist."""
        # [Task]: T025, [From]: specs/001-task-crud-api/spec.md#Pagination
        # Create 5 tasks
        for i in range(5):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        # Request that covers all items
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=10&offset=0",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["has_more"] is False

    async def test_list_tasks_pagination_with_offset_beyond_total(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test requesting with offset beyond total items."""
        # [Task]: T025, [From]: specs/001-task-crud-api/spec.md#Pagination
        # Create 3 tasks
        for i in range(3):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        # Request with offset=10 (beyond total of 3)
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=10&offset=10",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 0
        assert data["data"]["pagination"]["has_more"] is False
        assert data["data"]["pagination"]["total"] == 3


@pytest.mark.asyncio
class TestListTasksUserIsolation:
    """Test that user_id isolation is enforced."""

    async def test_list_tasks_user_isolation_different_users(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that different users see only their own tasks."""
        # [Task]: T025, [From]: specs/001-task-crud-api/spec.md#Authorization-Rules
        # Create task for first user
        response1 = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "User 1 task"},
            headers=auth_headers,
        )
        assert response1.status_code == 201

        # Create task for second user
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

        response2 = client.post(
            f"/api/{other_user_id}/tasks",
            json={"title": "User 2 task"},
            headers=other_auth_headers,
        )
        assert response2.status_code == 201

        # List tasks for first user
        list_response1 = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert list_response1.status_code == 200
        tasks1 = list_response1.json()["data"]["items"]

        # List tasks for second user
        list_response2 = client.get(
            f"/api/{other_user_id}/tasks",
            headers=other_auth_headers,
        )
        assert list_response2.status_code == 200
        tasks2 = list_response2.json()["data"]["items"]

        # Verify isolation
        assert len(tasks1) == 1
        assert len(tasks2) == 1
        assert tasks1[0]["title"] == "User 1 task"
        assert tasks2[0]["title"] == "User 2 task"
        assert str(tasks1[0]["user_id"]) == str(test_user_id)
        assert str(tasks2[0]["user_id"]) == str(other_user_id)

    async def test_list_tasks_user_isolation_filters_by_user_id(
        self,
        client: TestClient,
        test_session: AsyncSession,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that database filtering by user_id works correctly."""
        # [Task]: T025, [From]: specs/001-task-crud-api/spec.md#Authorization-Rules
        # Create 3 tasks for test user
        for i in range(3):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        # List tasks
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        listed_tasks = response.json()["data"]["items"]

        # Verify all returned tasks belong to user
        for task in listed_tasks:
            assert str(task["user_id"]) == str(test_user_id)

        # Verify database filtering
        stmt = select(Task).where(Task.user_id == test_user_id)
        result = await test_session.execute(stmt)
        db_tasks = result.scalars().all()

        assert len(db_tasks) == 3
        assert len(listed_tasks) == 3


@pytest.mark.asyncio
class TestListTasksLargeDataset:
    """Test pagination with large datasets."""

    async def test_list_tasks_large_dataset_pagination(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test pagination with 150+ tasks."""
        # [Task]: T025, [From]: specs/001-task-crud-api/spec.md#Performance
        # Create 150 tasks
        num_tasks = 150
        for i in range(num_tasks):
            response = client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )
            assert response.status_code == 201

        # Page 1: offset=0, limit=50
        page1 = client.get(
            f"/api/{test_user_id}/tasks?limit=50&offset=0",
            headers=auth_headers,
        )
        assert page1.status_code == 200
        data1 = page1.json()
        assert len(data1["data"]["items"]) == 50
        assert data1["data"]["pagination"]["total"] == 150
        assert data1["data"]["pagination"]["has_more"] is True

        # Page 2: offset=50, limit=50
        page2 = client.get(
            f"/api/{test_user_id}/tasks?limit=50&offset=50",
            headers=auth_headers,
        )
        assert page2.status_code == 200
        data2 = page2.json()
        assert len(data2["data"]["items"]) == 50
        assert data2["data"]["pagination"]["has_more"] is True

        # Page 3: offset=100, limit=50
        page3 = client.get(
            f"/api/{test_user_id}/tasks?limit=50&offset=100",
            headers=auth_headers,
        )
        assert page3.status_code == 200
        data3 = page3.json()
        assert len(data3["data"]["items"]) == 50
        assert data3["data"]["pagination"]["has_more"] is False

        # Verify no duplicate tasks
        all_ids = (
            [t["id"] for t in data1["data"]["items"]]
            + [t["id"] for t in data2["data"]["items"]]
            + [t["id"] for t in data3["data"]["items"]]
        )
        assert len(all_ids) == len(set(all_ids))

    async def test_list_tasks_default_limit_works(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that default limit (10) works for many tasks."""
        # [Task]: T025, [From]: specs/001-task-crud-api/spec.md#Pagination
        # Create 25 tasks
        for i in range(25):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        # Request without limit (should default to 10)
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 10
        assert data["data"]["pagination"]["limit"] == 10
        assert data["data"]["pagination"]["total"] == 25
        assert data["data"]["pagination"]["has_more"] is True
