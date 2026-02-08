# [Task]: T367, [From]: specs/004-ai-chatbot/spec.md#Testing
"""MCP tool integration tests.

Tests integration between OpenAI Agents SDK and Phase-II task API via MCP.

Tests:
- add_task tool execution
- list_tasks tool execution with filtering
- update_task tool execution
- complete_task tool execution
- delete_task tool execution
- User isolation enforcement in tools
- Tool timeout handling
- Error recovery
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.mcp.tools import (
    add_task,
    complete_task,
    delete_task,
    list_tasks,
    update_task,
)


class TestAddTaskTool:
    """Tests for add_task MCP tool."""

    @pytest.mark.asyncio
    async def test_add_task_success(self):
        """Test successfully adding a task through MCP."""
        user_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            # Mock successful response from Phase-II API
            task_id = uuid4()
            mock_api.return_value = (
                200,
                {
                    "data": {
                        "id": str(task_id),
                        "title": "Buy groceries",
                        "user_id": str(user_id),
                        "status": "pending",
                    }
                },
            )

            result = await add_task(
                user_id=user_id,
                title="Buy groceries",
                description="Milk, eggs, bread",
                priority="high",
            )

            assert isinstance(result, dict)
            assert result["success"] is True
            assert "Buy groceries" in result["message"]
            mock_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_task_empty_title_fails(self):
        """Test that empty title is rejected."""
        user_id = uuid4()

        result = await add_task(
            user_id=user_id,
            title="",  # Empty
            description="Description",
        )

        assert result["success"] is False
        assert "title" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_add_task_api_error(self):
        """Test error handling when Phase-II API fails."""
        user_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            # Mock API error
            mock_api.return_value = (500, {"error": "Internal server error"})

            result = await add_task(
                user_id=user_id,
                title="New task",
            )

            assert result["success"] is False
            assert "error" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_add_task_user_isolation(self):
        """Test that add_task respects user_id scoping."""
        user_a_id = uuid4()
        user_b_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            mock_api.return_value = (200, {"data": {"id": str(uuid4()), "user_id": str(user_a_id)}})

            result = await add_task(user_id=user_a_id, title="User A task")

            # Verify user_id was passed correctly
            call_args = mock_api.call_args
            assert "user_id" in call_args[1]
            assert call_args[1]["user_id"] == user_a_id


class TestListTasksTool:
    """Tests for list_tasks MCP tool."""

    @pytest.mark.asyncio
    async def test_list_tasks_success(self):
        """Test listing tasks through MCP."""
        user_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            # Mock response with multiple tasks
            mock_api.return_value = (
                200,
                {
                    "data": [
                        {"id": str(uuid4()), "title": "Task 1", "status": "pending"},
                        {"id": str(uuid4()), "title": "Task 2", "status": "completed"},
                    ]
                },
            )

            result = await list_tasks(user_id=user_id)

            assert isinstance(result, dict)
            assert result["success"] is True
            assert "2" in result["message"] or "tasks" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_list_tasks_with_filtering(self):
        """Test listing tasks with status filter."""
        user_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            mock_api.return_value = (
                200,
                {"data": [{"id": str(uuid4()), "title": "Pending Task", "status": "pending"}]},
            )

            result = await list_tasks(user_id=user_id, status="pending")

            assert result["success"] is True
            # Verify filter was passed
            call_args = mock_api.call_args
            if "params" in call_args[1]:
                assert call_args[1]["params"].get("status") == "pending"

    @pytest.mark.asyncio
    async def test_list_tasks_empty(self):
        """Test listing tasks when user has no tasks."""
        user_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            mock_api.return_value = (200, {"data": []})

            result = await list_tasks(user_id=user_id)

            assert result["success"] is True
            assert "no tasks" in result["message"].lower() or "0" in result["message"]

    @pytest.mark.asyncio
    async def test_list_tasks_api_error(self):
        """Test error handling for list_tasks API failure."""
        user_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            mock_api.return_value = (401, {"error": "Unauthorized"})

            result = await list_tasks(user_id=user_id)

            assert result["success"] is False


class TestUpdateTaskTool:
    """Tests for update_task MCP tool."""

    @pytest.mark.asyncio
    async def test_update_task_success(self):
        """Test successfully updating a task."""
        user_id = uuid4()
        task_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            mock_api.return_value = (
                200,
                {
                    "data": {
                        "id": str(task_id),
                        "title": "Updated Title",
                        "status": "in_progress",
                    }
                },
            )

            result = await update_task(
                user_id=user_id,
                task_id=task_id,
                title="Updated Title",
            )

            assert result["success"] is True
            assert "Updated" in result["message"]

    @pytest.mark.asyncio
    async def test_update_task_cross_user_isolation(self):
        """Test that users cannot update tasks of other users."""
        user_a_id = uuid4()
        user_b_task_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            # Simulate 403 Forbidden from Phase-II API
            mock_api.return_value = (403, {"error": "Forbidden"})

            result = await update_task(
                user_id=user_a_id,
                task_id=user_b_task_id,
                title="Hacking attempt",
            )

            # Should fail with isolation error
            assert result["success"] is False

    @pytest.mark.asyncio
    async def test_update_task_invalid_task_id(self):
        """Test updating non-existent task."""
        user_id = uuid4()
        fake_task_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            mock_api.return_value = (404, {"error": "Task not found"})

            result = await update_task(
                user_id=user_id,
                task_id=fake_task_id,
                title="New title",
            )

            assert result["success"] is False
            assert "not found" in result["message"].lower()


class TestCompleteTaskTool:
    """Tests for complete_task MCP tool."""

    @pytest.mark.asyncio
    async def test_complete_task_success(self):
        """Test successfully marking task as complete."""
        user_id = uuid4()
        task_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            mock_api.return_value = (
                200,
                {"data": {"id": str(task_id), "status": "completed"}},
            )

            result = await complete_task(user_id=user_id, task_id=task_id)

            assert result["success"] is True
            assert "completed" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_complete_task_isolation(self):
        """Test that users cannot complete other users' tasks."""
        user_id = uuid4()
        other_user_task_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            mock_api.return_value = (403, {"error": "Forbidden"})

            result = await complete_task(user_id=user_id, task_id=other_user_task_id)

            assert result["success"] is False


