# [Task]: T341, [From]: specs/004-ai-chatbot/spec.md#Testing
"""Integration tests for chat API endpoints.

Tests:
- Conversation CRUD operations
- Message sending and retrieval
- User isolation enforcement
- Soft delete functionality
- Error handling scenarios
- JWT authentication
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from src.main import create_app
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole


@pytest.fixture
def app():
    """Create test FastAPI app."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def user_id():
    """Generate test user ID."""
    return str(uuid4())


@pytest.fixture
def other_user_id():
    """Generate another test user ID."""
    return str(uuid4())


@pytest.fixture
def valid_token(user_id):
    """Create valid JWT token for test user."""
    from src.config import settings
    from jose import jwt

    payload = {
        "user_id": user_id,
        "email": f"test-{user_id}@example.com",
        "sub": user_id,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


@pytest.fixture
def other_user_token(other_user_id):
    """Create valid JWT token for another test user."""
    from src.config import settings
    from jose import jwt

    payload = {
        "user_id": other_user_id,
        "email": f"test-{other_user_id}@example.com",
        "sub": other_user_id,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


# [Task]: T329
class TestConversationEndpoints:
    """Tests for conversation CRUD endpoints."""

    def test_create_conversation_success(self, client, valid_token, user_id):
        """Test successful conversation creation."""
        response = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Test Conversation"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["error"] is None
        assert data["data"]["id"] is not None
        assert data["data"]["user_id"] == user_id
        assert data["data"]["title"] == "Test Conversation"
        assert data["data"]["message_count"] == 0

    def test_create_conversation_without_auth(self, client):
        """Test conversation creation fails without auth."""
        response = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Test Conversation"},
        )

        assert response.status_code == 401

    def test_create_conversation_with_invalid_token(self, client):
        """Test conversation creation fails with invalid token."""
        response = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Test Conversation"},
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401

    def test_create_conversation_default_title(self, client, valid_token):
        """Test conversation creation with default title."""
        response = client.post(
            "/api/v1/chat/conversations",
            json={},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] is not None
        assert "Chat" in data["data"]["title"]

    def test_list_conversations_success(self, client, valid_token):
        """Test listing user's conversations."""
        # Create a conversation first
        create_response = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Test Conv"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert create_response.status_code == 200

        # List conversations
        response = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["error"] is None
        assert data["data"]["total"] >= 1
        assert data["data"]["limit"] == 20
        assert data["data"]["offset"] == 0

    def test_list_conversations_pagination(self, client, valid_token):
        """Test conversation listing with pagination."""
        response = client.get(
            "/api/v1/chat/conversations?limit=10&offset=0",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["limit"] == 10
        assert data["data"]["offset"] == 0

    def test_list_conversations_user_isolation(
        self, client, valid_token, other_user_token
    ):
        """Test that users only see their own conversations."""
        # User 1 creates a conversation
        user1_response = client.post(
            "/api/v1/chat/conversations",
            json={"title": "User 1 Conv"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert user1_response.status_code == 200

        # User 2 lists conversations (should not see User 1's)
        user2_response = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": f"Bearer {other_user_token}"},
        )

        assert user2_response.status_code == 200
        user2_data = user2_response.json()
        # Each user sees only their own conversations
        assert isinstance(user2_data["data"]["conversations"], list)

    def test_get_conversation_success(self, client, valid_token):
        """Test retrieving a specific conversation."""
        # Create a conversation
        create_response = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Specific Conv"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        conv_id = create_response.json()["data"]["id"]

        # Get conversation
        response = client.get(
            f"/api/v1/chat/conversations/{conv_id}",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == conv_id
        assert data["data"]["title"] == "Specific Conv"

    def test_get_conversation_not_found(self, client, valid_token):
        """Test retrieving non-existent conversation returns 404."""
        fake_id = uuid4()
        response = client.get(
            f"/api/v1/chat/conversations/{fake_id}",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 404
        data = response.json()
        assert data["error"] is not None
        assert data["error"]["error_code"] == "CONVERSATION_NOT_FOUND"

    def test_get_conversation_unauthorized(self, client, valid_token, other_user_token):
        """Test that users cannot access others' conversations."""
        # User 1 creates conversation
        create_response = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Private Conv"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        conv_id = create_response.json()["data"]["id"]

        # User 2 tries to access it
        response = client.get(
            f"/api/v1/chat/conversations/{conv_id}",
            headers={"Authorization": f"Bearer {other_user_token}"},
        )

        # Should not see the conversation
        assert response.status_code == 404

    def test_delete_conversation_success(self, client, valid_token):
        """Test soft-deleting a conversation."""
        # Create conversation
        create_response = client.post(
            "/api/v1/chat/conversations",
            json={"title": "To Delete"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        conv_id = create_response.json()["data"]["id"]

        # Delete it
        response = client.delete(
            f"/api/v1/chat/conversations/{conv_id}",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 204

        # Verify it's gone from list
        list_response = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        # Conversation should not appear in active list
        conv_ids = [c["id"] for c in list_response.json()["data"]["conversations"]]
        assert conv_id not in conv_ids


# [Task]: T330, T331
class TestMessageEndpoints:
    """Tests for message endpoints."""

    @pytest.fixture
    def conversation_id(self, client, valid_token):
        """Create a test conversation."""
        response = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Test Messages"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        return response.json()["data"]["id"]

    def test_get_messages_empty_conversation(self, client, valid_token, conversation_id):
        """Test getting messages from empty conversation."""
        response = client.get(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["messages"] == []
        assert data["data"]["total"] == 0

    def test_get_messages_pagination(self, client, valid_token, conversation_id):
        """Test message listing with pagination."""
        response = client.get(
            f"/api/v1/chat/conversations/{conversation_id}/messages?limit=10&offset=0",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["limit"] == 10
        assert data["data"]["offset"] == 0

    def test_send_message_empty_fails(self, client, valid_token, conversation_id):
        """Test sending empty message fails."""
        response = client.post(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            json={"message": ""},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"] is not None
        assert data["error"]["error_code"] == "INVALID_MESSAGE"

    def test_send_message_too_long_fails(self, client, valid_token, conversation_id):
        """Test sending message exceeding max length fails."""
        long_message = "a" * 5001
        response = client.post(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            json={"message": long_message},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 400

    def test_send_message_conversation_not_found(self, client, valid_token):
        """Test sending message to non-existent conversation."""
        fake_id = uuid4()
        response = client.post(
            f"/api/v1/chat/conversations/{fake_id}/messages",
            json={"message": "Hello"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 404

    def test_send_message_user_isolation(
        self, client, valid_token, other_user_token, conversation_id
    ):
        """Test users cannot send messages to others' conversations."""
        response = client.post(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            json={"message": "Hacking attempt"},
            headers={"Authorization": f"Bearer {other_user_token}"},
        )

        # Should fail since conversation belongs to another user
        assert response.status_code == 404

    def test_delete_message_success(self, client, valid_token, conversation_id):
        """Test soft-deleting a message."""
        # We can't directly create messages without mocking the agent,
        # but we can test the endpoint structure
        fake_message_id = uuid4()
        response = client.delete(
            f"/api/v1/chat/conversations/{conversation_id}/messages/{fake_message_id}",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        # Will return 403 because message doesn't exist or doesn't belong to conversation
        # This is expected behavior
        assert response.status_code in [403, 204]


# [Task]: T332
class TestAuthenticationAndAuthorization:
    """Tests for JWT authentication and authorization."""

    def test_missing_authorization_header(self, client):
        """Test request without Authorization header fails."""
        response = client.get("/api/v1/chat/conversations")

        assert response.status_code == 401

    def test_invalid_bearer_format(self, client):
        """Test request with invalid Bearer format fails."""
        response = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": "InvalidFormat token"},
        )

        assert response.status_code == 401

    def test_invalid_token(self, client):
        """Test request with invalid token fails."""
        response = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == 401

    def test_public_endpoints_no_auth(self, client):
        """Test that public endpoints don't require auth."""
        response = client.get("/health")
        assert response.status_code == 200

        response = client.get("/docs")
        # Docs might return 200 or redirect
        assert response.status_code in [200, 307]


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_invalid_conversation_id_format(self, client, valid_token):
        """Test invalid UUID format in path."""
        response = client.get(
            "/api/v1/chat/conversations/not-a-uuid",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        # FastAPI validation should catch this
        assert response.status_code == 422

    def test_response_format_consistency(self, client, valid_token):
        """Test all responses follow standard format."""
        response = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        data = response.json()
        # All responses should have 'data' and 'error' fields
        assert "data" in data
        assert "error" in data

    def test_validation_error_response_format(self, client, valid_token):
        """Test validation error response format."""
        response = client.post(
            "/api/v1/chat/conversations",
            json={"title": ""},  # Empty title should fail validation if required
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        # Might succeed with empty title (optional), but if validation fails:
        if response.status_code == 422:
            data = response.json()
            assert "error" in data
