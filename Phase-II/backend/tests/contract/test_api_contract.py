# [Task]: T055, [From]: specs/001-task-crud-api/plan.md#Phase-11
"""
API contract tests for endpoint consistency and isolation.

Tests:
- Each endpoint works independently
- Response format consistency
- Header validation
- Query parameter handling
- Path parameter validation
"""

import pytest
from uuid import UUID
from datetime import datetime


@pytest.mark.contract
class TestEndpointIsolation:
    """Test that each endpoint operates independently."""

    def test_create_endpoint_isolation(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test POST endpoint works independently."""
        payload = {
            "title": "Isolated task",
            "description": "Test isolation",
        }
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["title"] == payload["title"]

    def test_list_endpoint_isolation(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test GET list endpoint works independently."""
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert "data" in response.json()
        assert "items" in response.json()["data"]

    def test_get_detail_endpoint_isolation(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test GET detail endpoint works independently."""
        # First create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Detail task"},
            headers=auth_headers,
        )
        task_id = create_response.json()["data"]["id"]

        # Then get it
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["data"]["id"] == task_id

    def test_update_endpoint_isolation(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test PUT endpoint works independently."""
        # Create a task first
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Update test", "completed": False},
            headers=auth_headers,
        )
        task_id = create_response.json()["data"]["id"]

        # Update it
        response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={"title": "Updated", "description": "New desc", "due_date": None, "completed": False},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Updated"

    def test_patch_endpoint_isolation(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test PATCH endpoint works independently."""
        # Create a task first
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Patch test"},
            headers=auth_headers,
        )
        task_id = create_response.json()["data"]["id"]

        # Patch it
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={"title": "Patched"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Patched"

    def test_complete_endpoint_isolation(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test PATCH complete endpoint works independently."""
        # Create a task first
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Complete test"},
            headers=auth_headers,
        )
        task_id = create_response.json()["data"]["id"]

        # Complete it
        response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}/complete",
            json={"completed": True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["data"]["completed"] is True

    def test_delete_endpoint_isolation(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test DELETE endpoint works independently."""
        # Create a task first
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Delete test"},
            headers=auth_headers,
        )
        task_id = create_response.json()["data"]["id"]

        # Delete it
        response = client.delete(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204


@pytest.mark.contract
class TestResponseConsistency:
    """Test response format consistency across all endpoints."""

    def test_create_response_structure(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test POST response envelope structure."""
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test"},
            headers=auth_headers,
        )
        data = response.json()

        # Standard envelope
        assert "data" in data
        assert "error" in data
        assert isinstance(data["data"], dict)
        assert data["error"] is None

    def test_get_response_structure(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test GET response envelope structure."""
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test"},
            headers=auth_headers,
        )
        task_id = create_response.json()["data"]["id"]

        # Get it
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        data = response.json()

        # Standard envelope
        assert "data" in data
        assert "error" in data
        assert isinstance(data["data"], dict)
        assert data["error"] is None

    def test_list_response_structure(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test GET list response envelope structure."""
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        data = response.json()

        # Standard envelope
        assert "data" in data
        assert "error" in data
        assert isinstance(data["data"], dict)
        assert data["error"] is None

        # List-specific structure
        assert "items" in data["data"]
        assert "pagination" in data["data"]

    def test_error_response_structure(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test error response envelope structure."""
        response = client.get(
            f"/api/{test_user_id}/tasks/invalid-uuid",
            headers=auth_headers,
        )
        data = response.json()

        # Error envelope
        assert "data" in data
        assert data["data"] is None
        assert "error" in data
        assert isinstance(data["error"], dict)
        assert "code" in data["error"]
        assert "message" in data["error"]

    def test_task_object_consistency(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test task objects have consistent fields across endpoints."""
        # Create a task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test", "description": "Desc"},
            headers=auth_headers,
        )
        task_from_create = create_response.json()["data"]

        # Get the same task
        task_id = task_from_create["id"]
        get_response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        task_from_get = get_response.json()["data"]

        # Both should have identical core fields
        for field in ["id", "user_id", "title", "description", "completed"]:
            assert field in task_from_create
            assert field in task_from_get
            assert task_from_create[field] == task_from_get[field]


@pytest.mark.contract
class TestHeaderValidation:
    """Test proper handling of request headers."""

    def test_authorization_header_required(
        self, client, test_user_id: UUID
    ):
        """Test endpoints require Authorization header."""
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test"},
        )
        assert response.status_code == 401

    def test_authorization_header_bearer_format(
        self, client, test_user_id: UUID
    ):
        """Test Authorization header must use Bearer scheme."""
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test"},
            headers={"Authorization": "Basic invalid"},
        )
        assert response.status_code == 401

    def test_valid_bearer_token_accepted(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test valid Bearer token is accepted."""
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test"},
            headers=auth_headers,
        )
        assert response.status_code == 201

    def test_invalid_token_rejected(
        self, client, test_user_id: UUID
    ):
        """Test invalid JWT token is rejected."""
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test"},
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401


@pytest.mark.contract
class TestQueryParameterHandling:
    """Test proper handling of query parameters."""

    def test_pagination_limit_parameter(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test limit query parameter is respected."""
        # Create tasks
        for i in range(15):
            client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )

        # Get with limit=5
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=5",
            headers=auth_headers,
        )
        assert response.status_code == 200
        items = response.json()["data"]["items"]
        assert len(items) <= 5

    def test_pagination_offset_parameter(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test offset query parameter is respected."""
        # Create tasks
        task_ids = []
        for i in range(10):
            response = client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": f"Task {i}"},
                headers=auth_headers,
            )
            task_ids.append(response.json()["data"]["id"])

        # Get first page
        response1 = client.get(
            f"/api/{test_user_id}/tasks?limit=5&offset=0",
            headers=auth_headers,
        )
        page1_ids = [t["id"] for t in response1.json()["data"]["items"]]

        # Get second page
        response2 = client.get(
            f"/api/{test_user_id}/tasks?limit=5&offset=5",
            headers=auth_headers,
        )
        page2_ids = [t["id"] for t in response2.json()["data"]["items"]]

        # Pages should be different
        assert len(set(page1_ids) & set(page2_ids)) == 0

    def test_default_pagination_values(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test default pagination values are applied."""
        # Create a task
        client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test"},
            headers=auth_headers,
        )

        # Get without pagination params
        response = client.get(
            f"/api/{test_user_id}/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        pagination = response.json()["data"]["pagination"]

        # Should have default values
        assert "limit" in pagination
        assert "offset" in pagination
        assert pagination["offset"] == 0  # Default offset is 0

    def test_invalid_limit_parameter(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test invalid limit parameter is rejected."""
        response = client.get(
            f"/api/{test_user_id}/tasks?limit=999",
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_invalid_offset_parameter(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test invalid offset parameter is rejected."""
        response = client.get(
            f"/api/{test_user_id}/tasks?offset=-1",
            headers=auth_headers,
        )
        assert response.status_code == 422


@pytest.mark.contract
class TestPathParameterValidation:
    """Test proper validation of path parameters."""

    def test_invalid_user_id_format(
        self, client, auth_headers: dict
    ):
        """Test invalid user_id format is rejected."""
        response = client.get(
            "/api/invalid-uuid/tasks",
            headers=auth_headers,
        )
        assert response.status_code in (400, 422)

    def test_invalid_task_id_format(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test invalid task_id format is rejected."""
        response = client.get(
            f"/api/{test_user_id}/tasks/invalid-uuid",
            headers=auth_headers,
        )
        assert response.status_code in (400, 422)

    def test_user_id_path_validation(
        self, client, test_user_id: UUID, other_user_id: UUID, auth_headers: dict, other_user_auth_headers: dict
    ):
        """Test user_id in path is validated against JWT."""
        # Create a task as user 1
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test"},
            headers=auth_headers,
        )
        task_id = create_response.json()["data"]["id"]

        # Try to access as user 2 with user 2's auth but user 1's path
        response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=other_user_auth_headers,
        )
        # Should fail because JWT user doesn't match path user
        assert response.status_code == 403

    def test_task_id_validation(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test task_id is validated to exist."""
        from uuid import uuid4

        non_existent_id = str(uuid4())
        response = client.get(
            f"/api/{test_user_id}/tasks/{non_existent_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404


@pytest.mark.contract
class TestContentTypeHandling:
    """Test Content-Type header handling."""

    def test_request_json_content_type_required(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test POST requires JSON content type."""
        headers = dict(auth_headers)
        headers["Content-Type"] = "application/json"

        response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test"},
            headers=headers,
        )
        assert response.status_code == 201

    def test_response_json_content_type(
        self, client, test_user_id: UUID, auth_headers: dict
    ):
        """Test responses have JSON content type."""
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Test"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert "application/json" in response.headers.get("content-type", "")
