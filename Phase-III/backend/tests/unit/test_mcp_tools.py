"""Unit tests for MCP tool implementations.

Tests each tool independently with valid/invalid inputs,
verifying parameter validation, error handling, and user isolation.
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4, UUID

from src.mcp.tools import (
    add_task,
    list_tasks,
    update_task,
    complete_task,
    delete_task,
)
from src.mcp.schemas import (
    AddTaskInput,
    ListTasksInput,
    UpdateTaskInput,
    CompleteTaskInput,
    DeleteTaskInput,
    TaskPriority,
    TaskStatus,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def user_id():
    """Test user ID."""
    return uuid4()


@pytest.fixture
def task_id():
    """Test task ID."""
    return uuid4()


@pytest.fixture
def add_task_input(user_id):
    """Valid AddTaskInput."""
    return AddTaskInput(
        user_id=user_id,
        title="Buy groceries",
        description="Milk, eggs, bread",
        priority=TaskPriority.HIGH,
        due_date="2026-02-14",
        tags=["shopping"],
    )


@pytest.fixture
def list_tasks_input(user_id):
    """Valid ListTasksInput."""
    return ListTasksInput(
        user_id=user_id,
        status=TaskStatus.INCOMPLETE,
        priority=TaskPriority.HIGH,
        overdue=False,
        limit=10,
        offset=0,
    )


# ============================================================================
# Tests: add_task Tool
# ============================================================================


@pytest.mark.asyncio
async def test_add_task_success(add_task_input):
    """Test successful task creation."""
    mock_response = {
        "data": {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "user_id": str(add_task_input.user_id),
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "priority": "high",
            "completed": False,
            "completed_at": None,
            "due_date": "2026-02-14T00:00:00Z",
            "tags": ["shopping"],
            "created_at": "2026-02-07T10:00:00Z",
            "updated_at": "2026-02-07T10:00:00Z",
        }
    }

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (201, mock_response)

        result = await add_task(add_task_input)

        assert result.success is True
        assert result.data["title"] == "Buy groceries"
        assert "created successfully" in result.message.lower()
        mock_api.assert_called_once()


@pytest.mark.asyncio
async def test_add_task_empty_title():
    """Test validation error with empty title."""
    input_data = AddTaskInput(
        user_id=uuid4(),
        title="",  # Empty title
    )

    result = await add_task(input_data)

    assert result.success is False
    assert "title" in result.error.lower() or "required" in result.error.lower()


@pytest.mark.asyncio
async def test_add_task_validation_error_from_api(add_task_input):
    """Test handling of Phase-II validation error."""
    mock_response = {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Title exceeds maximum length",
            "details": {"title": ["Title exceeds maximum length"]},
        }
    }

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (422, mock_response)

        result = await add_task(add_task_input)

        assert result.success is False
        assert "validation" in result.error.lower()


@pytest.mark.asyncio
async def test_add_task_unauthorized():
    """Test 401 error handling."""
    input_data = AddTaskInput(
        user_id=uuid4(),
        title="Test task",
    )

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (401, {"error": "Unauthorized"})

        result = await add_task(input_data)

        assert result.success is False
        assert "unauthorized" in result.error.lower() or "authorized" in result.message.lower()


@pytest.mark.asyncio
async def test_add_task_forbidden():
    """Test 403 error handling."""
    input_data = AddTaskInput(
        user_id=uuid4(),
        title="Test task",
    )

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (403, {"error": "Forbidden"})

        result = await add_task(input_data)

        assert result.success is False
        assert "permission" in result.message.lower()


# ============================================================================
# Tests: list_tasks Tool
# ============================================================================


@pytest.mark.asyncio
async def test_list_tasks_success(list_tasks_input):
    """Test successful task listing."""
    mock_response = {
        "data": {
            "items": [
                {
                    "id": "660e8400-e29b-41d4-a716-446655440001",
                    "user_id": str(list_tasks_input.user_id),
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                    "priority": "high",
                    "completed": False,
                    "completed_at": None,
                    "due_date": "2026-02-14T00:00:00Z",
                    "tags": ["shopping"],
                    "created_at": "2026-02-07T10:00:00Z",
                    "updated_at": "2026-02-07T10:00:00Z",
                },
            ],
            "total": 1,
        }
    }

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (200, mock_response)

        result = await list_tasks(list_tasks_input)

        assert result.success is True
        assert len(result.tasks) == 1
        assert result.tasks[0].title == "Buy groceries"
        assert result.total_count == 1


@pytest.mark.asyncio
async def test_list_tasks_no_results():
    """Test listing tasks with no results."""
    input_data = ListTasksInput(
        user_id=uuid4(),
        status=TaskStatus.COMPLETED,
    )

    mock_response = {
        "data": {
            "items": [],
            "total": 0,
        }
    }

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (200, mock_response)

        result = await list_tasks(input_data)

        assert result.success is True
        assert len(result.tasks) == 0
        assert result.total_count == 0


@pytest.mark.asyncio
async def test_list_tasks_filters_applied(list_tasks_input):
    """Test that filters are properly applied."""
    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (200, {"data": {"items": [], "total": 0}})

        await list_tasks(list_tasks_input)

        # Verify filters were passed to API
        call_args = mock_api.call_args
        assert call_args is not None
        params = call_args.kwargs.get("params", {})
        assert params.get("status") == "incomplete"
        assert params.get("priority") == "high"


@pytest.mark.asyncio
async def test_list_tasks_unauthorized():
    """Test 401 error handling."""
    input_data = ListTasksInput(user_id=uuid4())

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (401, {"error": "Unauthorized"})

        result = await list_tasks(input_data)

        assert result.success is False
        assert "unauthorized" in result.error.lower()


# ============================================================================
# Tests: update_task Tool
# ============================================================================


@pytest.mark.asyncio
async def test_update_task_success():
    """Test successful task update."""
    user_id = uuid4()
    task_id = uuid4()
    input_data = UpdateTaskInput(
        user_id=user_id,
        task_id=task_id,
        priority=TaskPriority.HIGH,
    )

    mock_response = {
        "data": {
            "id": str(task_id),
            "user_id": str(user_id),
            "title": "Buy groceries",
            "priority": "high",
            "completed": False,
            "completed_at": None,
            "due_date": None,
            "tags": None,
            "created_at": "2026-02-07T10:00:00Z",
            "updated_at": "2026-02-07T11:00:00Z",
        }
    }

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (200, mock_response)

        result = await update_task(input_data)

        assert result.success is True
        assert result.data["priority"] == "high"


@pytest.mark.asyncio
async def test_update_task_not_found():
    """Test 404 error when task not found."""
    input_data = UpdateTaskInput(
        user_id=uuid4(),
        task_id=uuid4(),
        priority=TaskPriority.HIGH,
    )

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (404, {"error": "Task not found"})

        result = await update_task(input_data)

        assert result.success is False
        assert "not found" in result.message.lower()


@pytest.mark.asyncio
async def test_update_task_forbidden():
    """Test 403 error when user doesn't own task."""
    input_data = UpdateTaskInput(
        user_id=uuid4(),
        task_id=uuid4(),
        title="New title",
    )

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (403, {"error": "Forbidden"})

        result = await update_task(input_data)

        assert result.success is False
        assert "permission" in result.message.lower()


