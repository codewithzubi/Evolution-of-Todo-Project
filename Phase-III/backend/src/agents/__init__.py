# [Task]: T318, [From]: specs/004-ai-chatbot/spec.md#FR-008
"""OpenAI Agents SDK integration for Phase-III AI Chatbot.

Provides agent executor, tool binding, response parsing, and system prompts
for multi-turn conversational task management.
"""

from .executor import AgentExecutor
from .response_parser import ResponseParser
from .system_prompt import SYSTEM_PROMPT

__all__ = [
    "AgentExecutor",
    "ResponseParser",
    "SYSTEM_PROMPT",
]
