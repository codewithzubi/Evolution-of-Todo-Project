# [Task]: T326, [From]: specs/004-ai-chatbot/spec.md#FR-010
"""Unit tests for Conversation Context Manager.

Tests message history truncation, formatting for OpenAI API,
and context window management.
"""

import pytest
from datetime import datetime

from src.agents.context_manager import (
    ConversationContextManager,
    create_assistant_message,
    create_system_message,
    create_user_message,
)


class TestConversationContextManager:
    """Test suite for ConversationContextManager."""

    def test_initialization(self):
        """Test context manager initializes with correct max_messages."""
        manager = ConversationContextManager(max_messages=20)
        assert manager.max_messages == 20

    def test_format_messages_empty_list(self):
        """Test formatting empty message list."""
        manager = ConversationContextManager()
        result = manager.format_messages_for_agent([])

        assert result == []

    def test_format_messages_preserves_all_under_limit(self):
        """Test that messages under limit are all preserved."""
        manager = ConversationContextManager(max_messages=10)

        messages = [
            {"role": "user", "content": f"Message {i}"}
            for i in range(5)
        ]

        result = manager.format_messages_for_agent(messages)

        assert len(result) == 5
        assert result[0]["content"] == "Message 0"

    def test_format_messages_truncates_over_limit(self):
        """Test that messages over limit are truncated to last N.

        [Task]: T321, [From]: specs/004-ai-chatbot/plan.md#Decision-4-Token-Window
        Verify that 20-message limit is enforced.
        """
        manager = ConversationContextManager(max_messages=20)

        # Create 30 messages
        messages = [
            {"role": "user" if i % 2 == 0 else "assistant", "content": f"Message {i}"}
            for i in range(30)
        ]

        result = manager.format_messages_for_agent(messages)

        assert len(result) == 20
        assert result[0]["content"] == "Message 10"  # First is 11th from input
        assert result[-1]["content"] == "Message 29"  # Last is last

    def test_format_messages_filters_empty_content(self):
        """Test that messages with empty content are filtered."""
        manager = ConversationContextManager()

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": ""},  # Empty
            {"role": "user", "content": "How are you?"},
        ]

        result = manager.format_messages_for_agent(messages)

        assert len(result) == 2
        assert all(msg["content"] for msg in result)

    def test_format_messages_adds_default_role(self):
        """Test that default role is added if missing."""
        manager = ConversationContextManager()

        messages = [
            {"content": "Message without role"},
        ]

        result = manager.format_messages_for_agent(messages)

        assert len(result) == 1
        assert result[0]["role"] == "user"

    def test_get_message_summary_below_limit(self):
        """Test message summary for conversation below context limit."""
        manager = ConversationContextManager(max_messages=10)

        messages = [
            {"role": "user", "content": "Hi"}
            for _ in range(5)
        ]

        summary = manager.get_message_summary(messages)

        assert summary["total_messages"] == 5
        assert summary["context_window_messages"] == 5
        assert summary["was_truncated"] is False

    def test_get_message_summary_above_limit(self):
        """Test message summary for conversation exceeding context limit."""
        manager = ConversationContextManager(max_messages=10)

        messages = [
            {"role": "user", "content": "M"}
            for _ in range(20)
        ]

        summary = manager.get_message_summary(messages)

        assert summary["total_messages"] == 20
        assert summary["context_window_messages"] == 10
        assert summary["was_truncated"] is True
        assert summary["message_roles"]["user"] == 10

    def test_get_message_summary_token_estimate(self):
        """Test that token estimate is reasonable."""
        manager = ConversationContextManager(max_messages=10)

        messages = [
            {"role": "user", "content": "Hello" * 20}  # ~100 char message
            for _ in range(5)
        ]

        summary = manager.get_message_summary(messages)

        # Should estimate ~40 tokens per message + content length/4
        # 5 messages * 40 + 5 messages * (100/4) = 200 + 125 = ~325 tokens
        assert summary["approximate_tokens"] > 0
        assert summary["approximate_tokens"] < 1000  # Reasonable range

    def test_get_message_summary_role_counts(self):
        """Test that role counts are accurate."""
        manager = ConversationContextManager()

        messages = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm good"},
        ]

        summary = manager.get_message_summary(messages)

        assert summary["message_roles"]["user"] == 2
        assert summary["message_roles"]["assistant"] == 2
        assert summary["message_roles"]["system"] == 0


class TestMessageCreators:
    """Test suite for message creator functions."""

    def test_create_system_message(self):
        """Test creating a system message."""
        msg = create_system_message("You are a helpful assistant")

        assert msg["role"] == "system"
        assert msg["content"] == "You are a helpful assistant"

    def test_create_user_message(self):
        """Test creating a user message."""
        msg = create_user_message("Hello there!")

        assert msg["role"] == "user"
        assert msg["content"] == "Hello there!"

    def test_create_assistant_message(self):
        """Test creating an assistant message."""
        msg = create_assistant_message("Hi! How can I help?")

        assert msg["role"] == "assistant"
        assert msg["content"] == "Hi! How can I help?"

    def test_message_creators_return_dicts(self):
        """Test that message creators return proper dictionaries."""
        sys_msg = create_system_message("System")
        user_msg = create_user_message("User")
        asst_msg = create_assistant_message("Assistant")

        for msg in [sys_msg, user_msg, asst_msg]:
            assert isinstance(msg, dict)
            assert "role" in msg
            assert "content" in msg
            assert len(msg) == 2
