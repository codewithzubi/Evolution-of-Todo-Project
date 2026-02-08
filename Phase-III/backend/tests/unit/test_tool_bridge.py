# [Task]: T326, [From]: specs/004-ai-chatbot/spec.md#FR-017
"""Unit tests for Tool Invocation Bridge.

Tests MCP tool invocation, user context injection, cross-user access prevention,
and tool result formatting.
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from src.agents.tool_bridge import ToolInvocationBridge


@pytest.mark.asyncio
class TestToolInvocationBridge:
    """Test suite for ToolInvocationBridge."""

    async def test_invoke_tool_success(self):
        """Test successful tool invocation."""
        user_id = uuid4()

        mock_result = {
            "success": True,
            "data": {"id": "task-1", "title": "Test Task"},
            "message": "Task created successfully!",
        }

        with patch("src.agents.tool_bridge.MCPToolExecutor.execute_tool", new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result

            result = await ToolInvocationBridge.invoke_tool(
                tool_name="add_task",
                tool_params={"title": "Test Task"},
                user_id=user_id,
            )

        assert result["success"] is True
        assert result["message"] == "Task created successfully!"

    async def test_invoke_tool_injects_user_id(self):
        """Test that invoke_tool injects user_id from JWT."""
        user_id = uuid4()
        tool_params = {"title": "Test"}

        with patch("src.agents.tool_bridge.MCPToolExecutor.execute_tool", new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {"success": True}

            await ToolInvocationBridge.invoke_tool(
                tool_name="add_task",
                tool_params=tool_params,
                user_id=user_id,
            )

        # Verify user_id was injected
        called_params = mock_execute.call_args[0][1]
        assert str(called_params["user_id"]) == str(user_id)

    async def test_invoke_tool_prevents_cross_user_access(self):
        """Test that invoke_tool prevents cross-user access.

        [Task]: T323, [From]: specs/004-ai-chatbot/spec.md#FR-018
        Verify that if a tool call attempts to use a different user_id,
        it is rejected with proper error.
        """
        jwt_user_id = uuid4()
        other_user_id = uuid4()

        result = await ToolInvocationBridge.invoke_tool(
            tool_name="list_tasks",
            tool_params={"user_id": str(other_user_id)},
            user_id=jwt_user_id,
        )

        assert result["success"] is False
        assert result["error"] == "user_id_mismatch"

    async def test_invoke_tool_handles_validation_error(self):
        """Test handling of validation errors."""
        user_id = uuid4()

        with patch("src.agents.tool_bridge.MCPToolExecutor.execute_tool", side_effect=ValueError("Invalid param")):
            result = await ToolInvocationBridge.invoke_tool(
                tool_name="add_task",
                tool_params={"title": ""},
                user_id=user_id,
            )

        assert result["success"] is False
        assert result["error"] == "tool_validation_error"

    async def test_format_tool_result_as_message_success(self):
        """Test formatting successful tool result as message."""
        result = {
            "success": True,
            "data": {"title": "Buy groceries"},
            "message": "Task created!",
        }

        message = ToolInvocationBridge.format_tool_result_as_agent_message("add_task", result)

        assert "Task created!" in message

    async def test_format_tool_result_as_message_list_tasks(self):
        """Test formatting list_tasks result."""
        result = {
            "success": True,
            "tasks": [{"id": "1", "title": "Task 1"}],
            "total_count": 1,
        }

        message = ToolInvocationBridge.format_tool_result_as_agent_message("list_tasks", result)

        assert "1 tasks" in message

    async def test_format_tool_result_as_message_error(self):
        """Test formatting error result as message."""
        result = {
            "success": False,
            "error": "task_not_found",
            "message": "Task not found",
        }

        message = ToolInvocationBridge.format_tool_result_as_agent_message("delete_task", result)

        assert "Error" in message or "not found" in message

    async def test_handle_tool_call_from_agent(self):
        """Test handling complete tool call from agent."""
        user_id = uuid4()

        tool_call = {
            "name": "list_tasks",
            "params": {"status": "incomplete"},
        }

        mock_result = {
            "success": True,
            "tasks": [],
            "total_count": 0,
        }

        with patch.object(ToolInvocationBridge, "invoke_tool", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result

            result = await ToolInvocationBridge.handle_tool_call_from_agent(
                tool_call=tool_call,
                user_id=user_id,
            )

        assert result["tool_name"] == "list_tasks"
        assert result["success"] is True
        assert "agent_message" in result

    async def test_handle_tool_call_missing_name(self):
        """Test handling tool call with missing name."""
        user_id = uuid4()

        tool_call = {
            "params": {"title": "Test"},
        }

        with pytest.raises(ValueError, match="missing 'name'"):
            await ToolInvocationBridge.handle_tool_call_from_agent(
                tool_call=tool_call,
                user_id=user_id,
            )


@pytest.mark.asyncio
class TestUserIsolation:
    """Test suite for user isolation in tool invocation."""

    async def test_tool_invocation_respects_user_id_from_jwt(self):
        """Test that tool invocations use user_id from JWT, not from params.

        [Task]: T323, [From]: specs/004-ai-chatbot/spec.md#FR-017
        Verify user_id is extracted from JWT and passed to MCP tools.
        """
        jwt_user_id = uuid4()

        with patch("src.agents.tool_bridge.MCPToolExecutor.execute_tool", new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {"success": True}

            await ToolInvocationBridge.invoke_tool(
                tool_name="list_tasks",
                tool_params={},
                user_id=jwt_user_id,
            )

        # Verify JWT user_id was used
        called_params = mock_execute.call_args[0][1]
        assert str(called_params["user_id"]) == str(jwt_user_id)

    async def test_cannot_list_other_users_tasks(self):
        """Test that user cannot list another user's tasks."""
        user_a_id = uuid4()
        user_b_id = uuid4()

        # User A tries to invoke with User B's ID
        result = await ToolInvocationBridge.invoke_tool(
            tool_name="list_tasks",
            tool_params={"user_id": str(user_b_id)},
            user_id=user_a_id,
        )

        assert result["success"] is False
        assert result["error"] == "user_id_mismatch"

    async def test_cannot_delete_other_users_tasks(self):
        """Test that user cannot delete another user's tasks."""
        user_a_id = uuid4()
        user_b_id = uuid4()
        task_id = uuid4()

        # User A tries to delete User B's task
        result = await ToolInvocationBridge.invoke_tool(
            tool_name="delete_task",
            tool_params={"user_id": str(user_b_id), "task_id": str(task_id)},
            user_id=user_a_id,
        )

        assert result["success"] is False
        assert result["error"] == "user_id_mismatch"
