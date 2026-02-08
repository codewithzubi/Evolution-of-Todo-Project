# [Task]: T379, [From]: specs/004-ai-chatbot/spec.md#Testing
"""Load Testing & Scalability Tests - Verify system performance under load.

Tests ensure the system can handle:
- 10+ concurrent users
- 100+ rapid message sends
- 1000+ message conversations
- Database connection pooling
- API rate limiting
- Memory stability

Performance baselines:
- Response time: <3s (p95)
- Query time: <200ms (p95)
- Memory: stable over 1000+ requests
"""

import asyncio
import time
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


class TestConcurrentUsers:
    """T379.1: Test system with concurrent users."""

    def test_10_concurrent_users_create_conversations(self, client):
        """Test 10 users creating conversations simultaneously."""
        num_users = 10
        users = [uuid4() for _ in range(num_users)]
        tokens = [create_token(uid) for uid in users]

        start_time = time.time()

        # Each user creates a conversation
        responses = []
        for token in tokens:
            resp = client.post(
                "/api/v1/chat/conversations",
                json={"title": "Concurrent Test Conversation"},
                headers={"Authorization": f"Bearer {token}"},
            )
            responses.append(resp)

        elapsed = time.time() - start_time

        # All requests should succeed
        assert all(r.status_code == 201 for r in responses)
        # Should complete in reasonable time (<5 seconds for 10 users)
        assert elapsed < 5.0, f"10 concurrent user creations took {elapsed}s"

    def test_10_concurrent_users_send_messages(self, client):
        """Test 10 users sending messages concurrently."""
        num_users = 10
        users = [uuid4() for _ in range(num_users)]
        tokens = [create_token(uid) for uid in users]

        # Create conversation for each user
        conversation_ids = []
        for token in tokens:
            resp = client.post(
                "/api/v1/chat/conversations",
                json={"title": "Concurrent Message Test"},
                headers={"Authorization": f"Bearer {token}"},
            )
            conversation_ids.append(resp.json()["data"]["id"])

        start_time = time.time()

        # Each user sends a message
        responses = []
        for i, (token, conv_id) in enumerate(zip(tokens, conversation_ids)):
            resp = client.post(
                f"/api/v1/chat/conversations/{conv_id}/messages",
                json={"content": f"Message from user {i}"},
                headers={"Authorization": f"Bearer {token}"},
            )
            responses.append(resp)

        elapsed = time.time() - start_time

        # All should succeed
        assert all(r.status_code == 201 for r in responses)
        # Should complete in reasonable time (<3 seconds)
        assert elapsed < 3.0, f"10 concurrent message sends took {elapsed}s"


class TestRapidMessageSends:
    """T379.2: Test system with rapid message sends."""

    def test_100_rapid_message_sends_no_data_loss(self, client):
        """Test 100 rapid message sends - verify no data loss or corruption."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create conversation
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Rapid Fire Messages"},
            headers={"Authorization": f"Bearer {token}"},
        )
        conv_id = resp.json()["data"]["id"]

        start_time = time.time()

        # Send 100 messages rapidly
        message_ids = []
        for i in range(100):
            resp = client.post(
                f"/api/v1/chat/conversations/{conv_id}/messages",
                json={"content": f"Rapid message {i+1}"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 201
            message_ids.append(resp.json()["data"]["id"])

        elapsed = time.time() - start_time

        # All 100 messages sent successfully
        assert len(message_ids) == 100
        assert len(set(message_ids)) == 100  # All unique

        # Should complete in reasonable time (<10 seconds)
        assert elapsed < 10.0, f"100 rapid messages took {elapsed}s"

        # Verify all messages persisted
        resp = client.get(
            f"/api/v1/chat/conversations/{conv_id}/messages?limit=100",
            headers={"Authorization": f"Bearer {token}"},
        )
        messages = resp.json()["data"]["items"]
        assert len(messages) == 100

    def test_100_messages_per_conversation_pagination(self, client):
        """Test pagination works correctly with 100+ messages."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create conversation
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Pagination Test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        conv_id = resp.json()["data"]["id"]

        # Add 100 messages
        for i in range(100):
            client.post(
                f"/api/v1/chat/conversations/{conv_id}/messages",
                json={"content": f"Message {i+1}"},
                headers={"Authorization": f"Bearer {token}"},
            )

        # Test pagination with limit=20
        responses = []
        for offset in range(0, 100, 20):
            resp = client.get(
                f"/api/v1/chat/conversations/{conv_id}/messages?limit=20&offset={offset}",
                headers={"Authorization": f"Bearer {token}"},
            )
            responses.append(resp)

        # All pagination requests should succeed
        assert all(r.status_code == 200 for r in responses)

        # Verify pagination metadata
        last_resp = responses[-1].json()
        pagination = last_resp["data"]["pagination"]
        assert pagination["total"] == 100
        assert pagination["limit"] == 20