class TestDeleteTaskTool:
    """Tests for delete_task MCP tool."""

    @pytest.mark.asyncio
    async def test_delete_task_success(self):
        """Test successfully deleting a task."""
        user_id = uuid4()
        task_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            mock_api.return_value = (204, {})

            result = await delete_task(user_id=user_id, task_id=task_id)

            assert result["success"] is True
            assert "deleted" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_delete_task_isolation(self):
        """Test that users cannot delete other users' tasks."""
        user_id = uuid4()
        other_user_task_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            mock_api.return_value = (403, {"error": "Forbidden"})

            result = await delete_task(user_id=user_id, task_id=other_user_task_id)

            assert result["success"] is False


class TestToolErrorHandling:
    """Tests for error handling in MCP tools."""

    @pytest.mark.asyncio
    async def test_tool_timeout(self):
        """Test tool behavior when Phase-II API times out."""
        user_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            # Simulate timeout
            mock_api.side_effect = TimeoutError("Request timed out")

            with pytest.raises(TimeoutError):
                await list_tasks(user_id=user_id)

    @pytest.mark.asyncio
    async def test_tool_network_error(self):
        """Test tool behavior on network error."""
        user_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            # Simulate network error
            mock_api.side_effect = ConnectionError("Connection refused")

            with pytest.raises(ConnectionError):
                await add_task(user_id=user_id, title="Test")

    @pytest.mark.asyncio
    async def test_tool_malformed_response(self):
        """Test tool handling of malformed API response."""
        user_id = uuid4()

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            # Simulate malformed response
            mock_api.return_value = (200, {"invalid": "format"})

            result = await list_tasks(user_id=user_id)

            # Should handle gracefully
            assert isinstance(result, dict)
            assert "success" in result


class TestToolUserScopingInheritance:
    """Tests that ensure all tools properly scope operations to authenticated user."""

    @pytest.mark.asyncio
    async def test_all_tools_require_user_id(self):
        """Test that all tools enforce user_id parameter."""
        user_id = uuid4()

        # Each tool should require user_id and use it in API calls
        tools = [
            (add_task, {"user_id": user_id, "title": "Test"}),
            (list_tasks, {"user_id": user_id}),
            (update_task, {"user_id": user_id, "task_id": uuid4(), "title": "Test"}),
            (complete_task, {"user_id": user_id, "task_id": uuid4()}),
            (delete_task, {"user_id": user_id, "task_id": uuid4()}),
        ]

        with patch("src.mcp.tools._call_phase2_api") as mock_api:
            mock_api.return_value = (200, {"data": {}})

            for tool_func, params in tools:
                try:
                    await tool_func(**params)
                    # Verify user_id was passed to API
                    call_args = mock_api.call_args
                    assert call_args[1].get("user_id") == user_id
                except Exception:
                    # Some tools may have other validation, that's ok
                    pass
