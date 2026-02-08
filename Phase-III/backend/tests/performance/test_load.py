# [Task]: T056, [From]: specs/001-task-crud-api/plan.md#Phase-11
"""
Performance and load tests for Task CRUD API.

Tests:
- Response times are within SLA (<500ms)
- API handles concurrent requests
- Pagination performance with large datasets
"""

import pytest
import time
from uuid import UUID
from concurrent.futures import ThreadPoolExecutor, as_completed


@pytest.mark.performance
class TestResponseTimes:
    """Test API response time performance."""

    def test_create_task_response_time(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test POST task creation is fast (<500ms)."""
        start = time.time()
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Performance test"},
            headers=auth_headers,
        )
        elapsed = time.time() - start

        assert response.status_code == 201
        assert elapsed < 0.5, f"Create task took {elapsed}s, expected <0.5s"

    def test_list_tasks_response_time(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test GET list is fast (<500ms) even with many tasks."""
        # Create 50 tasks
        for i in range(50):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        start = time.time()
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.5, f"List tasks took {elapsed}s, expected <0.5s"

    def test_get_task_response_time(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test GET detail is fast (<500ms)."""
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test"},
            headers=auth_headers,
        )
        task_id = create_response.json()["data"]["id"]

        start = time.time()
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.5, f"Get task took {elapsed}s, expected <0.5s"

    def test_update_task_response_time(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test PUT update is fast (<500ms)."""
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test", "completed": False},
            headers=auth_headers,
        )
        task_id = create_response.json()["data"]["id"]

        start = time.time()
        response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={"title": "Updated", "description": None, "due_date": None, "completed": False},
            headers=auth_headers,
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.5, f"Update task took {elapsed}s, expected <0.5s"

    def test_delete_task_response_time(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test DELETE is fast (<500ms)."""
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test"},
            headers=auth_headers,
        )
        task_id = create_response.json()["data"]["id"]

        start = time.time()
        response = client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        elapsed = time.time() - start

        assert response.status_code == 204
        assert elapsed < 0.5, f"Delete task took {elapsed}s, expected <0.5s"


@pytest.mark.performance
class TestConcurrentRequests:
    """Test API behavior under concurrent load."""

    def test_concurrent_create_requests(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test 10 simultaneous create requests."""
        def create_task(index):
            response = client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Concurrent task {index}"},
                headers=auth_headers,
            )
            return response.status_code == 201

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(create_task, i)
                for i in range(10)
            ]
            results = [f.result() for f in as_completed(futures)]

        # All requests should succeed
        assert all(results), "Some concurrent create requests failed"

    def test_concurrent_read_requests(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test 10 simultaneous read requests."""
        # Create a task first
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Shared task"},
            headers=auth_headers,
        )
        task_id = create_response.json()["data"]["id"]

        def read_task(_):
            response = client.get(
                f"/api/{test_user_id}/tasks/{task_id}",
                headers=auth_headers,
            )
            return response.status_code == 200

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(read_task, i)
                for i in range(10)
            ]
            results = [f.result() for f in as_completed(futures)]

        # All requests should succeed
        assert all(results), "Some concurrent read requests failed"

    def test_concurrent_list_requests(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test 10 simultaneous list requests."""
        # Create some tasks
        for i in range(5):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        def list_tasks(_):
            response = client.get(
                f"/api/{test_user_id}/tasks",
                headers=auth_headers,
            )
            return response.status_code == 200

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(list_tasks, i)
                for i in range(10)
            ]
            results = [f.result() for f in as_completed(futures)]

        # All requests should succeed
        assert all(results), "Some concurrent list requests failed"

    def test_concurrent_mixed_operations(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test 10 concurrent requests with mixed operations."""
        # Create some initial tasks
        task_ids = []
        for i in range(5):
            response = client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Initial task {i}"},
                headers=auth_headers,
            )
            task_ids.append(response.json()["data"]["id"])

        operations_completed = []

        def create_task(index):
            response = client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"New task {index}"},
                headers=auth_headers,
            )
            return response.status_code == 201

        def read_task():
            if task_ids:
                response = client.get(
                    f"/api/{test_user_id}/tasks/{task_ids[0]}",
                    headers=auth_headers,
                )
                return response.status_code == 200
            return True

        def list_tasks():
            response = client.get(
                f"/api/{test_user_id}/tasks",
                headers=auth_headers,
            )
            return response.status_code == 200

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []

            # Mix of operations
            for i in range(4):
                futures.append(executor.submit(create_task, i))
            for i in range(3):
                futures.append(executor.submit(read_task))
            for i in range(3):
                futures.append(executor.submit(list_tasks))

            results = [f.result() for f in as_completed(futures)]

        # Most operations should succeed (allow 1 failure)
        assert sum(results) >= len(results) - 1


@pytest.mark.performance
class TestPaginationPerformance:
    """Test pagination performance with large datasets."""

    def test_pagination_with_100_tasks(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test pagination with 100 tasks."""
        # Create 100 tasks
        for i in range(100):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        # Get first page
        start = time.time()
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=10&offset=0",
            headers=auth_headers,
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.5, f"Pagination with 100 tasks took {elapsed}s"
        assert len(response.json()["data"]["items"]) == 10

    def test_pagination_with_500_tasks(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test pagination with 500 tasks is still performant."""
        # Create 500 tasks
        for i in range(500):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        # Get page from middle
        start = time.time()
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=10&offset=250",
            headers=auth_headers,
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.5, f"Pagination with 500 tasks took {elapsed}s"

    def test_pagination_last_page_performance(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test pagination on last page is performant."""
        # Create 100 tasks
        for i in range(100):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        # Get last page
        start = time.time()
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=10&offset=90",
            headers=auth_headers,
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.5, f"Last page pagination took {elapsed}s"

    def test_large_limit_parameter(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test pagination with maximum limit is still performant."""
        # Create 100 tasks
        for i in range(100):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        # Get all with limit=100
        start = time.time()
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=100&offset=0",
            headers=auth_headers,
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.5, f"Large limit pagination took {elapsed}s"


@pytest.mark.performance
class TestMemoryEfficiency:
    """Test API memory efficiency under load."""

    def test_list_large_dataset_memory(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test listing large dataset doesn't consume excessive memory."""
        # Create 200 tasks
        for i in range(200):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}", "description": f"Description {i}"},
                headers=auth_headers,
            )

        # List with pagination (should be efficient)
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=20&offset=0",
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Response should only contain 20 items, not all 200
        items = response.json()["data"]["items"]
        assert len(items) == 20

    def test_single_item_response_size(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test single item responses are appropriately sized."""
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test", "description": "A" * 1000},
            headers=auth_headers,
        )
        task_id = create_response.json()["data"]["id"]

        # Get task
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )

        # Response should be reasonable size
        response_size = len(response.content)
        assert response_size < 10000, f"Single task response is {response_size} bytes"
