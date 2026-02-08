# [Task]: T321, [From]: specs/004-ai-chatbot/spec.md#FR-010
"""Manages conversation context for OpenAI Agents SDK.

Handles message history truncation to respect token limits and formats
messages for OpenAI API consumption.
"""

import json
import logging
from typing import Any, Dict, List
from uuid import UUID

logger = logging.getLogger(__name__)


# [Task]: T321, [From]: specs/004-ai-chatbot/plan.md#Decision-4-Token-Window
class ConversationContextManager:
    """Manages conversation context and message history truncation."""

    def __init__(self, max_messages: int = 20):
        """Initialize context manager.

        Args:
            max_messages: Maximum number of messages to include in agent context
                         (per ADR-005: 20 messages ≈ 2-3K tokens)
        """
        self.max_messages = max_messages
        logger.debug(f"ConversationContextManager initialized with max_messages={max_messages}")

    def format_messages_for_agent(
        self,
        messages: List[Dict[str, Any]],
        include_system_prompt: bool = False,
    ) -> List[Dict[str, Any]]:
        """Format message history for OpenAI Agents API.

        Truncates to last N messages to stay within token limits.
        Converts database message format to OpenAI API format.
        Properly includes tool_calls for assistant messages.

        Args:
            messages: List of message dictionaries from database
                     Expected format: {"role": "user|assistant|tool", "content": "...", "tool_calls": {...}, "created_at": "..."}
            include_system_prompt: If True, return format with system message slot

        Returns:
            List of messages in OpenAI format: [{"role": "...", "content": "...", "tool_calls": [...]}]

        Raises:
            ValueError: If messages list is invalid
        """
        if not isinstance(messages, list):
            raise ValueError("messages must be a list")

        # Truncate to last N messages
        # [Task]: T321, [From]: specs/004-ai-chatbot/plan.md#Decision-4-Token-Window
        truncated_messages = messages[-self.max_messages :] if len(messages) > self.max_messages else messages

        if len(messages) > self.max_messages:
            logger.info(
                f"Truncated conversation from {len(messages)} to {len(truncated_messages)} messages "
                f"(token limit: {self.max_messages} message window)"
            )

        # Format for OpenAI API
        formatted = []
        for msg in truncated_messages:
            try:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                formatted_msg = {
                    "role": role,
                    "content": content or "",
                }

                # Include tool_calls if present and message is from assistant
                if role == "assistant" and msg.get("tool_calls"):
                    tool_calls = msg.get("tool_calls")
                    # Parse JSON string if needed (stored as string in DB)
                    if isinstance(tool_calls, str):
                        try:
                            tool_calls = json.loads(tool_calls)
                        except:
                            tool_calls = None
                    if tool_calls:
                        formatted_msg["tool_calls"] = tool_calls

                # Include tool_call_id for tool messages
                if role == "tool" and msg.get("tool_call_id"):
                    formatted_msg["tool_call_id"] = msg.get("tool_call_id")

                formatted.append(formatted_msg)

            except Exception as e:
                logger.error(f"Error formatting message: {e}, skipping", exc_info=True)
                continue

        logger.debug(f"Formatted {len(formatted)} messages for agent (from {len(messages)} total)")

        return formatted

    def get_message_summary(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary of message history for logging/debugging.

        Args:
            messages: List of messages

        Returns:
            Dictionary with message counts and token estimate
        """
        total_messages = len(messages)
        within_window = len(messages[-self.max_messages :]) if len(messages) > 0 else 0
        truncated = total_messages > self.max_messages

        # Rough token estimate: ~40 tokens per message + content length
        approx_tokens = sum(
            len(msg.get("content", "")) // 4 + 40
            for msg in messages[-self.max_messages :]
        )

        return {
            "total_messages": total_messages,
            "context_window_messages": within_window,
            "was_truncated": truncated,
            "approximate_tokens": approx_tokens,
            "message_roles": {
                "user": sum(1 for m in messages if m.get("role") == "user"),
                "assistant": sum(1 for m in messages if m.get("role") == "assistant"),
                "system": sum(1 for m in messages if m.get("role") == "system"),
            },
        }


def create_system_message(content: str) -> Dict[str, str]:
    """Create a system message for the agent.

    Args:
        content: System message content

    Returns:
        Message dictionary in OpenAI format
    """
    return {
        "role": "system",
        "content": content,
    }


def create_user_message(content: str) -> Dict[str, str]:
    """Create a user message for the agent.

    Args:
        content: User message content

    Returns:
        Message dictionary in OpenAI format
    """
    return {
        "role": "user",
        "content": content,
    }


def create_assistant_message(content: str) -> Dict[str, str]:
    """Create an assistant message for the agent.

    Args:
        content: Assistant message content

    Returns:
        Message dictionary in OpenAI format
    """
    return {
        "role": "assistant",
        "content": content,
    }
