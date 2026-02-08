# [Task]: T375, [From]: specs/004-ai-chatbot/spec.md#Testing
"""API Contract Validation Tests - Verify all API responses match specification.

Tests ensure that all endpoints return responses with:
- Correct envelope format ({data, error})
- Correct HTTP status codes
- Timestamps in ISO 8601 format
- UUIDs in valid UUID4 format
- Pagination metadata correct
- Required fields present
- No unexpected extra fields

Validates contract compliance without testing business logic.
"""

from datetime import datetime, timedelta
from uuid import uuid4, UUID

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


def is_valid_uuid(value):
    """Check if value is a valid UUID."""
    try:
        UUID(str(value))
        return True
    except (ValueError, AttributeError):
        return False


def is_iso8601_timestamp(value):
    """Check if value is ISO 8601 formatted timestamp."""
    try:
        # Parse ISO format timestamp
        datetime.fromisoformat(value.replace('Z', '+00:00'))
        return True
    except (ValueError, AttributeError):
        return False


class TestResponseEnvelopeFormat:
    """T375.1: Verify all responses use consistent envelope format {data, error}."""

    def test_success_response_has_data_error_fields(self, client):
        """Test successful response has data and error fields."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test Task"},
            headers={"Authorization": f"Bearer {token}"},
        )

        body = response.json()
        assert "data" in body, "Response must have 'data' field"
        assert "error" in body, "Response must have 'error' field"

    def test_error_response_has_data_error_fields(self, client):
        """Test error response has data and error fields."""
        response = client.get("/api/nonexistent-endpoint")

        body = response.json()
        assert "data" in body, "Error response must have 'data' field"
        assert "error" in body, "Error response must have 'error' field"

    def test_success_has_null_error(self, client):
        """Test that successful response has null error."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.json()["error"] is None

    def test_error_has_null_data(self, client):
        """Test that error response has null data."""
        user_id = uuid4()

        response = client.get(f"/api/{user_id}/tasks")

        assert response.json()["data"] is None


class TestHTTPStatusCodes:
    """T375.2: Verify all endpoints return correct HTTP status codes."""

    def test_create_task_returns_201(self, client):
        """Test POST /api/{user_id}/tasks returns 201 Created."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201

    def test_list_tasks_returns_200(self, client):
        """Test GET /api/{user_id}/tasks returns 200 OK."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_get_task_returns_200(self, client):
        """Test GET /api/{user_id}/tasks/{task_id} returns 200 OK."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create task first
        create_resp = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_resp.json()["data"]["id"]

        # Get task
        response = client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_update_task_returns_200(self, client):
        """Test PUT returns 200 OK."""
        user_id = uuid4()
        token = create_token(user_id)

        create_resp = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_resp.json()["data"]["id"]

        response = client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json={"title": "Updated"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_delete_task_returns_200(self, client):
        """Test DELETE returns 200 OK."""
        user_id = uuid4()
        token = create_token(user_id)

        create_resp = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_resp.json()["data"]["id"]

        response = client.delete(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_unauthorized_returns_401(self, client):
        """Test requests without token return 401."""
        user_id = uuid4()

        response = client.get(f"/api/{user_id}/tasks")

        assert response.status_code == 401

    def test_not_found_returns_404(self, client):
        """Test requests for non-existent resources return 404."""
        user_id = uuid4()
        token = create_token(user_id)
        fake_task_id = uuid4()

        response = client.get(
            f"/api/{user_id}/tasks/{fake_task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    def test_forbidden_returns_403(self, client):
        """Test requests with user_id mismatch return 403."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)

        response = client.post(
            f"/api/{user_b_id}/tasks",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        assert response.status_code == 403

    def test_validation_error_returns_422(self, client):
        """Test invalid request data returns 422."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": ""},  # Invalid: empty string
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422


class TestTimestampFormats:
    """T375.3: Verify all timestamps are in ISO 8601 format."""

    def test_task_created_at_is_iso8601(self, client):
        """Test task created_at timestamp is ISO 8601 format."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {token}"},
        )

        created_at = response.json()["data"]["created_at"]
        assert is_iso8601_timestamp(
            created_at
        ), f"created_at '{created_at}' is not ISO 8601 format"

    def test_task_updated_at_is_iso8601(self, client):
        """Test task updated_at timestamp is ISO 8601 format."""
        user_id = uuid4()
        token = create_token(user_id)

        create_resp = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_resp.json()["data"]["id"]

        response = client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json={"title": "Updated"},
            headers={"Authorization": f"Bearer {token}"},
        )

        updated_at = response.json()["data"]["updated_at"]
        assert is_iso8601_timestamp(
            updated_at
        ), f"updated_at '{updated_at}' is not ISO 8601 format"


