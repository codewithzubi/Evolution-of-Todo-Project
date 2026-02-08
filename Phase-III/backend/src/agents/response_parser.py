# [Task]: T324, [From]: specs/004-ai-chatbot/spec.md#FR-008
"""Parses OpenAI Agents SDK responses.

Extracts response text, tool calls, and reasoning from agent output.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# [Task]: T324, [From]: specs/004-ai-chatbot/spec.md#FR-008
class ResponseParser:
    """Parses OpenAI Agents SDK responses."""

    @staticmethod
    def parse_agent_response(
        agent_response: Any,
    ) -> Tuple[Optional[str], List[Dict[str, Any]], Optional[str]]:
        """Parse agent response into response_text, tool_calls, and reasoning.

        Handles both direct responses (no tools needed) and tool-calling responses.

        Args:
            agent_response: Response from OpenAI Agents SDK

        Returns:
            Tuple of (response_text, tool_calls, reasoning)
            - response_text: Text response for user (str or None)
            - tool_calls: List of tool call dicts with name and params (list[Dict])
            - reasoning: Agent's reasoning trace (str or None)

        Raises:
            ValueError: If response format is invalid
        """
        if not agent_response:
            logger.error("Received empty agent response")
            raise ValueError("Agent returned empty response")

        response_text = None
        tool_calls = []
        reasoning = None

        try:
            # Handle OpenAI client response object
            # The response structure depends on OpenAI SDK version
            # Newer versions have message with content and tool_calls attributes

            # Try to extract text content
            if hasattr(agent_response, "content"):
                # Message object with content attribute
                response_text = agent_response.content
            elif isinstance(agent_response, dict):
                # Dictionary response
                response_text = agent_response.get("content") or agent_response.get("text")
            elif isinstance(agent_response, str):
                # Direct string response
                response_text = agent_response

            # Try to extract tool calls
            if hasattr(agent_response, "tool_calls"):
                # OpenAI message object with tool_calls
                tool_calls = ResponseParser._parse_tool_calls(agent_response.tool_calls)
            elif isinstance(agent_response, dict) and "tool_calls" in agent_response:
                # Dictionary with tool_calls
                tool_calls = ResponseParser._parse_tool_calls(agent_response["tool_calls"])

            # Try to extract reasoning (optional field, may not be present)
            if hasattr(agent_response, "reasoning"):
                reasoning = agent_response.reasoning
            elif isinstance(agent_response, dict) and "reasoning" in agent_response:
                reasoning = agent_response["reasoning"]

            logger.debug(
                f"Parsed agent response: text={bool(response_text)}, "
                f"tool_calls={len(tool_calls)}, reasoning={bool(reasoning)}"
            )

            return response_text, tool_calls, reasoning

        except Exception as e:
            logger.error(f"Error parsing agent response: {e}", exc_info=True)
            raise ValueError(f"Failed to parse agent response: {str(e)}")

    @staticmethod
    def _parse_tool_calls(tool_calls: Any) -> List[Dict[str, Any]]:
        """Parse tool calls from OpenAI response.

        Converts OpenAI tool call objects to dictionaries.

        Args:
            tool_calls: Tool calls from agent response (list or generator)

        Returns:
            List of tool call dictionaries: [{"id": "...", "name": "...", "params": {...}}]
        """
        if not tool_calls:
            return []

        parsed_calls = []

        try:
            for call in tool_calls:
                try:
                    # Handle OpenAI ToolCall object
                    if hasattr(call, "function"):
                        # Standard OpenAI format
                        func = call.function
                        tool_id = call.id if hasattr(call, "id") else None
                        tool_name = func.name if hasattr(func, "name") else None
                        tool_args = func.arguments if hasattr(func, "arguments") else None

                        if isinstance(tool_args, str):
                            # Parse JSON arguments
                            try:
                                tool_args = json.loads(tool_args)
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse tool arguments JSON: {e}")
                                tool_args = {}

                    elif isinstance(call, dict):
                        # Dictionary format
                        tool_id = call.get("id")
                        tool_name = call.get("function", {}).get("name")
                        tool_args_str = call.get("function", {}).get("arguments")

                        if isinstance(tool_args_str, str):
                            try:
                                tool_args = json.loads(tool_args_str)
                            except json.JSONDecodeError:
                                tool_args = {}
                        else:
                            tool_args = tool_args_str or {}
                    else:
                        logger.warning(f"Unknown tool call format: {type(call)}")
                        continue

                    if not tool_name:
                        logger.warning("Tool call missing name")
                        continue

                    parsed_calls.append({
                        "id": tool_id,
                        "name": tool_name,
                        "params": tool_args or {},
                    })

                except Exception as e:
                    logger.error(f"Error parsing individual tool call: {e}", exc_info=True)
                    continue

        except Exception as e:
            logger.error(f"Error iterating tool calls: {e}", exc_info=True)
            return []

        logger.debug(f"Parsed {len(parsed_calls)} tool calls")
        return parsed_calls

    @staticmethod
    def format_response_for_frontend(
        response_text: Optional[str],
        tool_calls: List[Dict[str, Any]],
        reasoning: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Format agent response for frontend consumption.

        Args:
            response_text: Text response from agent
            tool_calls: List of tool calls executed
            reasoning: Optional reasoning trace

        Returns:
            Formatted response dict: {"message": "...", "tools_executed": [...], "reasoning": "..."}
        """
        return {
            "message": response_text or "I'm processing your request...",
            "tools_executed": [call.get("name") for call in tool_calls],
            "reasoning": reasoning,
            "tool_count": len(tool_calls),
        }

    @staticmethod
    def format_error_response(
        error_code: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Format error response for frontend.

        Args:
            error_code: Error code (e.g., "agent_timeout", "validation_error")
            error_message: Human-readable error message
            details: Optional additional error details

        Returns:
            Formatted error response
        """
        return {
            "message": error_message,
            "error_code": error_code,
            "tools_executed": [],
            "error": True,
            "details": details or {},
        }
