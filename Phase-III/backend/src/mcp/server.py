"""MCP (Model Context Protocol) Server initialization and tool execution.

Provides interfaces for:
1. Registering MCP tools with OpenAI Agents SDK
2. Executing tool calls with parameter validation
3. Error handling and response formatting
"""

import json
import logging
from typing import Any, Dict, Optional
from uuid import UUID

from .schemas import (
    AddTaskInput,
    CompleteTaskInput,
    DeleteTaskInput,
    ListTasksInput,
    UpdateTaskInput,
)
from .tools import (
    MCP_TOOLS,
    add_task,
    complete_task,
    delete_task,
    list_tasks,
    update_task,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Tool Executor
# ============================================================================


class MCPToolExecutor:
    """Executes MCP tools with parameter validation and error handling."""

    @staticmethod
    def get_tool_definitions() -> list[Dict[str, Any]]:
        """Get OpenAI-compatible tool definitions.

        Returns:
            List of tool definitions in OpenAI format
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task with title, optional description, priority, and due date",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 255,
                                "description": "Task title",
                            },
                            "description": {
                                "type": "string",
                                "maxLength": 2000,
                                "description": "Task description",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "default": "medium",
                                "description": "Priority level",
                            },
                            "due_date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "ISO 8601 due date",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Task tags",
                            },
                        },
                        "required": ["title"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List user's tasks with optional filters (status, priority, overdue)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["completed", "incomplete"],
                                "description": "Filter by status",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Filter by priority",
                            },
                            "overdue": {
                                "type": "boolean",
                                "description": "Show only overdue incomplete tasks",
                            },
                            "limit": {
                                "type": "integer",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 100,
                                "description": "Max results",
                            },
                            "offset": {
                                "type": "integer",
                                "default": 0,
                                "minimum": 0,
                                "description": "Pagination offset",
                            },
                        },
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update task fields (title, description, priority, due_date)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "format": "uuid",
                                "description": "Task ID to update",
                            },
                            "title": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 255,
                                "description": "New title",
                            },
                            "description": {
                                "type": "string",
                                "maxLength": 2000,
                                "description": "New description",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "New priority",
                            },
                            "due_date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "New due date",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "New tags",
                            },
                        },
                        "required": ["task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "format": "uuid",
                                "description": "Task ID to complete",
                            },
                        },
                        "required": ["task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task permanently (requires user confirmation)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "format": "uuid",
                                "description": "Task ID to delete",
                            },
                        },
                        "required": ["task_id"],
                    },
                },
            },
        ]

    @staticmethod
    async def execute_tool(
        tool_name: str,
        tool_input: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a tool with parameter validation.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Tool parameters as dictionary

        Returns:
            Tool result as dictionary

        Raises:
            ValueError: If tool not found or parameters invalid
        """
        logger.info(f"Executing tool: {tool_name} with user_id: {tool_input.get('user_id')}")

        try:
            # Route to correct tool handler
            if tool_name == "add_task":
                input_obj = AddTaskInput(**tool_input)
                result = await add_task(input_obj)
                return result.model_dump()

            elif tool_name == "list_tasks":
                input_obj = ListTasksInput(**tool_input)
                result = await list_tasks(input_obj)
                return result.model_dump()

            elif tool_name == "update_task":
                input_obj = UpdateTaskInput(**tool_input)
                result = await update_task(input_obj)
                return result.model_dump()

            elif tool_name == "complete_task":
                input_obj = CompleteTaskInput(**tool_input)
                result = await complete_task(input_obj)
                return result.model_dump()

            elif tool_name == "delete_task":
                input_obj = DeleteTaskInput(**tool_input)
                result = await delete_task(input_obj)
                return result.model_dump()

            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        except ValueError as e:
            logger.error(f"Validation error in tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"I couldn't understand your request: {str(e)}",
            }

        except Exception as e:
            logger.error(f"Unexpected error executing tool {tool_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": "Internal tool execution error",
                "message": "I encountered an unexpected error. Please try again.",
            }


# ============================================================================
# Tool Schema Factory
# ============================================================================


def get_mcp_tools_for_agent() -> list[Dict[str, Any]]:
    """Get tool definitions for OpenAI Agents SDK.

    These definitions tell the agent what tools are available and their signatures.

    Returns:
        List of tool definition dictionaries in OpenAI format
    """
    return MCPToolExecutor.get_tool_definitions()


# ============================================================================
# Tool Result Formatter
# ============================================================================


def format_tool_result_for_agent(
    tool_name: str,
    tool_result: Dict[str, Any],
) -> str:
    """Format tool result as a message for the agent.

    Converts tool result to a natural language message that the agent
    can read and incorporate into its response.

    Args:
        tool_name: Name of the tool that was executed
        tool_result: Result from the tool execution

    Returns:
        Formatted message string
    """
    success = tool_result.get("success", False)
    error = tool_result.get("error")
    message = tool_result.get("message", "")
    data = tool_result.get("data")

    if not success:
        return f"Error: {error or message or 'Tool execution failed'}"

    if message:
        return message

    # Fallback: describe what happened
    if tool_name == "list_tasks":
        tasks = tool_result.get("tasks", [])
        tasks_count = len(tasks)

        # Format task list with IDs
        if tasks_count > 0:
            task_lines = ["Found {} tasks:".format(tasks_count)]
            for task in tasks:
                task_id = task.get("id", "unknown")[:8]  # First 8 chars of UUID for readability
                task_title = task.get("title", "Untitled")
                status = "✓ Done" if task.get("completed") else "○ Pending"
                priority = task.get("priority", "").capitalize()
                task_lines.append(f"  [{task_id}] {task_title} ({status}) - Priority: {priority}")
            return "\n".join(task_lines)
        return "No tasks found."

    elif tool_name == "add_task":
        task_id = data.get("id", "unknown")[:8] if data else "unknown"
        task_title = data.get("title") if data else None
        if task_title:
            return f"✓ Task created! ID: [{task_id}] '{task_title}'"
        return f"✓ Task created! ID: [{task_id}]"

    elif tool_name == "update_task":
        task_id = data.get("id", "unknown")[:8] if data else "unknown"
        task_title = data.get("title") if data else None
        if task_title:
            return f"✓ Updated! ID: [{task_id}] '{task_title}'"
        return f"✓ Task updated! ID: [{task_id}]"

    elif tool_name == "complete_task":
        task_id = data.get("id", "unknown")[:8] if data else "unknown"
        task_title = data.get("title") if data else None
        if task_title:
            return f"✓ Marked complete! ID: [{task_id}] '{task_title}'"
        return f"✓ Task marked as complete! ID: [{task_id}]"

    elif tool_name == "delete_task":
        return "✓ Task deleted successfully."

    return "Tool executed successfully."
