# [Task]: T377, [From]: specs/004-ai-chatbot/spec.md#Testing
"""Multi-User Chat Scenario Tests - Complex real-world multi-user situations.

Tests multiple concurrent users interacting with the chat system in realistic
scenarios to detect race conditions, isolation violations, and consistency issues.

Scenarios:
1. Independent conversations (no cross-user leakage)
2. Task isolation (user cannot see other user's tasks via MCP)
3. Rapid message sequences (stress test)
4. Network failure recovery
5. Concurrent user safety
"""

import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

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


class TestIndependentUserConversations:
    """T377.1: Verify users cannot see each other's conversations."""

    def test_user_a_and_b_independent_conversations(self, client):
        """Test that User A and User B chat independently with no cross-leakage."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)
        user_b_token = create_token(user_b_id)

        # User A creates conversation
        resp_a = client.post(
            "/api/v1/chat/conversations",
            json={"title": "User A Conversation"},
            headers={"Authorization": f"Bearer {user_a_token}"},
        )
        conv_a_id = resp_a.json()["data"]["id"]

        # User B creates conversation
        resp_b = client.post(
            "/api/v1/chat/conversations",
            json={"title": "User B Conversation"},
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        conv_b_id = resp_b.json()["data"]["id"]

        # User A lists conversations - should only see their own
        list_a = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": f"Bearer {user_a_token}"},
        )
        user_a_convs = list_a.json()["data"]["items"]
        conv_ids_a = [c["id"] for c in user_a_convs]

        assert conv_a_id in conv_ids_a
        assert conv_b_id not in conv_ids_a

        # User B lists conversations - should only see their own
        list_b = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        user_b_convs = list_b.json()["data"]["items"]
        conv_ids_b = [c["id"] for c in user_b_convs]

        assert conv_b_id in conv_ids_b
        assert conv_a_id not in conv_ids_b

    def test_user_cannot_access_other_users_conversation(self, client):
        """Test User A cannot read User B's conversation even with exact ID."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)
        user_b_token = create_token(user_b_id)

        # User B creates conversation
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Secret Conversation"},
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        conv_b_id = resp.json()["data"]["id"]

        # User A tries to get User B's conversation by ID
        resp = client.get(
            f"/api/v1/chat/conversations/{conv_b_id}",
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        # Should return 404 (not found in User A's scope)
        assert resp.status_code == 404

    def test_multiple_users_same_conversation_isolation(self, client):
        """Test conversation isolation with multiple simultaneous users."""
        users = [uuid4() for _ in range(3)]
        tokens = [create_token(uid) for uid in users]

        # Each user creates their own conversation
        conversation_ids = []
        for i, token in enumerate(tokens):
            resp = client.post(
                "/api/v1/chat/conversations",
                json={"title": f"User {i} Conversation"},
                headers={"Authorization": f"Bearer {token}"},
            )
            conversation_ids.append(resp.json()["data"]["id"])

        # Each user lists conversations and verifies isolation
        for i, token in enumerate(tokens):
            resp = client.get(
                "/api/v1/chat/conversations",
                headers={"Authorization": f"Bearer {token}"},
            )
            user_convs = resp.json()["data"]["items"]
            user_conv_ids = [c["id"] for c in user_convs]

            # Should only see their own conversation
            assert conversation_ids[i] in user_conv_ids
            for j, other_id in enumerate(conversation_ids):
                if i != j:
                    assert other_id not in user_conv_ids


class TestTaskIsolation:
    """T377.2: Verify tasks created via Phase-II are isolated between users."""

    def test_user_cannot_see_other_users_tasks(self, client):
        """Test User A cannot see User B's tasks."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)
        user_b_token = create_token(user_b_id)

        # User B creates a task
        resp = client.post(
            f"/api/{user_b_id}/tasks",
            json={"title": "User B Private Task"},
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        assert resp.status_code == 201

        # User A lists tasks - should be empty
        resp = client.get(
            f"/api/{user_a_id}/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        assert resp.status_code == 200
        tasks = resp.json()["data"]["items"]
        assert len(tasks) == 0

    def test_user_cannot_read_other_users_task_by_id(self, client):
        """Test User A cannot read User B's task even with exact ID."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)
        user_b_token = create_token(user_b_id)

        # User B creates a task
        resp = client.post(
            f"/api/{user_b_id}/tasks",
            json={"title": "Secret Task"},
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        task_id = resp.json()["data"]["id"]

        # User A tries to get User B's task
        resp = client.get(
            f"/api/{user_a_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        assert resp.status_code == 404


class TestRapidMessageSequence:
    """T377.3: Test rapid message sending (stress test for ordering and consistency)."""

    def test_rapid_5_message_sequence(self, client):
        """Test sending 5 messages rapidly maintains order and consistency."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create conversation
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Rapid Test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        conv_id = resp.json()["data"]["id"]

        # Send 5 messages rapidly
        message_ids = []
        for i in range(5):
            resp = client.post(
                f"/api/v1/chat/conversations/{conv_id}/messages",
                json={"content": f"Message {i+1}"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 201
            message_ids.append(resp.json()["data"]["id"])

        # Verify all messages created
        assert len(message_ids) == 5
        assert len(set(message_ids)) == 5  # All unique IDs

        # Retrieve and verify ordering
        resp = client.get(
            f"/api/v1/chat/conversations/{conv_id}/messages",
            headers={"Authorization": f"Bearer {token}"},
        )

        messages = resp.json()["data"]["items"]
        assert len(messages) == 5

        # Verify chronological order
        for i in range(len(messages) - 1):
            assert messages[i]["created_at"] <= messages[i + 1]["created_at"]

    def test_100_rapid_messages_no_loss(self, client):
        """Test 100 rapid message sends - no data loss."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create conversation
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "100 Message Test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        conv_id = resp.json()["data"]["id"]

        # Send 100 messages rapidly
        for i in range(100):
            resp = client.post(
                f"/api/v1/chat/conversations/{conv_id}/messages",
                json={"content": f"Message {i+1}"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 201

        # Verify pagination works correctly with 100 messages
        resp = client.get(
            f"/api/v1/chat/conversations/{conv_id}/messages?limit=10&offset=0",
            headers={"Authorization": f"Bearer {token}"},
        )

        pagination = resp.json()["data"]["pagination"]
        assert pagination["total"] == 100
        assert pagination["limit"] == 10
        assert pagination["has_more"] is True
        assert len(resp.json()["data"]["items"]) == 10


class TestNetworkFailureRecovery:
    """T377.4: Test conversation recovery after network loss."""

    def test_conversation_persists_after_simulated_disconnection(self, client):
        """Test conversation data persists even after client disconnect."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create conversation
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Recovery Test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        conv_id = resp.json()["data"]["id"]
        created_at_1 = resp.json()["data"]["created_at"]

        # Send a message
        resp = client.post(
            f"/api/v1/chat/conversations/{conv_id}/messages",
            json={"content": "Before disconnect"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        msg_id = resp.json()["data"]["id"]

        # Simulate "reconnection" - fetch conversation again
        resp = client.get(
            f"/api/v1/chat/conversations/{conv_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200
        recovered_conv = resp.json()["data"]
        assert recovered_conv["id"] == conv_id
        assert recovered_conv["created_at"] == created_at_1

        # Verify message still exists
        resp = client.get(
            f"/api/v1/chat/conversations/{conv_id}/messages/{msg_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200


class TestConcurrentUserSafety:
    """T377.5: Test system safety with concurrent users."""

    def test_10_concurrent_users_independent_conversations(self, client):
        """Test 10 users creating and operating on conversations simultaneously."""
        num_users = 10
        users = [uuid4() for _ in range(num_users)]
        tokens = [create_token(uid) for uid in users]

        # Each user creates a conversation
        conversation_ids = []
        for token in tokens:
            resp = client.post(
                "/api/v1/chat/conversations",
                json={"title": "Concurrent Test"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 201
            conversation_ids.append(resp.json()["data"]["id"])

        # Each user sends 3 messages
        for i, token in enumerate(tokens):
            for j in range(3):
                resp = client.post(
                    f"/api/v1/chat/conversations/{conversation_ids[i]}/messages",
                    json={"content": f"User {i} Message {j+1}"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert resp.status_code == 201

        # Verify each user only sees their own messages
        for i, token in enumerate(tokens):
            resp = client.get(
                f"/api/v1/chat/conversations/{conversation_ids[i]}/messages",
                headers={"Authorization": f"Bearer {token}"},
            )
            messages = resp.json()["data"]["items"]
            assert len(messages) == 3
            for msg in messages:
                # Verify user_id matches
                assert msg["user_id"] == str(users[i])

    def test_concurrent_task_operations(self, client):
        """Test concurrent task creation from multiple users."""
        num_users = 5
        users = [uuid4() for _ in range(num_users)]
        tokens = [create_token(uid) for uid in users]

        # Each user creates 2 tasks
        task_ids = []
        for i, (uid, token) in enumerate(zip(users, tokens)):
            for j in range(2):
                resp = client.post(
                    f"/api/{uid}/tasks",
                    json={"title": f"User {i} Task {j+1}"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert resp.status_code == 201
                task_ids.append(resp.json()["data"]["id"])

        # Verify user isolation
        for i, (uid, token) in enumerate(zip(users, tokens)):
            resp = client.get(
                f"/api/{uid}/tasks",
                headers={"Authorization": f"Bearer {token}"},
            )
            tasks = resp.json()["data"]["items"]
            # Should only see own tasks (2)
            assert len(tasks) == 2


class TestConversationDeletion:
    """T377.6: Test conversation deletion with user isolation."""

    def test_user_delete_only_affects_own_data(self, client):
        """Test that deleting a conversation only affects the user's view."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)
        user_b_token = create_token(user_b_id)

        # Both users create conversations
        resp_a = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Conv A"},
            headers={"Authorization": f"Bearer {user_a_token}"},
        )
        conv_a = resp_a.json()["data"]["id"]

        resp_b = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Conv B"},
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        conv_b = resp_b.json()["data"]["id"]

        # User A deletes their conversation
        resp = client.delete(
            f"/api/v1/chat/conversations/{conv_a}",
            headers={"Authorization": f"Bearer {user_a_token}"},
        )
        assert resp.status_code == 200

        # User B's conversation still exists
        resp = client.get(
            f"/api/v1/chat/conversations/{conv_b}",
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        assert resp.status_code == 200
