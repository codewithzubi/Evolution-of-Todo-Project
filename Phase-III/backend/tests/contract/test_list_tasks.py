# [Task]: T024, [From]: specs/001-task-crud-api/spec.md#User-Story-2-List
# [From]: specs/001-task-crud-api/plan.md#Phase-4-User-Story-2
"""
Contract tests for GET /api/{user_id}/tasks endpoint (List Tasks).

Verifies:
- Response schema validation (pagination structure)
- Query parameter handling (limit, offset)
- HTTP status codes (200, 401, 403, 422)
- Error response formats
- Pagination metadata (has_more, total, limit, offset)
"""

from fastapi.testclient import TestClient


class TestListTasksRequestSchema:
    """Test GET request schema and query parameter validation."""

    def test_list_tasks_with_default_pagination(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test listing tasks with default limit and offset."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data["data"]
        assert "pagination" in data["data"]

    def test_list_tasks_with_custom_limit(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test listing tasks with custom limit query parameter."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Query-Parameters
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=5",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["limit"] == 5

    def test_list_tasks_with_custom_offset(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test listing tasks with custom offset query parameter."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Query-Parameters
        response = client.get(
            f"/api/{test_user_id}/tasks?offset=10",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["offset"] == 10

    def test_list_tasks_with_limit_and_offset(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test listing tasks with both limit and offset."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Query-Parameters
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=15&offset=30",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["limit"] == 15
        assert data["data"]["pagination"]["offset"] == 30

    def test_list_tasks_invalid_limit_too_small_returns_422(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that limit < 1 returns 422 Unprocessable Entity."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Pagination-Constraints
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=0",
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_list_tasks_invalid_limit_too_large_returns_422(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that limit > 100 returns 422 Unprocessable Entity."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Pagination-Constraints
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=101",
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_list_tasks_invalid_offset_negative_returns_422(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that negative offset returns 422 Unprocessable Entity."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Pagination-Constraints
        response = client.get(
            f"/api/{test_user_id}/tasks?offset=-1",
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_list_tasks_invalid_limit_non_integer_returns_422(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that non-integer limit returns 422 Unprocessable Entity."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Query-Parameters
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=abc",
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_list_tasks_offset_zero_valid(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that offset=0 is valid."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Pagination-Constraints
        response = client.get(
            f"/api/{test_user_id}/tasks?offset=0",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_list_tasks_limit_boundary_1_valid(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that limit=1 (minimum) is valid."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Pagination-Constraints
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=1",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["limit"] == 1

    def test_list_tasks_limit_boundary_100_valid(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that limit=100 (maximum) is valid."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Pagination-Constraints
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=100",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["limit"] == 100


class TestListTasksResponseSchema:
    """Test response schema and HTTP status codes."""

    def test_list_tasks_returns_200_status(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that list endpoint returns 200 OK."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#List-Tasks-Response
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_list_tasks_response_has_required_structure(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test response contains items and pagination fields."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#List-Tasks-Response
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "items" in data["data"]
        assert "pagination" in data["data"]
        assert isinstance(data["data"]["items"], list)

    def test_list_tasks_response_pagination_has_required_fields(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test pagination object has all required fields."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Pagination-Metadata
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        pagination = response.json()["data"]["pagination"]

        # Verify pagination fields
        assert "limit" in pagination
        assert "offset" in pagination
        assert "total" in pagination
        assert "has_more" in pagination

    def test_list_tasks_response_item_has_task_fields(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that task items have all required fields."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Task-Response-Fields
        # First create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201

        # Then list tasks
        list_response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert list_response.status_code == 200
        items = list_response.json()["data"]["items"]

        assert len(items) > 0
        task = items[0]
        assert "id" in task
        assert "user_id" in task
        assert "title" in task
        assert "description" in task
        assert "due_date" in task
        assert "completed" in task
        assert "completed_at" in task
        assert "created_at" in task
        assert "updated_at" in task

    def test_list_tasks_pagination_metadata_correct(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test pagination metadata values are correct."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Pagination-Metadata
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=10&offset=0",
            headers=auth_headers,
        )
        assert response.status_code == 200
        pagination = response.json()["data"]["pagination"]

        # Verify values match request
        assert pagination["limit"] == 10
        assert pagination["offset"] == 0
        assert isinstance(pagination["total"], int)
        assert isinstance(pagination["has_more"], bool)

    def test_list_tasks_has_more_false_when_no_more_items(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that has_more is false when all items fit in page."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Pagination-Metadata
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=100&offset=0",
            headers=auth_headers,
        )
        assert response.status_code == 200
        pagination = response.json()["data"]["pagination"]

        # When offset + limit >= total, has_more should be false
        expected_has_more = (pagination["offset"] + pagination["limit"]) < pagination[
            "total"
        ]
        assert pagination["has_more"] == expected_has_more


class TestListTasksAuthentication:
    """Test authentication and authorization for list endpoint."""

    def test_list_tasks_missing_jwt_returns_401(
        self,
        client: TestClient,
        test_user_id,
    ):
        """Test that missing JWT returns 401 Unauthorized."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        response = client.get(
            f"/api/{test_user_id}/tasks",
            # No Authorization header
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"

    def test_list_tasks_invalid_jwt_returns_401(
        self,
        client: TestClient,
        test_user_id,
        invalid_auth_headers: dict,
    ):
        """Test that invalid JWT returns 401 Unauthorized."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#JWT-Token-Requirements
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=invalid_auth_headers,
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"

    def test_list_tasks_mismatched_user_id_returns_403(
        self,
        client: TestClient,
        test_user_id,
        mismatched_auth_headers: dict,
    ):
        """Test that mismatched user_id in JWT returns 403 Forbidden."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#Authorization-Rules
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=mismatched_auth_headers,
        )
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "FORBIDDEN"

    def test_list_tasks_invalid_auth_scheme_returns_401(
        self,
        client: TestClient,
        test_user_id,
    ):
        """Test that invalid auth scheme (not Bearer) returns 401."""
        # [Task]: T024, [From]: specs/001-task-crud-api/spec.md#JWT-Token-Requirements
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers={"Authorization": "Basic invalid"},
        )
        assert response.status_code == 401
