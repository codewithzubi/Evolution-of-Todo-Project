# [Task]: T318, [From]: specs/004-ai-chatbot/spec.md#FR-008
"""Agent Executor for OpenAI Agents SDK.

Orchestrates multi-turn conversation with OpenAI agents, handles tool calling,
and manages agent execution flow with proper error handling.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional
from uuid import UUID

from openai import AsyncOpenAI, APITimeoutError, RateLimitError

from ..config import settings
from ..mcp.server import MCPToolExecutor, get_mcp_tools_for_agent
from .context_manager import ConversationContextManager
from .response_parser import ResponseParser
from .system_prompt import SYSTEM_PROMPT
from .tool_bridge import ToolInvocationBridge

logger = logging.getLogger(__name__)


# ============================================================================
# Tool Validation Rules (Tool Invocation Gate)
# ============================================================================

TOOL_REQUIRED_FIELDS = {
    "add_task": ["title"],
    "update_task": ["task_id"],
    "complete_task": ["task_id"],
    "delete_task": ["task_id"],
    "list_tasks": [],  # No required fields
}

TOOL_CLARIFICATION_PROMPTS = {
    "add_task": "To create a task, I need at least a **title**. What would you like to call this task?",
    "update_task": "To update a task, I need the **task ID** of the task you want to update. Which task would you like to modify?",
    "complete_task": "To mark a task as complete, I need the **task ID**. Which task did you complete?",
    "delete_task": "To delete a task, I need the **task ID**. Which task would you like to delete?",
}


# ============================================================================
# Tool Validation & Clarification Logic
# ============================================================================


def validate_tool_arguments(tool_name: str, tool_params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate tool arguments against required fields.

    TOOL INVOCATION GATE: Prevents execution with empty/invalid arguments.

    Args:
        tool_name: Name of the tool
        tool_params: Tool parameters from OpenAI response

    Returns:
        {
            "valid": bool,
            "missing_fields": List[str] or None,
            "clarification_prompt": str or None
        }
    """
    # Check if tool_params is empty dict
    if not tool_params or tool_params == {}:
        logger.warning(f"Tool '{tool_name}' called with empty parameters: {tool_params}")
        if tool_name in TOOL_CLARIFICATION_PROMPTS:
            return {
                "valid": False,
                "missing_fields": TOOL_REQUIRED_FIELDS.get(tool_name, []),
                "clarification_prompt": TOOL_CLARIFICATION_PROMPTS[tool_name],
            }

    # Check for required fields
    required_fields = TOOL_REQUIRED_FIELDS.get(tool_name, [])
    missing_fields = [field for field in required_fields if not tool_params.get(field)]

    if missing_fields:
        logger.warning(
            f"Tool '{tool_name}' missing required fields: {missing_fields}. "
            f"Params provided: {list(tool_params.keys())}"
        )
        if tool_name in TOOL_CLARIFICATION_PROMPTS:
            return {
                "valid": False,
                "missing_fields": missing_fields,
                "clarification_prompt": TOOL_CLARIFICATION_PROMPTS[tool_name],
            }

    return {
        "valid": True,
        "missing_fields": None,
        "clarification_prompt": None,
    }