# ============================================================================
# Tests: complete_task Tool
# ============================================================================


@pytest.mark.asyncio
async def test_complete_task_success():
    """Test successful task completion."""
    user_id = uuid4()
    task_id = uuid4()
    input_data = CompleteTaskInput(
        user_id=user_id,
        task_id=task_id,
    )

    mock_response = {
        "data": {
            "id": str(task_id),
            "user_id": str(user_id),
            "title": "Buy groceries",
            "completed": True,
            "completed_at": "2026-02-07T11:00:00Z",
            "priority": "high",
            "due_date": None,
            "tags": None,
            "created_at": "2026-02-07T10:00:00Z",
            "updated_at": "2026-02-07T11:00:00Z",
        }
    }

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (200, mock_response)

        result = await complete_task(input_data)

        assert result.success is True
        assert "complete" in result.message.lower()


@pytest.mark.asyncio
async def test_complete_task_not_found():
    """Test 404 error when task not found."""
    input_data = CompleteTaskInput(
        user_id=uuid4(),
        task_id=uuid4(),
    )

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (404, {"error": "Task not found"})

        result = await complete_task(input_data)

        assert result.success is False
        assert "not found" in result.message.lower()


# ============================================================================
# Tests: delete_task Tool
# ============================================================================


@pytest.mark.asyncio
async def test_delete_task_success():
    """Test successful task deletion."""
    user_id = uuid4()
    task_id = uuid4()
    input_data = DeleteTaskInput(
        user_id=user_id,
        task_id=task_id,
    )

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (204, {})

        result = await delete_task(input_data)

        assert result.success is True
        assert "deleted" in result.message.lower()


