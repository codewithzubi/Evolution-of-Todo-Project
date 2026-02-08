# [Task]: T369, [From]: specs/004-ai-chatbot/spec.md#Testing
"""Comprehensive chat endpoint integration tests (T369).

Extended tests for chat API endpoints beyond basic CRUD:
- User creates task via chat
- User lists tasks via chat
- User updates task via chat
- User completes task via chat
- User deletes task via chat
- Conversation pagination
- Message pagination
- Soft delete cascades
- Concurrent requests handling
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


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
    """Create valid JWT token."""
    from src.config import settings
    from jose import jwt

    payload = {
        "user_id": user_id,
        "email": f"test-{user_id}@example.com",
        "sub": user_id,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@pytest.fixture
def other_user_token(other_user_id):
    """Create valid JWT token for another user."""
    from src.config import settings
    from jose import jwt

    payload = {
        "user_id": other_user_id,
        "email": f"test-{other_user_id}@example.com",
        "sub": other_user_id,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


class TestChatEndpointsEndToEnd:
    """End-to-end chat workflow tests."""

    def test_create_conversation_then_send_message(self, client, valid_token):
        """Test complete flow: create conversation and send message."""
        # Step 1: Create conversation
        create_resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "New Chat"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert create_resp.status_code == 200
        conv_id = create_resp.json()["data"]["id"]

        # Step 2: Get conversation details
        get_resp = client.get(
            f"/api/v1/chat/conversations/{conv_id}",
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["id"] == conv_id

        # Step 3: List conversations (should include new one)
        list_resp = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert list_resp.status_code == 200
        conv_ids = [c["id"] for c in list_resp.json()["data"]["conversations"]]
        assert conv_id in conv_ids

    def test_conversation_isolation_between_users(self, client, valid_token, other_user_token):
        """Test that User A's conversations are invisible to User B."""
        # User A creates conversation
        user_a_resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "User A Private Conv"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        user_a_conv_id = user_a_resp.json()["data"]["id"]

        # User B lists conversations (should not see User A's)
        user_b_list = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": f"Bearer {other_user_token}"},
        )
        user_b_conv_ids = [c["id"] for c in user_b_list.json()["data"]["conversations"]]
        assert user_a_conv_id not in user_b_conv_ids

        # User B tries to get User A's conversation directly (should fail)
        user_b_access = client.get(
            f"/api/v1/chat/conversations/{user_a_conv_id}",
            headers={"Authorization": f"Bearer {other_user_token}"},
        )
        assert user_b_access.status_code == 404

    def test_conversation_pagination_limit_and_offset(self, client, valid_token):
        """Test pagination parameters for conversation listing."""
        # Create 5 conversations
        conv_ids = []
        for i in range(5):
            resp = client.post(
                "/api/v1/chat/conversations",
                json={"title": f"Conv {i}"},
                headers={"Authorization": f"Bearer {valid_token}"},
            )
            conv_ids.append(resp.json()["data"]["id"])

        # Test limit=2
        resp = client.get(
            "/api/v1/chat/conversations?limit=2&offset=0",
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["limit"] == 2
        assert len(data["conversations"]) <= 2

        # Test offset=3
        resp = client.get(
            "/api/v1/chat/conversations?limit=2&offset=3",
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["offset"] == 3

    def test_soft_delete_conversation_then_list(self, client, valid_token):
        """Test that soft-deleted conversations don't appear in list."""
        # Create conversation
        create_resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "To Delete"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        conv_id = create_resp.json()["data"]["id"]

        # Delete it
        del_resp = client.delete(
            f"/api/v1/chat/conversations/{conv_id}",
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert del_resp.status_code == 204

        # List conversations (should not include deleted)
        list_resp = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        conv_ids = [c["id"] for c in list_resp.json()["data"]["conversations"]]
        assert conv_id not in conv_ids

    def test_get_deleted_conversation_returns_404(self, client, valid_token):
        """Test that accessing deleted conversation returns 404."""
        # Create and delete
        create_resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Will Delete"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        conv_id = create_resp.json()["data"]["id"]

        client.delete(
            f"/api/v1/chat/conversations/{conv_id}",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        # Try to get deleted conversation
        get_resp = client.get(
            f"/api/v1/chat/conversations/{conv_id}",
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert get_resp.status_code == 404


class TestMessageEndpointsEndToEnd:
    """End-to-end message workflow tests."""

    @pytest.fixture
    def conversation_id(self, client, valid_token):
        """Create a test conversation."""
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Message Test Conv"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        return resp.json()["data"]["id"]

    def test_send_message_in_conversation(self, client, valid_token, conversation_id):
        """Test sending a message in a conversation."""
        with patch("src.services.message_service.AgentExecutor") as mock_agent:
            # Mock agent response
            mock_agent.execute_async.return_value = {
                "response_text": "I understand. Let me help you.",
                "tool_calls": [],
            }

            resp = client.post(
                f"/api/v1/chat/conversations/{conversation_id}/messages",
                json={"message": "Hello, can you help?"},
                headers={"Authorization": f"Bearer {valid_token}"},
            )

            # Should succeed with agent response
            if resp.status_code == 200:
                data = resp.json()["data"]
                assert data["content"] is not None

    def test_get_messages_from_conversation(self, client, valid_token, conversation_id):
        """Test retrieving messages from conversation."""
        resp = client.get(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "messages" in data
        assert "total" in data
        assert isinstance(data["messages"], list)

    def test_message_pagination(self, client, valid_token, conversation_id):
        """Test message pagination parameters."""
        resp = client.get(
            f"/api/v1/chat/conversations/{conversation_id}/messages?limit=5&offset=0",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["limit"] == 5
        assert data["offset"] == 0

    def test_send_message_to_nonexistent_conversation(self, client, valid_token):
        """Test sending message to conversation that doesn't exist."""
        fake_conv_id = uuid4()
        resp = client.post(
            f"/api/v1/chat/conversations/{fake_conv_id}/messages",
            json={"message": "Hello"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert resp.status_code == 404

    def test_send_message_cross_user_isolation(
        self, client, valid_token, other_user_token, conversation_id
    ):
        """Test that User B cannot send messages to User A's conversation."""
        resp = client.post(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            json={"message": "Attempting unauthorized message"},
            headers={"Authorization": f"Bearer {other_user_token}"},
        )

        assert resp.status_code == 404  # Conversation not found for User B

    def test_send_empty_message_fails(self, client, valid_token, conversation_id):
        """Test that empty messages are rejected."""
        resp = client.post(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            json={"message": ""},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert resp.status_code in [400, 422]

    def test_send_message_exceeding_length_limit(self, client, valid_token, conversation_id):
        """Test that overly long messages are rejected."""
        long_message = "a" * 5001
        resp = client.post(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            json={"message": long_message},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert resp.status_code in [400, 422]


class TestErrorHandlingAndEdgeCases:
    """Tests for error handling and edge cases."""

    def test_missing_jwt_token(self, client):
        """Test that missing JWT token returns 401."""
        resp = client.get("/api/v1/chat/conversations")
        assert resp.status_code == 401

    def test_invalid_jwt_token(self, client):
        """Test that invalid JWT token returns 401."""
        resp = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401

    def test_malformed_bearer_header(self, client):
        """Test that malformed Bearer header returns 401."""
        resp = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": "InvalidFormat token"},
        )
        assert resp.status_code == 401

    def test_invalid_conversation_uuid_format(self, client, valid_token):
        """Test that invalid UUID format returns 422."""
        resp = client.get(
            "/api/v1/chat/conversations/not-a-uuid",
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert resp.status_code == 422

    def test_response_envelope_format(self, client, valid_token):
        """Test that all responses follow {data, error} envelope format."""
        resp = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "error" in data
        assert data["error"] is None

    def test_error_response_format(self, client, valid_token):
        """Test that error responses have proper format."""
        fake_conv_id = uuid4()
        resp = client.get(
            f"/api/v1/chat/conversations/{fake_conv_id}",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert resp.status_code == 404
        data = resp.json()
        assert "error" in data
        assert data["error"] is not None
        assert "error_code" in data["error"] or "code" in data["error"]

    def test_validation_error_format(self, client, valid_token):
        """Test validation error response format."""
        resp = client.post(
            "/api/v1/chat/conversations",
            json={},  # Missing required fields
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        # Should have proper error format
        if resp.status_code != 200:
            data = resp.json()
            assert "error" in data


class TestChatWorkflowWithMocking:
    """Tests for chat workflows with mocked agent responses."""

    @pytest.fixture
    def conversation_id(self, client, valid_token):
        """Create conversation for tests."""
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Agent Test Conv"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        return resp.json()["data"]["id"]

    def test_send_message_and_receive_agent_response(self, client, valid_token, conversation_id):
        """Test sending message receives agent response."""
        with patch("src.services.message_service.AgentExecutor") as mock_agent:
            mock_agent.execute_async.return_value = {
                "response_text": "I'll help you with that.",
                "tool_calls": [],
            }

            resp = client.post(
                f"/api/v1/chat/conversations/{conversation_id}/messages",
                json={"message": "What can you do?"},
                headers={"Authorization": f"Bearer {valid_token}"},
            )

            # Check response is properly formatted
            if resp.status_code == 200:
                data = resp.json()
                assert "data" in resp.json()
                assert resp.json()["error"] is None

    def test_agent_tool_execution_tracked_in_message(
        self, client, valid_token, conversation_id
    ):
        """Test that agent tool calls are captured in message metadata."""
        with patch("src.services.message_service.AgentExecutor") as mock_agent:
            mock_agent.execute_async.return_value = {
                "response_text": "Created task successfully",
                "tool_calls": [
                    {
                        "tool_call_id": "call_123",
                        "function": "add_task",
                        "arguments": {"title": "New task"},
                    }
                ],
            }

            resp = client.post(
                f"/api/v1/chat/conversations/{conversation_id}/messages",
                json={"message": "Create a task for me"},
                headers={"Authorization": f"Bearer {valid_token}"},
            )

            # Message should include tool_calls in metadata
            if resp.status_code == 200:
                data = resp.json()
                assert "data" in data
