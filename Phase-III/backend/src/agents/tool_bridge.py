# [Task]: T319, [From]: specs/004-ai-chatbot/spec.md#FR-008
"""Bridge between OpenAI Agents tool calls and MCP tools.

Receives tool calls from OpenAI, invokes corresponding MCP tools,
and returns formatted results.
"""

import json
import logging
from typing import Any, Dict
from uuid import UUID

from ..mcp.server import MCPToolExecutor
from .response_parser import ResponseParser

logger = logging.getLogger(__name__)


# [Task]: T319, [From]: specs/004-ai-chatbot/spec.md#FR-008
class ToolInvocationBridge:
    """Bridges OpenAI Agents tool calls to MCP tool execution."""

    @staticmethod
    async def invoke_tool(
        tool_name: str,
        tool_params: Dict[str, Any],
        user_id: UUID,
    ) -> Dict[str, Any]:
        """Invoke an MCP tool from an OpenAI Agent tool call.

        Validates parameters, ensures user_id is set correctly,
        invokes MCP tool, and returns formatted result.

        Args:
            tool_name: Name of the tool to invoke
            tool_params: Parameters for the tool
            user_id: User ID from JWT token (for scoping)

        Returns:
            Tool result as dictionary

        Raises:
            ValueError: If tool not found or parameters invalid
        """
        logger.info(f"ToolInvocationBridge: Invoking {tool_name} for user {user_id}")

        try:
            # Ensure user_id is set in parameters
            # [Task]: T323, [From]: specs/004-ai-chatbot/spec.md#FR-017
            if "user_id" in tool_params and str(tool_params["user_id"]) != str(user_id):
                logger.warning(
                    f"Tool call attempted cross-user access: "
                    f"JWT user_id={user_id}, tool user_id={tool_params['user_id']}"
                )
                return {
                    "success": False,
                    "error": "user_id_mismatch",
                    "message": "User ID mismatch - you cannot access another user's resources",
                }

            # Set user_id from JWT (override any provided value)
            tool_params["user_id"] = str(user_id)

            logger.debug(f"Executing MCP tool: {tool_name} with params: {tool_params.keys()}")

            # Invoke MCP tool executor
            result = await MCPToolExecutor.execute_tool(tool_name, tool_params)

            logger.debug(f"MCP tool result for {tool_name}: success={result.get('success')}")

            return result

        except ValueError as e:
            logger.error(f"Validation error invoking tool {tool_name}: {e}")
            return {
                "success": False,
                "error": "tool_validation_error",
                "message": f"I couldn't validate the request: {str(e)}",
            }

        except Exception as e:
            logger.error(f"Unexpected error invoking tool {tool_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": "tool_execution_error",
                "message": "An unexpected error occurred while executing the tool. Please try again.",
            }

    @staticmethod
    def format_tool_result_as_agent_message(
        tool_name: str,
        tool_result: Dict[str, Any],
    ) -> str:
        """Format tool result as a message for the agent to process.

        Converts tool result to natural language that agent can understand
        and incorporate into its next response.

        Args:
            tool_name: Name of the tool that was executed
            tool_result: Result from tool execution

        Returns:
            Formatted message string for agent

        Raises:
            ValueError: If result format is invalid
        """
        if not isinstance(tool_result, dict):
            raise ValueError("tool_result must be a dictionary")

        success = tool_result.get("success", False)
        error = tool_result.get("error", "")
        message = tool_result.get("message", "")
        data = tool_result.get("data")

        # If tool failed, return error message
        if not success:
            error_msg = message or error or "Tool execution failed"
            return f"Tool error: {error_msg}"

        # Format success message
        if message:
            # Use provided message
            return message

        # Fallback: generate message based on tool type
        if tool_name == "list_tasks":
            tasks = tool_result.get("tasks", [])
            total = tool_result.get("total_count", 0)
            return f"Found {total} tasks."

        elif tool_name == "add_task":
            title = data.get("title") if data else None
            if title:
                return f"Created task: {title}"
            return "Task created successfully!"

        elif tool_name == "update_task":
            title = data.get("title") if data else None
            if title:
                return f"Updated task: {title}"
            return "Task updated successfully!"

        elif tool_name == "complete_task":
            title = data.get("title") if data else None
            if title:
                return f"Marked complete: {title}"
            return "Task marked as complete!"

        elif tool_name == "delete_task":
            return "Task deleted successfully."

        # Default fallback
        return "Tool executed successfully."

    @staticmethod
    async def handle_tool_call_from_agent(
        tool_call: Dict[str, Any],
        user_id: UUID,
    ) -> Dict[str, Any]:
        """Handle a complete tool call from agent.

        Extracts parameters, invokes tool, and formats result.

        Args:
            tool_call: Tool call dict from agent ({"name": "...", "params": {...}})
            user_id: User ID from JWT

        Returns:
            Dictionary with:
            - tool_name: Name of tool called
            - success: Whether tool succeeded
            - result: Tool result
            - agent_message: Formatted message for agent to process
        """
        tool_name = tool_call.get("name")
        tool_params = tool_call.get("params", {})

        if not tool_name:
            raise ValueError("Tool call missing 'name' field")

        logger.debug(f"Handling tool call: {tool_name}")

        # Invoke the tool
        result = await ToolInvocationBridge.invoke_tool(
            tool_name=tool_name,
            tool_params=tool_params,
            user_id=user_id,
        )

        # Format result for agent
        agent_message = ToolInvocationBridge.format_tool_result_as_agent_message(tool_name, result)

        return {
            "tool_name": tool_name,
            "success": result.get("success", False),
            "result": result,
            "agent_message": agent_message,
        }