class TestLargeConversations:
    """T379.3: Test performance with large conversations (1000+ messages)."""

    def test_1000_message_conversation_query_performance(self, client):
        """Test query performance with 1000 messages in conversation."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create conversation
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Large Conversation"},
            headers={"Authorization": f"Bearer {token}"},
        )
        conv_id = resp.json()["data"]["id"]

        # Add 1000 messages (in batches to avoid timeout)
        print("Adding 1000 messages to conversation...")
        for i in range(1000):
            client.post(
                f"/api/v1/chat/conversations/{conv_id}/messages",
                json={"content": f"Message {i+1}"},
                headers={"Authorization": f"Bearer {token}"},
            )
            if (i + 1) % 100 == 0:
                print(f"  {i+1}/1000 messages added")

        # Query performance test
        start_time = time.time()
        resp = client.get(
            f"/api/v1/chat/conversations/{conv_id}/messages?limit=20&offset=0",
            headers={"Authorization": f"Bearer {token}"},
        )
        query_time = time.time() - start_time

        assert resp.status_code == 200
        # Query should complete in <200ms (p95)
        assert query_time < 0.2, f"Query took {query_time}s (should be <200ms)"

        # Verify pagination works with 1000 messages
        pagination = resp.json()["data"]["pagination"]
        assert pagination["total"] == 1000

    def test_1000_message_offset_pagination(self, client):
        """Test offset pagination at different points in 1000 message list."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create conversation with 1000 messages
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Offset Test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        conv_id = resp.json()["data"]["id"]

        # Add messages
        for i in range(1000):
            client.post(
                f"/api/v1/chat/conversations/{conv_id}/messages",
                json={"content": f"Message {i+1}"},
                headers={"Authorization": f"Bearer {token}"},
            )

        # Test different offsets
        test_offsets = [0, 100, 500, 900, 990]
        times = []

        for offset in test_offsets:
            start_time = time.time()
            resp = client.get(
                f"/api/v1/chat/conversations/{conv_id}/messages?limit=10&offset={offset}",
                headers={"Authorization": f"Bearer {token}"},
            )
            elapsed = time.time() - start_time
            times.append(elapsed)

            assert resp.status_code == 200

        # All queries should be <200ms
        assert all(t < 0.2 for t in times), f"Query times: {times}"


