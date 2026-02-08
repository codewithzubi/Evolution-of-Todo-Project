# [Task]: T326, [From]: specs/004-ai-chatbot/spec.md#FR-008
"""Unit tests for Response Parser.

Tests parsing of OpenAI Agents SDK responses, tool call extraction,
and response formatting for frontend consumption.
"""

import json
import pytest
from unittest.mock import MagicMock

from src.agents.response_parser import ResponseParser


class TestResponseParser:
    """Test suite for ResponseParser."""

    def test_parse_agent_response_text_only(self):
        """Test parsing response with text only (no tool calls)."""
        parser = ResponseParser()

        mock_response = MagicMock()
        mock_response.content = "Hello! How can I help?"
        mock_response.tool_calls = None
        mock_response.reasoning = None

        text, tool_calls, reasoning = parser.parse_agent_response(mock_response)

        assert text == "Hello! How can I help?"
        assert tool_calls == []
        assert reasoning is None

    def test_parse_agent_response_with_single_tool_call(self):
        """Test parsing response with a single tool call."""
        parser = ResponseParser()

        mock_func = MagicMock()
        mock_func.name = "list_tasks"
        mock_func.arguments = json.dumps({
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "incomplete"
        })

        mock_call = MagicMock()
        mock_call.function = mock_func

        mock_response = MagicMock()
        mock_response.content = "Let me check your tasks..."
        mock_response.tool_calls = [mock_call]
        mock_response.reasoning = None

        text, tool_calls, reasoning = parser.parse_agent_response(mock_response)

        assert text == "Let me check your tasks..."
        assert len(tool_calls) == 1
        assert tool_calls[0]["name"] == "list_tasks"
        assert tool_calls[0]["params"]["status"] == "incomplete"

    def test_parse_agent_response_with_multiple_tool_calls(self):
        """Test parsing response with multiple tool calls."""
        parser = ResponseParser()

        calls = []
        for i, tool_name in enumerate(["list_tasks", "add_task"]):
            mock_func = MagicMock()
            mock_func.name = tool_name
            mock_func.arguments = json.dumps({"param": f"value{i}"})

            mock_call = MagicMock()
            mock_call.function = mock_func
            calls.append(mock_call)

        mock_response = MagicMock()
        mock_response.content = "I'll list and create tasks"
        mock_response.tool_calls = calls
        mock_response.reasoning = None

        text, tool_calls, reasoning = parser.parse_agent_response(mock_response)

        assert len(tool_calls) == 2
        assert tool_calls[0]["name"] == "list_tasks"
        assert tool_calls[1]["name"] == "add_task"

    def test_parse_agent_response_with_reasoning(self):
        """Test parsing response that includes reasoning."""
        parser = ResponseParser()

        mock_response = MagicMock()
        mock_response.content = "I'll create a task"
        mock_response.tool_calls = None
        mock_response.reasoning = "User asked to create a task called 'Buy milk'"

        text, tool_calls, reasoning = parser.parse_agent_response(mock_response)

        assert reasoning == "User asked to create a task called 'Buy milk'"

    def test_parse_agent_response_invalid_json_in_arguments(self):
        """Test parsing tool call with invalid JSON in arguments."""
        parser = ResponseParser()

        mock_func = MagicMock()
        mock_func.name = "list_tasks"
        mock_func.arguments = "not-valid-json{]}"

        mock_call = MagicMock()
        mock_call.function = mock_func

        mock_response = MagicMock()
        mock_response.content = "Checking tasks..."
        mock_response.tool_calls = [mock_call]
        mock_response.reasoning = None

        text, tool_calls, reasoning = parser.parse_agent_response(mock_response)

        # Should still parse but with empty params due to JSON error
        assert len(tool_calls) == 1
        assert tool_calls[0]["name"] == "list_tasks"
        assert tool_calls[0]["params"] == {}

    def test_parse_agent_response_handles_dict_response(self):
        """Test parsing dictionary-formatted response."""
        parser = ResponseParser()

        response_dict = {
            "content": "Here are your tasks",
            "tool_calls": None,
        }

        text, tool_calls, reasoning = parser.parse_agent_response(response_dict)

        assert text == "Here are your tasks"
        assert tool_calls == []

    def test_parse_agent_response_handles_string_response(self):
        """Test parsing plain string response."""
        parser = ResponseParser()

        response_str = "I'll help you with that!"

        text, tool_calls, reasoning = parser.parse_agent_response(response_str)

        assert text == "I'll help you with that!"
        assert tool_calls == []

    def test_parse_agent_response_empty_raises_error(self):
        """Test that empty response raises ValueError."""
        parser = ResponseParser()

        with pytest.raises(ValueError, match="empty response"):
            parser.parse_agent_response(None)

    def test_format_response_for_frontend(self):
        """Test formatting response for frontend consumption."""
        parser = ResponseParser()

        response = parser.format_response_for_frontend(
            response_text="I've completed your request",
            tool_calls=[
                {"name": "add_task", "params": {}},
                {"name": "list_tasks", "params": {}},
            ],
            reasoning="User asked to create and list tasks",
        )

        assert response["message"] == "I've completed your request"
        assert response["tools_executed"] == ["add_task", "list_tasks"]
        assert response["tool_count"] == 2
        assert response["reasoning"] == "User asked to create and list tasks"

    def test_format_response_for_frontend_no_response_text(self):
        """Test formatting when response text is None."""
        parser = ResponseParser()

        response = parser.format_response_for_frontend(
            response_text=None,
            tool_calls=[],
        )

        assert response["message"] == "I'm processing your request..."
        assert response["tools_executed"] == []

    def test_format_error_response(self):
        """Test formatting error response."""
        parser = ResponseParser()

        response = parser.format_error_response(
            error_code="agent_timeout",
            error_message="Agent execution took too long",
            details={"timeout_seconds": 10},
        )

        assert response["error_code"] == "agent_timeout"
        assert response["message"] == "Agent execution took too long"
        assert response["error"] is True
        assert response["tools_executed"] == []
        assert response["details"]["timeout_seconds"] == 10

    def test_format_error_response_minimal(self):
        """Test formatting error response with minimal details."""
        parser = ResponseParser()

        response = parser.format_error_response(
            error_code="validation_error",
            error_message="Invalid parameters",
        )

        assert response["error_code"] == "validation_error"
        assert response["error"] is True
        assert response["details"] == {}

    def test_parse_tool_calls_empty_list(self):
        """Test parsing empty tool calls list."""
        parser = ResponseParser()

        tool_calls = parser._parse_tool_calls([])

        assert tool_calls == []

    def test_parse_tool_calls_none(self):
        """Test parsing None tool calls."""
        parser = ResponseParser()

        tool_calls = parser._parse_tool_calls(None)

        assert tool_calls == []

    def test_parse_tool_calls_with_dict_format(self):
        """Test parsing tool calls in dictionary format."""
        parser = ResponseParser()

        tool_calls_data = [
            {
                "function": {
                    "name": "add_task",
                    "arguments": json.dumps({"title": "Test", "priority": "high"})
                }
            }
        ]

        tool_calls = parser._parse_tool_calls(tool_calls_data)

        assert len(tool_calls) == 1
        assert tool_calls[0]["name"] == "add_task"
        assert tool_calls[0]["params"]["title"] == "Test"