# [Task]: T318, [From]: specs/004-ai-chatbot/spec.md#FR-008
class AgentExecutor:
    """Executes OpenAI Agents with MCP tool support.

    Stateless design: all state comes from database, not in-memory.
    Each execution is independent and complete.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_messages: Optional[int] = None,
    ):
        """Initialize agent executor.

        Args:
            api_key: OpenAI API key (defaults to settings.openai_api_key)
            model: Model name (defaults to settings.openai_model)
            timeout: Agent execution timeout in seconds (defaults to settings.agent_timeout)
            max_messages: Maximum messages in context (defaults to settings.agent_max_messages)
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self.timeout = timeout or settings.agent_timeout
        self.max_messages = max_messages or settings.agent_max_messages

        if not self.api_key:
            logger.error("OPENAI_API_KEY not configured")
            raise ValueError("OPENAI_API_KEY environment variable is required")

        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=self.api_key)

        # Message context manager
        self.context_manager = ConversationContextManager(max_messages=self.max_messages)

        # Response parser
        self.response_parser = ResponseParser()

        logger.info(
            f"AgentExecutor initialized: model={self.model}, "
            f"timeout={self.timeout}s, context={self.max_messages} messages"
        )

    async def execute(
        self,
        user_id: UUID,
        user_message: str,
        conversation_history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Execute agent with message and conversation history.

        Orchestrates the full agent execution flow:
        1. Build message array from history
        2. Call OpenAI Agents API
        3. Parse response and tool calls
        4. Execute tools (if any)
        5. Feed results back to agent (agentic loop)
        6. Return final response

        [SAFETY GUARD] Entire pipeline wrapped in try/except.
        - No uncaught exceptions
        - No stack traces to client
        - Always returns HTTP 200-compatible response

        Args:
            user_id: User ID from JWT
            user_message: New message from user
            conversation_history: List of prior messages from database

        Returns:
            Dictionary with:
            - success: bool
            - response: Agent response text
            - tool_calls: List of tools executed
            - error: Error message (if failed)
            - error_code: Error code (if failed)

        Raises:
            ValueError: If inputs invalid
            Timeout: If agent execution exceeds timeout
        """
        start_time = time.time()
        logger.info(f"[AGENT_START] User {user_id}, message: {user_message[:100]}")

        try:
            # Validate inputs
            if not user_message or not user_message.strip():
                raise ValueError("User message cannot be empty")

            if not conversation_history:
                conversation_history = []

            # [Task]: T321, [From]: specs/004-ai-chatbot/spec.md#FR-010
            # Format message history for agent
            messages = self.context_manager.format_messages_for_agent(conversation_history)

            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message,
            })

            logger.debug(
                f"Prepared messages for agent: "
                f"{self.context_manager.get_message_summary(conversation_history)}"
            )

            # Get MCP tools for agent
            # [Task]: T317, [From]: specs/004-ai-chatbot/spec.md#FR-008
            tools = get_mcp_tools_for_agent()

            # Execute agent with timeout
            # [Task]: T320, [From]: specs/004-ai-chatbot/spec.md#CLARIFICATION-001
            response = await asyncio.wait_for(
                self._execute_agent_loop(
                    user_id=user_id,
                    messages=messages,
                    tools=tools,
                ),
                timeout=self.timeout,
            )

            elapsed = time.time() - start_time
            logger.info(f"[AGENT_SUCCESS] User {user_id}, elapsed: {elapsed:.2f}s")

            return {
                "success": True,
                "response": response.get("response_text"),
                "tool_calls": response.get("tool_calls", []),
                "tool_results": response.get("tool_results"),
                "reasoning": response.get("reasoning"),
            }

        except asyncio.TimeoutError as e:
            # Agent execution exceeded timeout
            elapsed = time.time() - start_time
            logger.error(f"[AGENT_TIMEOUT] User {user_id}, elapsed: {elapsed:.2f}s (limit: {self.timeout}s)")
            # Return HTTP 200 with friendly message, never HTTP 500
            return {
                "success": False,
                "response": "I'm taking longer than expected. Please try again in a moment.",
                "error": "agent_timeout",
                "error_code": "AGENT_TIMEOUT",
                "tool_calls": [],
            }

        except APITimeoutError as e:
            elapsed = time.time() - start_time
            logger.error(f"[OPENAI_TIMEOUT] User {user_id}, elapsed: {elapsed:.2f}s: {e}")
            # Return HTTP 200 with friendly message, never HTTP 500
            return {
                "success": False,
                "response": "I'm having trouble connecting to my AI backend. Please try again.",
                "error": "openai_timeout",
                "error_code": "OPENAI_TIMEOUT",
                "tool_calls": [],
            }

        except RateLimitError as e:
            elapsed = time.time() - start_time
            logger.error(f"[RATE_LIMIT] User {user_id}, elapsed: {elapsed:.2f}s")
            # Return HTTP 200 with friendly message, never HTTP 500
            return {
                "success": False,
                "response": "I'm receiving too many requests. Please try again in a few seconds.",
                "error": "rate_limit",
                "error_code": "RATE_LIMIT_ERROR",
                "tool_calls": [],
            }

        except ValueError as e:
            elapsed = time.time() - start_time
            logger.error(f"[VALIDATION_ERROR] User {user_id}, elapsed: {elapsed:.2f}s: {e}")
            # Return HTTP 200 with friendly message, never HTTP 500
            return {
                "success": False,
                "response": "I couldn't understand your request properly. Could you please rephrase?",
                "error": str(e),
                "error_code": "VALIDATION_ERROR",
                "tool_calls": [],
            }

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"[AGENT_ERROR] User {user_id}, elapsed: {elapsed:.2f}s, "
                f"error_type: {type(e).__name__}, error: {str(e)}",
                exc_info=True
            )
            # CRITICAL: Never let exceptions bubble up as HTTP 500
            # Always return HTTP 200 with friendly message
            return {
                "success": False,
                "response": "I'm having trouble completing that right now. Please try again.",
                "error": type(e).__name__,
                "error_code": "INTERNAL_ERROR",
                "tool_calls": [],
            }

    async def _execute_agent_loop(
        self,
        user_id: UUID,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        max_iterations: int = 5,
    ) -> Dict[str, Any]:
        """Execute agent loop with tool calling support.

        Implements multi-turn reasoning:
        1. Send messages to agent
        2. Check if agent wants to call tools
        3. If tools needed, execute and append results
        4. Continue loop until agent outputs final response

        Args:
            user_id: User ID for tool invocations
            messages: Formatted messages for API
            tools: Tool definitions for agent
            max_iterations: Max loop iterations (prevent infinite loops)

        Returns:
            Dictionary with response_text, tool_calls, reasoning

        Raises:
            Exception: If API call fails
        """
        logger.debug(f"Starting agent loop (max {max_iterations} iterations)")

        all_tool_calls = []  # Track tool names for logging
        all_tool_call_objects = []  # Track actual tool call objects for persistence
        all_tool_results = {}  # Track tool results for persistence
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            logger.debug(f"Agent iteration {iteration}/{max_iterations}")

            try:
                # Call OpenAI Agents API
                # [Task]: T318, [From]: specs/004-ai-chatbot/spec.md#FR-008
                # Debug: log messages being sent to OpenAI
                logger.debug(f"Sending {len(messages)} messages to OpenAI:")
                for i, msg in enumerate(messages):
                    msg_summary = {
                        "role": msg.get("role"),
                        "content": (msg.get("content", "")[:50] if msg.get("content") else "")
                    }
                    if msg.get("tool_calls"):
                        tool_calls_list = msg.get("tool_calls", [])
                        msg_summary["tool_calls_count"] = len(tool_calls_list)
                        if tool_calls_list:
                            first_tc = tool_calls_list[0]
                            msg_summary["first_tool_call_type"] = type(first_tc).__name__
                            if isinstance(first_tc, str):
                                msg_summary["ERROR_tool_call_is_string"] = first_tc[:100]
                            logger.error(f"CRITICAL: Message {i} tool_calls[0] is {type(first_tc).__name__}, content: {first_tc}")
                    logger.debug(f"  Message {i}: {msg_summary}")
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",  # Agent decides when to call tools
                    temperature=0.7,
                    max_tokens=2000,
                )

                # Extract assistant's response
                choice = response.choices[0]
                assistant_message = choice.message

                # Parse response
                response_text, tool_calls, reasoning = self.response_parser.parse_agent_response(
                    assistant_message
                )

                logger.debug(
                    f"Agent response: text={bool(response_text)}, "
                    f"tool_calls={len(tool_calls)}, reasoning={bool(reasoning)}"
                )

                # Build assistant message with tool_calls if any
                assistant_msg = {
                    "role": "assistant",
                    "content": response_text or "",
                }

                # Add tool_calls to message if present
                if tool_calls:
                    # Re-construct tool_calls in OpenAI format for the message history
                    formatted_tool_calls = []
                    for call in tool_calls:
                        # Check if already in OpenAI format
                        if isinstance(call, dict) and "type" in call and "function" in call:
                            # Already in correct format, use as-is
                            formatted_tool_calls.append(call)
                        else:
                            # In simplified format from response_parser, reconstruct
                            formatted_tool_calls.append({
                                "id": call.get("id"),
                                "type": "function",
                                "function": {
                                    "name": call.get("name"),
                                    "arguments": json.dumps(call.get("params", {})) if call.get("params") else "{}",
                                }
                            })
                    assistant_msg["tool_calls"] = formatted_tool_calls
                    # Store the full tool_call objects for persistence
                    all_tool_call_objects.extend(formatted_tool_calls)

                messages.append(assistant_msg)

                # If no tool calls, we're done
                if not tool_calls:
                    logger.info(f"Agent finished after {iteration} iteration(s), no tool calls")
                    return {
                        "response_text": response_text or "I'm ready to help!",
                        "tool_calls": all_tool_call_objects,  # Return actual tool_call objects, not names
                        "tool_results": all_tool_results if all_tool_results else None,
                        "reasoning": reasoning,
                    }

                # ====================================================================
                # TOOL INVOCATION GATE: Validate all tool calls BEFORE execution
                # ====================================================================
                logger.debug(f"Validating {len(tool_calls)} tool call(s)")

                invalid_tools = []
                valid_tools = []

                for tool_call in tool_calls:
                    tool_name = tool_call.get("name")
                    tool_params = tool_call.get("params", {})

                    # Validate tool arguments
                    validation = validate_tool_arguments(tool_name, tool_params)

                    if not validation["valid"]:
                        logger.warning(
                            f"[TOOL_VALIDATION_FAILED] Tool '{tool_name}' missing fields: "
                            f"{validation['missing_fields']}"
                        )
                        invalid_tools.append({
                            "tool_call": tool_call,
                            "clarification": validation["clarification_prompt"],
                        })
                    else:
                        valid_tools.append(tool_call)

                # If ANY tools are invalid, ask for clarification in this turn
                # (Conversation-Safe Multi-Turn Logic)
                if invalid_tools and not valid_tools:
                    logger.info(
                        f"[CLARIFICATION_NEEDED] All {len(invalid_tools)} tools require clarification"
                    )
                    # Return clarification request instead of executing
                    clarification_msgs = [tool["clarification"] for tool in invalid_tools]
                    clarification_text = "\n".join(clarification_msgs)

                    return {
                        "response_text": clarification_text,
                        "tool_calls": [],
                        "tool_results": None,
                        "reasoning": "Clarification needed before tool execution",
                    }

                # Execute ONLY valid tools
                logger.debug(f"Executing {len(valid_tools)} valid tool call(s)")

                for tool_call in valid_tools:
                    try:
                        tool_name = tool_call.get("name")
                        logger.debug(f"[TOOL_EXEC_START] {tool_name} with params: {tool_call.get('params')}")

                        tool_result = await ToolInvocationBridge.handle_tool_call_from_agent(
                            tool_call=tool_call,
                            user_id=user_id,
                        )

                        all_tool_calls.append(tool_call.get("name"))
                        logger.debug(f"[TOOL_EXEC_SUCCESS] {tool_name}")

                        # Format tool result as message for agent
                        agent_message = tool_result.get("agent_message", "")

                        # Store tool result for persistence
                        tool_call_id = tool_call.get("id")
                        all_tool_results[tool_call_id] = agent_message

                        # Add tool result with proper tool_call_id reference
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": agent_message,
                        })

                        logger.debug(
                            f"Tool call succeeded: {tool_call.get('name')}, "
                            f"success={tool_result.get('success')}"
                        )

                    except Exception as e:
                        tool_name = tool_call.get("name")
                        tool_id = tool_call.get("id")
                        logger.error(
                            f"[TOOL_EXEC_ERROR] {tool_name} (id: {tool_id}), "
                            f"error: {type(e).__name__}: {str(e)}",
                            exc_info=True
                        )
                        # Store error result for persistence
                        error_message = f"I encountered an error while executing {tool_name}. Please try again."
                        all_tool_results[tool_id] = error_message
                        # Add error result with proper tool_call_id reference
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "content": error_message,
                        })

                # Continue loop to let agent process tool results

            except asyncio.TimeoutError as e:
                logger.error(f"[LOOP_TIMEOUT] Iteration {iteration} exceeded timeout", exc_info=True)
                # Return graceful response instead of raising
                return {
                    "response_text": "I'm taking too long to think. Let me give you what I have so far.",
                    "tool_calls": all_tool_call_objects,
                    "tool_results": all_tool_results if all_tool_results else None,
                    "reasoning": f"Timeout on iteration {iteration}",
                }
            except Exception as e:
                logger.error(
                    f"[LOOP_ERROR] Iteration {iteration}/{max_iterations}, "
                    f"error: {type(e).__name__}: {str(e)}",
                    exc_info=True
                )
                # Return graceful response instead of raising
                return {
                    "response_text": "I encountered an issue processing your request. Please try again.",
                    "tool_calls": all_tool_call_objects,
                    "tool_results": all_tool_results if all_tool_results else None,
                    "reasoning": f"Error on iteration {iteration}: {type(e).__name__}",
                }

        # Max iterations exceeded
        logger.warning(
            f"[LOOP_MAX_ITERATIONS] Agent loop exceeded max iterations ({max_iterations}). "
            f"Tool calls executed: {len(all_tool_calls)}"
        )
        return {
            "response_text": "I'm having trouble completing this task. Please try again.",
            "tool_calls": all_tool_call_objects,  # Return actual tool_call objects, not names
            "tool_results": all_tool_results if all_tool_results else None,
            "reasoning": "Max iterations exceeded",
        }