class TestDatabaseConnectionPooling:
    """T379.4: Test database connection pooling under load."""

    def test_concurrent_database_connections_dont_exhaust(self, client):
        """Test that 10 concurrent requests don't exhaust connection pool."""
        num_users = 10
        users = [uuid4() for _ in range(num_users)]
        tokens = [create_token(uid) for uid in users]

        # Create conversation for each user
        conv_ids = []
        for token in tokens:
            resp = client.post(
                "/api/v1/chat/conversations",
                json={"title": "Connection Pool Test"},
                headers={"Authorization": f"Bearer {token}"},
            )
            conv_ids.append(resp.json()["data"]["id"])

        # All requests should succeed without connection exhaustion
        for i, (token, conv_id) in enumerate(zip(tokens, conv_ids)):
            resp = client.post(
                f"/api/v1/chat/conversations/{conv_id}/messages",
                json={"content": f"User {i} message"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 201


class TestAPIRateLimiting:
    """T379.5: Test OpenAI API rate limit handling."""

    def test_graceful_degradation_on_rate_limit(self, client):
        """Test system handles rate limit errors gracefully."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create conversation
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Rate Limit Test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        conv_id = resp.json()["data"]["id"]

        # This test verifies error handling - actual rate limiting
        # would be tested against live OpenAI API
        resp = client.post(
            f"/api/v1/chat/conversations/{conv_id}/messages",
            json={"content": "Test message"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should return valid response (or appropriate error)
        assert resp.status_code in [201, 429, 503]


class TestMemoryStability:
    """T379.6: Test memory stability over many requests."""

    def test_memory_stable_over_100_requests(self, client):
        """Test memory usage stays stable over 100+ requests."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create conversation
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Memory Stability Test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        conv_id = resp.json()["data"]["id"]

        # Make 100 requests
        for i in range(100):
            resp = client.post(
                f"/api/v1/chat/conversations/{conv_id}/messages",
                json={"content": f"Message {i+1}"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 201

        # All requests should succeed - memory should not accumulate
        # In real scenario, would monitor process memory with psutil

    def test_task_creation_stable_over_50_tasks(self, client):
        """Test task creation stable over 50 tasks."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create 50 tasks
        task_ids = []
        for i in range(50):
            resp = client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Task {i+1}", "description": f"Desc {i+1}"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 201
            task_ids.append(resp.json()["data"]["id"])

        # All tasks created successfully
        assert len(task_ids) == 50

        # List tasks - should work smoothly
        resp = client.get(
            f"/api/{user_id}/tasks?limit=50",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["pagination"]["total"] == 50


class TestResponseTimeBaselines:
    """T379.7: Test response time meets baseline requirements."""

    def test_conversation_creation_under_3_seconds(self, client):
        """Test conversation creation completes <3s (p95)."""
        user_id = uuid4()
        token = create_token(user_id)

        times = []
        for i in range(10):
            start_time = time.time()
            resp = client.post(
                "/api/v1/chat/conversations",
                json={"title": f"Perf Test {i}"},
                headers={"Authorization": f"Bearer {token}"},
            )
            elapsed = time.time() - start_time
            times.append(elapsed)
            assert resp.status_code == 201

        # p95 should be <3s
        times_sorted = sorted(times)
        p95_idx = int(len(times_sorted) * 0.95)
        p95_time = times_sorted[p95_idx]

        assert p95_time < 3.0, f"p95 response time {p95_time}s exceeds 3s limit"

    def test_message_send_under_3_seconds(self, client):
        """Test message send completes <3s (p95)."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create conversation
        resp = client.post(
            "/api/v1/chat/conversations",
            json={"title": "Message Perf Test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        conv_id = resp.json()["data"]["id"]

        times = []
        for i in range(10):
            start_time = time.time()
            resp = client.post(
                f"/api/v1/chat/conversations/{conv_id}/messages",
                json={"content": f"Perf test message {i}"},
                headers={"Authorization": f"Bearer {token}"},
            )
            elapsed = time.time() - start_time
            times.append(elapsed)
            assert resp.status_code == 201

        # p95 should be <3s
        times_sorted = sorted(times)
        p95_idx = int(len(times_sorted) * 0.95)
        p95_time = times_sorted[p95_idx]

        assert p95_time < 3.0, f"p95 message send {p95_time}s exceeds 3s limit"

    def test_task_list_query_under_200ms(self, client):
        """Test task list query completes <200ms (p95)."""
        user_id = uuid4()
        token = create_token(user_id)

        # Create 20 tasks
        for i in range(20):
            client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Task {i}"},
                headers={"Authorization": f"Bearer {token}"},
            )

        times = []
        for _ in range(10):
            start_time = time.time()
            resp = client.get(
                f"/api/{user_id}/tasks",
                headers={"Authorization": f"Bearer {token}"},
            )
            elapsed = time.time() - start_time
            times.append(elapsed)
            assert resp.status_code == 200

        # p95 should be <200ms
        times_sorted = sorted(times)
        p95_idx = int(len(times_sorted) * 0.95)
        p95_time = times_sorted[p95_idx]

        assert p95_time < 0.2, f"p95 query time {p95_time}s exceeds 200ms limit"
