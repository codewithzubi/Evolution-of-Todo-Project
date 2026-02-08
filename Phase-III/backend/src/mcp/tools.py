"""MCP Tool implementations that wrap Phase-II task APIs.

Each tool is stateless and user-scoped via user_id from JWT tokens.
Tools call existing Phase-II endpoints directly; no direct database queries.

All tools handle errors gracefully and return user-friendly messages.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, select

from ..config import settings
from ..models.task import Task
from .schemas import (
    AddTaskInput,
    CompleteTaskInput,
    DeleteTaskInput,
    ListTasksInput,
    ListTasksOutput,
    TaskOutput,
    ToolResult,
    UpdateTaskInput,
)

logger = logging.getLogger(__name__)

# Create synchronous database session for tools
_db_engine = None
_SessionLocal = None

def _get_db_session() -> Session:
    """Get a synchronous database session for tools."""
    global _db_engine, _SessionLocal

    if _db_engine is None:
        _db_engine = create_engine(
            settings.database_url.replace("postgresql+asyncpg", "postgresql"),
            pool_pre_ping=True,
            echo=False
        )
        _SessionLocal = sessionmaker(bind=_db_engine, class_=Session)

    return _SessionLocal()


# ============================================================================
# Helper Functions
# ============================================================================


def _get_phase2_api_url() -> str:
    """Get Phase-II API base URL from configuration."""
    return settings.phase2_api_url or "http://localhost:8000"


def _generate_service_token(user_id: UUID) -> str:
    """Generate internal service token for server-to-server calls.

    Note: In a real implementation, this would generate a JWT with appropriate
    claims for service-to-service authentication. For now, we use the JWT_SECRET
    directly. In production, consider using a separate service account token.
    """
    import jwt
    from datetime import datetime, timedelta, timezone

    payload = {
        "user_id": str(user_id),
        "email": f"service+{user_id}@internal",  # Service account pseudo-email
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        "type": "service",
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256",
    )
    return token


async def _call_phase2_api(
    method: str,
    endpoint: str,
    user_id: UUID,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0,
) -> tuple[int, Dict[str, Any]]:
    """Call Phase-II API endpoint with proper authentication and error handling.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        endpoint: API endpoint path (e.g., "/api/v1/users/{user_id}/tasks")
        user_id: User ID for the request
        json_data: JSON body for POST/PUT/PATCH requests
        params: Query parameters for GET requests
        timeout: Request timeout in seconds

    Returns:
        Tuple of (status_code, response_json)
    """
    service_token = _generate_service_token(user_id)
    base_url = _get_phase2_api_url()
    url = f"{base_url}{endpoint}"

    headers = {
        "Authorization": f"Bearer {service_token}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params,
            )

            try:
                response_data = response.json()
            except Exception:
                response_data = {"error": f"Failed to parse response: {response.text}"}

            return response.status_code, response_data

    except httpx.TimeoutException:
        logger.error(f"Timeout calling Phase-II API: {method} {endpoint}")
        return 504, {"error": "API request timed out"}
    except httpx.RequestError as e:
        logger.error(f"Request error calling Phase-II API: {e}")
        return 503, {"error": "API service unavailable"}
    except Exception as e:
        logger.error(f"Unexpected error calling Phase-II API: {e}")
        return 500, {"error": "Internal error calling Phase-II API"}


# ============================================================================
# MCP Tool: add_task
# ============================================================================


async def add_task(input_data: AddTaskInput) -> ToolResult:
    """Create a new task via Phase-II API.

    Collects task details (title, description, priority, due_date, tags) and
    creates a new task in the Phase-II system with user_id scoping.

    Args:
        input_data: AddTaskInput with validated parameters

    Returns:
        ToolResult with success status and created task data or error message
    """
    # Validate required fields
    if not input_data.title or len(input_data.title.strip()) == 0:
        return ToolResult(
            success=False,
            error="Title is required and must not be empty",
            message="I need a task title to create the task. What's it called?",
        )

    endpoint = f"/api/{input_data.user_id}/tasks"

    # Build request body with provided fields
    request_body = {
        "title": input_data.title,
    }

    if input_data.description:
        request_body["description"] = input_data.description

    if input_data.priority:
        request_body["priority"] = input_data.priority.value

    if input_data.due_date:
        request_body["due_date"] = input_data.due_date

    if input_data.tags:
        request_body["tags"] = input_data.tags

    # Call Phase-II API
    status_code, response_data = await _call_phase2_api(
        method="POST",
        endpoint=endpoint,
        user_id=input_data.user_id,
        json_data=request_body,
    )

    # Handle responses
    if status_code == 201:
        task_data = response_data.get("data", {})
        return ToolResult(
            success=True,
            data=task_data,
            message=f"Task '{input_data.title}' created successfully!",
        )

    elif status_code == 401:
        logger.warning(f"Unauthorized task creation for user {input_data.user_id}")
        return ToolResult(
            success=False,
            error="Authentication failed",
            message="I'm not authorized to create tasks. Please check your login.",
        )

    elif status_code == 403:
        logger.warning(f"Forbidden task creation for user {input_data.user_id}")
        return ToolResult(
            success=False,
            error="Permission denied",
            message="You don't have permission to create tasks.",
        )

    elif status_code == 422:
        details = response_data.get("error", {}).get("details", {})
        error_msg = "Validation failed: " + ", ".join(details.keys())
        return ToolResult(
            success=False,
            error=error_msg,
            message=f"I couldn't create the task: {error_msg}. Please try again with different values.",
        )

    else:
        error_detail = response_data.get("error", {}).get("message", "Unknown error")
        logger.error(f"Phase-II API error ({status_code}): {error_detail}")
        return ToolResult(
            success=False,
            error=f"API error: {error_detail}",
            message="I encountered an error creating the task. Please try again.",
        )


# ============================================================================
# MCP Tool: list_tasks
# ============================================================================


async def list_tasks(input_data: ListTasksInput) -> ListTasksOutput:
    """List user's tasks with optional filters.

    Fetches tasks directly from database (bypasses HTTP to avoid timeouts).
    Applies optional filters for status (completed/incomplete), priority, and overdue state.

    Args:
        input_data: ListTasksInput with filter options

    Returns:
        ListTasksOutput with task list or error message
    """
    try:
        db = _get_db_session()

        # Build query
        query = select(Task).where(Task.user_id == input_data.user_id)

        # Apply filters
        if input_data.status:
            if input_data.status.value == "completed":
                query = query.where(Task.completed == True)
            elif input_data.status.value == "incomplete":
                query = query.where(Task.completed == False)

        if input_data.priority:
            query = query.where(Task.priority == input_data.priority.value)

        if input_data.overdue:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            query = query.where(
                (Task.due_date < now) &
                (Task.completed == False)
            )

        # Order by creation date descending
        from sqlalchemy import desc
        query = query.order_by(desc(Task.created_at))

        # Get total count
        count_query = select(Task).where(Task.user_id == input_data.user_id)
        if input_data.status:
            if input_data.status.value == "completed":
                count_query = count_query.where(Task.completed == True)
            elif input_data.status.value == "incomplete":
                count_query = count_query.where(Task.completed == False)
        if input_data.priority:
            count_query = count_query.where(Task.priority == input_data.priority.value)

        # Use execute().scalars() for SQLAlchemy Session compatibility
        total_count = len(db.execute(count_query).scalars().all())

        # Apply pagination
        tasks_data = db.execute(query.offset(input_data.offset).limit(input_data.limit)).scalars().all()

        # Convert to TaskOutput
        tasks = []
        for task in tasks_data:
            task_dict = {
                "id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "completed": task.completed,
                "completed_at": task.completed_at,
                "due_date": task.due_date,
                "tags": task.tags,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
            }
            tasks.append(TaskOutput(**task_dict))

        filter_summary = []
        if input_data.status:
            filter_summary.append(f"{input_data.status.value}")
        if input_data.priority:
            filter_summary.append(f"{input_data.priority.value} priority")
        if input_data.overdue:
            filter_summary.append("overdue")

        filter_text = f" ({', '.join(filter_summary)})" if filter_summary else ""

        # Format task list with IDs for display
        task_list_str = ""
        for i, task in enumerate(tasks, 1):
            status = "✓ Complete" if task.completed else "○ Incomplete"
            task_list_str += f"\n{i}. ID: {task.id}\n   Title: {task.title}\n   Priority: {task.priority}\n   Status: {status}"

        message = f"Found {total_count} tasks{filter_text}:{task_list_str}" if tasks else f"Found {total_count} tasks{filter_text}. No tasks to display."

        db.close()

        return ListTasksOutput(
            success=True,
            tasks=tasks,
            total_count=total_count,
            returned_count=len(tasks),
            message=message,
        )

    except Exception as e:
        logger.error(f"Error listing tasks for user {input_data.user_id}: {e}", exc_info=True)
        return ListTasksOutput(
            success=False,
            error="Database error",
            message="I encountered an error listing your tasks. Please try again.",
        )


# ============================================================================
# MCP Tool: update_task
# ============================================================================


async def update_task(input_data: UpdateTaskInput) -> ToolResult:
    """Update specific fields of an existing task.

    Only updates fields that are provided; omitted fields remain unchanged.

    Args:
        input_data: UpdateTaskInput with updated values

    Returns:
        ToolResult with success status and updated task data or error message
    """
    endpoint = f"/api/{input_data.user_id}/tasks/{input_data.task_id}"

    # Build request body with only provided fields
    request_body = {}

    if input_data.title is not None:
        request_body["title"] = input_data.title

    if input_data.description is not None:
        request_body["description"] = input_data.description

    if input_data.priority is not None:
        request_body["priority"] = input_data.priority.value

    if input_data.due_date is not None:
        request_body["due_date"] = input_data.due_date

    if input_data.tags is not None:
        request_body["tags"] = input_data.tags

    # Call Phase-II API
    status_code, response_data = await _call_phase2_api(
        method="PUT",
        endpoint=endpoint,
        user_id=input_data.user_id,
        json_data=request_body,
    )

    # Handle responses
    if status_code == 200:
        task_data = response_data.get("data", {})
        return ToolResult(
            success=True,
            data=task_data,
            message="Task updated successfully!",
        )

    elif status_code == 401:
        logger.warning(f"Unauthorized update for user {input_data.user_id}")
        return ToolResult(
            success=False,
            error="Authentication failed",
            message="I'm not authorized to update tasks. Please check your login.",
        )

    elif status_code == 403:
        logger.warning(f"Forbidden update: User {input_data.user_id} task {input_data.task_id}")
        return ToolResult(
            success=False,
            error="Permission denied",
            message="You don't have permission to update this task.",
        )

    elif status_code == 404:
        logger.warning(f"Task not found: {input_data.task_id} for user {input_data.user_id}")
        return ToolResult(
            success=False,
            error="Task not found",
            message="I couldn't find that task. Did you mean a different one?",
        )

    elif status_code == 422:
        details = response_data.get("error", {}).get("details", {})
        error_msg = "Validation failed: " + ", ".join(details.keys())
        return ToolResult(
            success=False,
            error=error_msg,
            message=f"I couldn't update the task: {error_msg}",
        )

    else:
        error_detail = response_data.get("error", {}).get("message", "Unknown error")
        logger.error(f"Phase-II API error ({status_code}): {error_detail}")
        return ToolResult(
            success=False,
            error=f"API error: {error_detail}",
            message="I encountered an error updating the task. Please try again.",
        )


# ============================================================================
# MCP Tool: complete_task
# ============================================================================


async def complete_task(input_data: CompleteTaskInput) -> ToolResult:
    """Mark a task as completed.

    Sets the task's completed status to true and records completion timestamp.

    Args:
        input_data: CompleteTaskInput with task_id

    Returns:
        ToolResult with success status and updated task data or error message
    """
    endpoint = f"/api/v1/users/{input_data.user_id}/tasks/{input_data.task_id}/complete"

    # Call Phase-II API
    status_code, response_data = await _call_phase2_api(
        method="PATCH",
        endpoint=endpoint,
        user_id=input_data.user_id,
        json_data={"completed": True},
    )

    # Handle responses
    if status_code == 200:
        task_data = response_data.get("data", {})
        return ToolResult(
            success=True,
            data=task_data,
            message="Task marked as complete! Great job! 🎉",
        )

    elif status_code == 401:
        logger.warning(f"Unauthorized completion for user {input_data.user_id}")
        return ToolResult(
            success=False,
            error="Authentication failed",
            message="I'm not authorized to complete tasks. Please check your login.",
        )

    elif status_code == 403:
        logger.warning(f"Forbidden completion: User {input_data.user_id} task {input_data.task_id}")
        return ToolResult(
            success=False,
            error="Permission denied",
            message="You don't have permission to complete this task.",
        )

    elif status_code == 404:
        logger.warning(f"Task not found: {input_data.task_id} for user {input_data.user_id}")
        return ToolResult(
            success=False,
            error="Task not found",
            message="I couldn't find that task to complete.",
        )

    else:
        error_detail = response_data.get("error", {}).get("message", "Unknown error")
        logger.error(f"Phase-II API error ({status_code}): {error_detail}")
        return ToolResult(
            success=False,
            error=f"API error: {error_detail}",
            message="I encountered an error completing the task. Please try again.",
        )


# ============================================================================
# MCP Tool: delete_task
# ============================================================================


async def delete_task(input_data: DeleteTaskInput) -> ToolResult:
    """Delete a task permanently.

    Removes the task from the system. This is a destructive operation
    and requires user confirmation before calling this tool.

    Args:
        input_data: DeleteTaskInput with task_id

    Returns:
        ToolResult with success status or error message
    """
    endpoint = f"/api/{input_data.user_id}/tasks/{input_data.task_id}"

    # Call Phase-II API
    status_code, response_data = await _call_phase2_api(
        method="DELETE",
        endpoint=endpoint,
        user_id=input_data.user_id,
    )

    # Handle responses
    if status_code == 204 or (status_code == 200 and not response_data.get("error")):
        return ToolResult(
            success=True,
            message="Task deleted successfully.",
        )

    elif status_code == 401:
        logger.warning(f"Unauthorized deletion for user {input_data.user_id}")
        return ToolResult(
            success=False,
            error="Authentication failed",
            message="I'm not authorized to delete tasks. Please check your login.",
        )

    elif status_code == 403:
        logger.warning(f"Forbidden deletion: User {input_data.user_id} task {input_data.task_id}")
        return ToolResult(
            success=False,
            error="Permission denied",
            message="You don't have permission to delete this task.",
        )

    elif status_code == 404:
        logger.warning(f"Task not found: {input_data.task_id} for user {input_data.user_id}")
        return ToolResult(
            success=False,
            error="Task not found",
            message="I couldn't find that task to delete.",
        )

    else:
        error_detail = response_data.get("error", {}).get("message", "Unknown error")
        logger.error(f"Phase-II API error ({status_code}): {error_detail}")
        return ToolResult(
            success=False,
            error=f"API error: {error_detail}",
            message="I encountered an error deleting the task. Please try again.",
        )


# ============================================================================
# Tool Registry
# ============================================================================


MCP_TOOLS = {
    "add_task": {
        "name": "add_task",
        "description": "Create a new task with title, optional description, priority, and due date",
        "function": add_task,
        "input_schema": AddTaskInput,
    },
    "list_tasks": {
        "name": "list_tasks",
        "description": "List user's tasks with optional filters (status, priority, overdue)",
        "function": list_tasks,
        "input_schema": ListTasksInput,
    },
    "update_task": {
        "name": "update_task",
        "description": "Update task fields (title, description, priority, due_date)",
        "function": update_task,
        "input_schema": UpdateTaskInput,
    },
    "complete_task": {
        "name": "complete_task",
        "description": "Mark a task as completed",
        "function": complete_task,
        "input_schema": CompleteTaskInput,
    },
    "delete_task": {
        "name": "delete_task",
        "description": "Delete a task permanently (requires user confirmation)",
        "function": delete_task,
        "input_schema": DeleteTaskInput,
    },
}


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Get OpenAI-compatible tool definitions for agent.

    Returns list of tool definitions in OpenAI Agents SDK format.
    """
    tools = []

    for tool_name, tool_info in MCP_TOOLS.items():
        schema = tool_info["input_schema"].model_json_schema()

        tool_def = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_info["description"],
                "parameters": schema,
            },
        }
        tools.append(tool_def)

    return tools