@pytest.mark.asyncio
async def test_delete_task_not_found():
    """Test 404 error when task not found."""
    input_data = DeleteTaskInput(
        user_id=uuid4(),
        task_id=uuid4(),
    )

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (404, {"error": "Task not found"})

        result = await delete_task(input_data)

        assert result.success is False
        assert "not found" in result.message.lower()


@pytest.mark.asyncio
async def test_delete_task_forbidden():
    """Test 403 error when user doesn't own task."""
    input_data = DeleteTaskInput(
        user_id=uuid4(),
        task_id=uuid4(),
    )

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (403, {"error": "Forbidden"})

        result = await delete_task(input_data)

        assert result.success is False
        assert "permission" in result.message.lower()


# ============================================================================
# Tests: User Isolation
# ============================================================================


@pytest.mark.asyncio
async def test_tools_cannot_access_other_users_data():
    """Test that tools enforce user_id scoping."""
    user_a_id = uuid4()
    user_b_id = uuid4()
    task_id = uuid4()

    # User B tries to update User A's task
    input_data = UpdateTaskInput(
        user_id=user_b_id,
        task_id=task_id,
        priority=TaskPriority.HIGH,
    )

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        # API returns 403 because user_b doesn't own the task
        mock_api.return_value = (403, {"error": "Forbidden"})

        result = await update_task(input_data)

        assert result.success is False
        assert "permission" in result.message.lower()

        # Verify user_id was passed to API call
        call_args = mock_api.call_args
        assert call_args.kwargs["user_id"] == user_b_id


# ============================================================================
# Tests: Error Handling & Resilience
# ============================================================================


@pytest.mark.asyncio
async def test_add_task_api_timeout():
    """Test handling of API timeout."""
    input_data = AddTaskInput(
        user_id=uuid4(),
        title="Test task",
    )

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (504, {"error": "API request timed out"})

        result = await add_task(input_data)

        assert result.success is False


@pytest.mark.asyncio
async def test_list_tasks_api_unavailable():
    """Test handling of API service unavailable."""
    input_data = ListTasksInput(user_id=uuid4())

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = (503, {"error": "API service unavailable"})

        result = await list_tasks(input_data)

        assert result.success is False


@pytest.mark.asyncio
async def test_update_task_malformed_response():
    """Test handling of malformed API response."""
    input_data = UpdateTaskInput(
        user_id=uuid4(),
        task_id=uuid4(),
        title="New title",
    )

    with patch("src.mcp.tools._call_phase2_api", new_callable=AsyncMock) as mock_api:
        # API returns 500 with error
        mock_api.return_value = (500, {"error": {"message": "Internal server error"}})

        result = await update_task(input_data)

        assert result.success is False
        assert "error" in result.error.lower()