class TestUUIDFormats:
    """T375.4: Verify all UUIDs are valid UUID4 format."""

    def test_task_id_is_valid_uuid(self, client):
        """Test task ID is valid UUID."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {token}"},
        )

        task_id = response.json()["data"]["id"]
        assert is_valid_uuid(
            task_id
        ), f"task id '{task_id}' is not valid UUID format"

    def test_user_id_is_valid_uuid(self, client):
        """Test user ID is valid UUID."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {token}"},
        )

        returned_user_id = response.json()["data"]["user_id"]
        assert is_valid_uuid(
            returned_user_id
        ), f"user_id '{returned_user_id}' is not valid UUID format"


class TestPaginationContract:
    """T375.5: Verify pagination metadata is correct."""

    def test_pagination_has_required_fields(self, client):
        """Test pagination response has all required fields."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

        pagination = response.json()["data"]["pagination"]
        assert "limit" in pagination
        assert "offset" in pagination
        assert "total" in pagination
        assert "has_more" in pagination

    def test_pagination_values_are_correct_types(self, client):
        """Test pagination values are correct types."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

        pagination = response.json()["data"]["pagination"]
        assert isinstance(pagination["limit"], int)
        assert isinstance(pagination["offset"], int)
        assert isinstance(pagination["total"], int)
        assert isinstance(pagination["has_more"], bool)

    def test_pagination_limit_default_is_10(self, client):
        """Test default limit is 10."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.json()["data"]["pagination"]["limit"] == 10

    def test_pagination_offset_default_is_0(self, client):
        """Test default offset is 0."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.json()["data"]["pagination"]["offset"] == 0

    def test_pagination_has_more_true_when_more_items(self, client):
        """Test has_more is true when there are more items."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create 15 tasks
        for i in range(15):
            client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Task {i+1}"},
                headers={"Authorization": f"Bearer {token}"},
            )

        # Get first 10 (default limit)
        response = client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

        pagination = response.json()["data"]["pagination"]
        assert pagination["total"] == 15
        assert pagination["has_more"] is True

    def test_pagination_has_more_false_when_all_returned(self, client):
        """Test has_more is false when all items returned."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create 5 tasks
        for i in range(5):
            client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Task {i+1}"},
                headers={"Authorization": f"Bearer {token}"},
            )

        # Get all
        response = client.get(
            f"/api/{user_id}/tasks?limit=10&offset=0",
            headers={"Authorization": f"Bearer {token}"},
        )

        pagination = response.json()["data"]["pagination"]
        assert pagination["total"] == 5
        assert pagination["has_more"] is False


class TestTaskResponseFields:
    """T375.6: Verify task response has all required fields with correct types."""

    def test_task_response_has_required_fields(self, client):
        """Test task response includes all required fields."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test Task", "description": "Test Desc"},
            headers={"Authorization": f"Bearer {token}"},
        )

        task = response.json()["data"]
        required_fields = [
            "id",
            "user_id",
            "title",
            "description",
            "completed",
            "created_at",
            "updated_at",
        ]

        for field in required_fields:
            assert field in task, f"Task response missing field: {field}"

    def test_task_field_types_correct(self, client):
        """Test task response field types are correct."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test Task"},
            headers={"Authorization": f"Bearer {token}"},
        )

        task = response.json()["data"]
        assert isinstance(task["id"], str)
        assert isinstance(task["user_id"], str)
        assert isinstance(task["title"], str)
        assert task["description"] is None or isinstance(task["description"], str)
        assert isinstance(task["completed"], bool)
        assert isinstance(task["created_at"], str)
        assert isinstance(task["updated_at"], str)

    def test_task_completed_default_false(self, client):
        """Test that newly created tasks have completed=false."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.json()["data"]["completed"] is False

    def test_task_response_no_extra_fields(self, client):
        """Test task response has no unexpected extra fields."""
        user_id = uuid4()
        token = create_token(user_id)

        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {token}"},
        )

        task = response.json()["data"]
        allowed_fields = {
            "id",
            "user_id",
            "title",
            "description",
            "completed",
            "created_at",
            "updated_at",
            "due_date",
        }

        for field in task.keys():
            assert (
                field in allowed_fields
            ), f"Task has unexpected field: {field}"
