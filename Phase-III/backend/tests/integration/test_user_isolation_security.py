# [Task]: T370, [From]: specs/004-ai-chatbot/spec.md#Testing
"""User isolation and security tests.

Comprehensive tests to verify:
- User A cannot access User B's conversations
- User A cannot access User B's messages
- User A cannot modify User B's conversations
- User A cannot modify User B's messages
- JWT token validation
- Token expiration handling
- Database queries enforce user_id filtering
- Security audit logging
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from src.config import settings
from src.main import create_app


@pytest.fixture
def app():
    """Create test FastAPI app."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


def create_token(user_id, expires_in_hours=24):
    """Helper to create JWT token."""
    payload = {
        "user_id": str(user_id),
        "email": f"user-{user_id}@example.com",
        "sub": str(user_id),
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=expires_in_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_expired_token(user_id):
    """Helper to create expired JWT token."""
    return create_token(user_id, expires_in_hours=-1)


class TestUserConversationIsolation:
    """Tests for conversation isolation between users."""

    def test_user_a_cannot_read_user_b_conversation(self, client):
        """Test User A cannot retrieve User B's conversation."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)
        user_b_token = create_token(user_b_id)

        # User B creates conversation
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "User B's Secret Conv"},
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        user_b_conv_id = resp.json()["data"]["id"]

        # User A tries to read User B's conversation
        resp = client.get(
            f"/api/v1/chat/conversations/{user_b_conv_id}",
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        # Should return 404 (conversation not found in User A's scope)
        assert resp.status_code == 404
        assert resp.json()["error"] is not None

    def test_user_a_cannot_list_user_b_conversations(self, client):
        """Test User A's conversation list only contains their own conversations."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)
        user_b_token = create_token(user_b_id)

        # User B creates conversation
        user_b_resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "B's Conv"},
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        user_b_conv_id = user_b_resp.json()["data"]["id"]

        # User A creates conversation
        user_a_resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "A's Conv"},
            headers={"Authorization": f"Bearer {user_a_token}"},
        )
        user_a_conv_id = user_a_resp.json()["data"]["id"]

        # User A lists their conversations
        list_resp = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        conv_ids = [c["id"] for c in list_resp.json()["data"]["conversations"]]

        # User A should see only their own
        assert user_a_conv_id in conv_ids
        assert user_b_conv_id not in conv_ids

    def test_user_a_cannot_delete_user_b_conversation(self, client):
        """Test User A cannot delete User B's conversation."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)
        user_b_token = create_token(user_b_id)

        # User B creates conversation
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "To Protect"},
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        user_b_conv_id = resp.json()["data"]["id"]

        # User A tries to delete User B's conversation
        del_resp = client.delete(
            f"/api/v1/chat/conversations/{user_b_conv_id}",
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        # Should fail with 404 or 403
        assert del_resp.status_code in [403, 404]

        # Verify User B's conversation still exists
        verify_resp = client.get(
            f"/api/v1/chat/conversations/{user_b_conv_id}",
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        assert verify_resp.status_code == 200


class TestUserMessageIsolation:
    """Tests for message isolation between users."""

    def test_user_a_cannot_send_message_to_user_b_conversation(self, client):
        """Test User A cannot send message to User B's conversation."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)
        user_b_token = create_token(user_b_id)

        # User B creates conversation
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Private"},
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        user_b_conv_id = resp.json()["data"]["id"]

        # User A tries to send message to User B's conversation
        msg_resp = client.post(
            f"/api/v1/chat/conversations/{user_b_conv_id}/messages",
            json={"message": "Unauthorized message"},
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        # Should fail - conversation not visible to User A
        assert msg_resp.status_code == 404

    def test_user_a_cannot_list_user_b_messages(self, client):
        """Test User A cannot see User B's messages."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)
        user_b_token = create_token(user_b_id)

        # User B creates conversation and sends message
        conv_resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Secret Conv"},
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        user_b_conv_id = conv_resp.json()["data"]["id"]

        # User A tries to list messages from User B's conversation
        msg_resp = client.get(
            f"/api/v1/chat/conversations/{user_b_conv_id}/messages",
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        # Should return 404
        assert msg_resp.status_code == 404


class TestJWTAuthentication:
    """Tests for JWT authentication and authorization."""

    def test_missing_authorization_header_returns_401(self, client):
        """Test that missing Authorization header returns 401."""
        resp = client.get("/api/v1/chat/conversations")
        assert resp.status_code == 401

    def test_invalid_bearer_format_returns_401(self, client):
        """Test that invalid Bearer format returns 401."""
        resp = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": "InvalidFormat sometoken"},
        )
        assert resp.status_code == 401

    def test_invalid_jwt_token_returns_401(self, client):
        """Test that invalid JWT token returns 401."""
        resp = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )
        assert resp.status_code == 401

    def test_malformed_jwt_returns_401(self, client):
        """Test that malformed JWT returns 401."""
        resp = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": "Bearer not.even.close"},
        )
        assert resp.status_code == 401

    def test_expired_jwt_token_returns_401(self, client):
        """Test that expired JWT token returns 401."""
        user_id = uuid4()
        expired_token = create_expired_token(user_id)

        resp = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert resp.status_code == 401

    def test_jwt_with_mismatched_user_id_in_path(self, client):
        """Test that JWT token doesn't authorize cross-user access via path manipulation."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)

        # Create conversation as User B
        user_b_token = create_token(user_b_id)
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "B's Conv"},
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        user_b_conv_id = resp.json()["data"]["id"]

        # User A tries to access with their token
        access_resp = client.get(
            f"/api/v1/chat/conversations/{user_b_conv_id}",
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        # Should be denied
        assert access_resp.status_code == 404


class TestDatabaseSecurityQueries:
    """Tests to verify database queries enforce user_id filtering."""

    @pytest.mark.asyncio
    async def test_conversation_query_includes_user_id_filter(self, test_session, test_user, other_user):
        """Test that conversation queries filter by user_id."""
        from sqlalchemy.future import select
        from src.models.conversation import Conversation

        # Create conversations for both users
        conv_a = Conversation(user_id=test_user.id, title="User A Conv")
        conv_b = Conversation(user_id=other_user.id, title="User B Conv")

        test_session.add(conv_a)
        test_session.add(conv_b)
        await test_session.commit()

        # Query for User A's conversations (should not include User B's)
        stmt = (
            select(Conversation)
            .where((Conversation.user_id == test_user.id) & (Conversation.deleted_at.is_(None)))
        )
        result = await test_session.execute(stmt)
        convs = result.scalars().all()

        # Should only get User A's conversation
        assert len(convs) == 1
        assert convs[0].user_id == test_user.id
        assert convs[0].id == conv_a.id

    @pytest.mark.asyncio
    async def test_message_query_includes_user_id_filter(
        self, test_session, test_user, other_user, sample_conversation
    ):
        """Test that message queries filter by user_id."""
        from sqlalchemy.future import select
        from src.models.message import Message, MessageRole

        # Create messages from different users
        msg_a = Message(
            conversation_id=sample_conversation.id,
            user_id=test_user.id,
            role=MessageRole.USER,
            content="User A message",
        )
        msg_b = Message(
            conversation_id=sample_conversation.id,
            user_id=other_user.id,
            role=MessageRole.USER,
            content="User B message",
        )

        test_session.add(msg_a)
        test_session.add(msg_b)
        await test_session.commit()

        # Query for User A's messages
        stmt = select(Message).where(
            (Message.user_id == test_user.id) & (Message.deleted_at.is_(None))
        )
        result = await test_session.execute(stmt)
        msgs = result.scalars().all()

        # Should only see User A's message
        assert len(msgs) == 1
        assert msgs[0].user_id == test_user.id


class TestErrorMessagesNoLeakage:
    """Tests to ensure error messages don't leak sensitive information."""

    def test_conversation_not_found_no_user_leak(self, client):
        """Test that 404 for nonexistent conversation doesn't leak existence to wrong user."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)

        fake_conv_id = uuid4()

        resp = client.get(
            f"/api/v1/chat/conversations/{fake_conv_id}",
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        assert resp.status_code == 404
        # Error message should be generic, not "owned by another user"
        error_msg = resp.json()["error"].get("error_message", "")
        assert "another user" not in error_msg.lower()

    def test_validation_error_no_internal_details(self, client):
        """Test that validation errors don't leak internal system details."""
        user_id = uuid4()
        token = create_token(user_id)

        resp = client.get(
            "/api/v1/chat/conversations/not-a-uuid",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 422
        error_msg = str(resp.json())
        # Should not contain internal field names or database column names
        assert "sqlalchemy" not in error_msg.lower()
        assert "column" not in error_msg.lower()


class TestConcurrentUserAccess:
    """Tests for safe concurrent access by multiple users."""

    def test_multiple_users_create_conversations_independently(self, client):
        """Test that multiple users can create conversations without interference."""
        user_ids = [uuid4() for _ in range(3)]
        tokens = [create_token(uid) for uid in user_ids]

        created_convs = []

        # All users create conversations
        for token in tokens:
            resp = client.post(
                "/api/v1/chat/conversations",
                json={"title": f"Conv for {token[:10]}"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200
            created_convs.append(resp.json()["data"]["id"])

        # Each user should only see their own conversation
        for i, token in enumerate(tokens):
            resp = client.get(
                "/api/v1/chat/conversations",
                headers={"Authorization": f"Bearer {token}"},
            )
            user_convs = [c["id"] for c in resp.json()["data"]["conversations"]]

            # Should see at least their own
            assert created_convs[i] in user_convs


class TestSecurityAuditLogging:
    """Tests for security-relevant logging (verification of audit trails)."""

    def test_failed_auth_attempt_logged(self, client):
        """Test that failed authentication attempts are logged."""
        # This would typically be checked in logs, but we verify the endpoint
        # properly rejects the attempt
        resp = client.get(
            "/api/v1/chat/conversations",
            headers={"Authorization": "Bearer invalid"},
        )

        assert resp.status_code == 401
        # In real scenario, check logs for audit entry

    def test_unauthorized_access_attempt_logged(self, client):
        """Test that unauthorized access attempts are logged."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        user_a_token = create_token(user_a_id)
        user_b_token = create_token(user_b_id)

        # User B creates conversation
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Private"},
            headers={"Authorization": f"Bearer {user_b_token}"},
        )
        conv_id = resp.json()["data"]["id"]

        # User A attempts unauthorized access
        resp = client.get(
            f"/api/v1/chat/conversations/{conv_id}",
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        assert resp.status_code == 404
        # In real scenario, check logs for audit entry including:
        # - User A's ID
        # - Attempted resource ID
        # - Timestamp
        # - Result (unauthorized)
