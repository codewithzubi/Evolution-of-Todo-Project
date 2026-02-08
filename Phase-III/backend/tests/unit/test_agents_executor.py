# [Task]: T326, [From]: specs/004-ai-chatbot/spec.md#FR-008
"""Unit tests for OpenAI Agents SDK executor.

Tests agent execution flows, error handling, message formatting,
and context window management.
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.context_manager import ConversationContextManager
from src.agents.executor import AgentExecutor
from src.agents.response_parser import ResponseParser


@pytest.mark.asyncio
class TestAgentExecutor:
    """Test suite for AgentExecutor."""

    @pytest.fixture
    def mock_openai_client(self):
        """Create mock OpenAI client."""
        return MagicMock()

    @pytest.fixture
    def agent_executor(self, mock_openai_client):
        """Create AgentExecutor with mocked client."""
        executor = AgentExecutor()
        executor.client = AsyncMock()
        return executor

    async def test_agent_executor_initialization(self):
        """Test agent executor initializes with correct config."""
        executor = AgentExecutor()

        assert executor.api_key
        assert executor.model == "gpt-4-turbo-preview"
        assert executor.timeout == 10
        assert executor.max_messages == 20

    async def test_agent_executor_requires_api_key(self):
        """Test that AgentExecutor raises error without API key."""
        with patch("src.agents.executor.settings.openai_api_key", ""):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                AgentExecutor()

    async def test_execute_with_empty_message_raises_error(self, agent_executor):
        """Test that execute rejects empty user messages."""
        user_id = uuid4()

        with pytest.raises(ValueError, match="cannot be empty"):
            await agent_executor.execute(
                user_id=user_id,
                user_message="",
                conversation_history=[],
            )

    async def test_execute_formats_message_history(self, agent_executor):
        """Test that execute properly formats conversation history."""
        user_id = uuid4()

        # Mock agent response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = "Hello!"
        mock_response.choices[0].message.tool_calls = None

        agent_executor.client.chat.completions.create = AsyncMock(return_value=mock_response)

        history = [
            {"role": "user", "content": "Hi there", "created_at": "2026-02-07T10:00:00Z"},
            {"role": "assistant", "content": "Hello!", "created_at": "2026-02-07T10:01:00Z"},
        ]

        result = await agent_executor.execute(
            user_id=user_id,
            user_message="How are you?",
            conversation_history=history,
        )

        assert result["success"] is True
        # Verify client was called with formatted messages
        agent_executor.client.chat.completions.create.assert_called_once()

    async def test_execute_respects_context_window_limit(self, agent_executor):
        """Test that agent executor truncates history to context window."""
        user_id = uuid4()

        # Create 30 messages (exceeds 20-message limit)
        history = [
            {"role": "user" if i % 2 == 0 else "assistant", "content": f"Message {i}"}
            for i in range(30)
        ]

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = "Response"
        mock_response.choices[0].message.tool_calls = None

        agent_executor.client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await agent_executor.execute(
            user_id=user_id,
            user_message="Test",
            conversation_history=history,
        )

        assert result["success"] is True

    async def test_execute_handles_timeout(self, agent_executor):
        """Test that execute handles OpenAI API timeout."""
        user_id = uuid4()

        # Mock timeout
        agent_executor.client.chat.completions.create = AsyncMock(
            side_effect=TimeoutError("API timeout")
        )

        with patch("asyncio.wait_for", side_effect=TimeoutError()):
            result = await agent_executor.execute(
                user_id=user_id,
                user_message="Test",
                conversation_history=[],
            )

        assert result["success"] is False
        assert result["error_code"] == "AGENT_TIMEOUT"

    async def test_execute_handles_validation_error(self, agent_executor):
        """Test that execute handles validation errors."""
        user_id = uuid4()

        agent_executor.client.chat.completions.create = AsyncMock(
            side_effect=ValueError("Invalid parameter")
        )

        with patch.object(agent_executor, "_execute_agent_loop", side_effect=ValueError("Invalid")):
            result = await agent_executor.execute(
                user_id=user_id,
                user_message="Test",
                conversation_history=[],
            )

        assert result["success"] is False
        assert result["error_code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
class TestContextManager:
    """Test suite for ConversationContextManager."""

    def test_context_manager_initialization(self):
        """Test context manager initializes with correct max_messages."""
        manager = ConversationContextManager(max_messages=20)
        assert manager.max_messages == 20

    def test_format_messages_for_agent_empty_list(self):
        """Test formatting empty message list."""
        manager = ConversationContextManager()
        result = manager.format_messages_for_agent([])

        assert result == []

    def test_format_messages_for_agent_truncates_to_window(self):
        """Test that formatting truncates to message window."""
        manager = ConversationContextManager(max_messages=10)

        # Create 20 messages
        messages = [
            {"role": "user", "content": f"Message {i}"}
            for i in range(20)
        ]

        result = manager.format_messages_for_agent(messages)

        assert len(result) == 10  # Only last 10
        assert result[0]["content"] == "Message 10"  # First in result is 11th in input

    def test_format_messages_for_agent_preserves_role(self):
        """Test that formatting preserves message roles."""
        manager = ConversationContextManager()

        messages = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"},
        ]

        result = manager.format_messages_for_agent(messages)

        assert result[0]["role"] == "user"
        assert result[1]["role"] == "assistant"

    def test_get_message_summary(self):
        """Test message summary calculation."""
        manager = ConversationContextManager(max_messages=10)

        messages = [
            {"role": "user", "content": "Hi"}
            for _ in range(15)
        ]

        summary = manager.get_message_summary(messages)

        assert summary["total_messages"] == 15
        assert summary["context_window_messages"] == 10
        assert summary["was_truncated"] is True
        assert summary["message_roles"]["user"] == 15


@pytest.mark.asyncio
class TestResponseParser:
    """Test suite for ResponseParser."""

    def test_parse_agent_response_with_text_only(self):
        """Test parsing response with text only (no tool calls)."""
        parser = ResponseParser()

        mock_response = MagicMock()
        mock_response.content = "Hello there!"
        mock_response.tool_calls = None

        text, tool_calls, reasoning = parser.parse_agent_response(mock_response)

        assert text == "Hello there!"
        assert tool_calls == []
        assert reasoning is None

    def test_parse_agent_response_with_tool_calls(self):
        """Test parsing response with tool calls."""
        parser = ResponseParser()

        mock_func = MagicMock()
        mock_func.name = "list_tasks"
        mock_func.arguments = '{"user_id": "123", "status": "incomplete"}'

        mock_call = MagicMock()
        mock_call.function = mock_func

        mock_response = MagicMock()
        mock_response.content = "Let me check your tasks..."
        mock_response.tool_calls = [mock_call]

        text, tool_calls, reasoning = parser.parse_agent_response(mock_response)

        assert text == "Let me check your tasks..."
        assert len(tool_calls) == 1
        assert tool_calls[0]["name"] == "list_tasks"

    def test_format_response_for_frontend(self):
        """Test formatting response for frontend consumption."""
        parser = ResponseParser()

        response = parser.format_response_for_frontend(
            response_text="Here are your tasks",
            tool_calls=[{"name": "list_tasks", "params": {}}],
            reasoning="User asked for task list",
        )

        assert response["message"] == "Here are your tasks"
        assert response["tools_executed"] == ["list_tasks"]
        assert response["reasoning"] == "User asked for task list"

    def test_format_error_response(self):
        """Test formatting error response."""
        parser = ResponseParser()

        response = parser.format_error_response(
            error_code="agent_timeout",
            error_message="Agent took too long",
        )

        assert response["error_code"] == "agent_timeout"
        assert response["message"] == "Agent took too long"
        assert response["error"] is True
