# [Task]: T336, [From]: specs/004-ai-chatbot/spec.md#Error-Handling
"""Custom exceptions for chat API.

Provides specific exception types for different error scenarios:
- ConversationNotFoundError (404)
- UnauthorizedConversationAccessError (403)
- InvalidMessageError (400)
- OpenAIAPIError (500)
- RateLimitError (429)
"""

from typing import Any, Dict, Optional


class ChatException(Exception):
    """Base exception for chat API errors."""

    def __init__(
        self,
        error_code: str,
        error_message: str,
        status_code: int,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize chat exception.

        Args:
            error_code: Machine-readable error code
            error_message: Human-readable error message
            status_code: HTTP status code
            details: Optional additional error details
        """
        self.error_code = error_code
        self.error_message = error_message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.error_message)


# [Task]: T336
class ConversationNotFoundError(ChatException):
    """Raised when conversation is not found (404)."""

    def __init__(self, conversation_id: str, details: Optional[Dict[str, Any]] = None):
        """Initialize ConversationNotFoundError."""
        super().__init__(
            error_code="CONVERSATION_NOT_FOUND",
            error_message=f"Conversation {conversation_id} not found",
            status_code=404,
            details=details or {"conversation_id": str(conversation_id)},
        )


# [Task]: T336
class UnauthorizedConversationAccessError(ChatException):
    """Raised when user doesn't have access to conversation (403)."""

    def __init__(self, conversation_id: str, details: Optional[Dict[str, Any]] = None):
        """Initialize UnauthorizedConversationAccessError."""
        super().__init__(
            error_code="UNAUTHORIZED_CONVERSATION_ACCESS",
            error_message="You don't have access to this conversation",
            status_code=403,
            details=details or {"conversation_id": str(conversation_id)},
        )


# [Task]: T336
class InvalidMessageError(ChatException):
    """Raised when message is invalid (400)."""

    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        """Initialize InvalidMessageError."""
        super().__init__(
            error_code="INVALID_MESSAGE",
            error_message=f"Invalid message: {reason}",
            status_code=400,
            details=details or {"reason": reason},
        )


# [Task]: T336
class OpenAIAPIError(ChatException):
    """Raised when OpenAI API call fails (500)."""

    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        """Initialize OpenAIAPIError."""
        super().__init__(
            error_code="OPENAI_API_ERROR",
            error_message="AI service temporarily unavailable. Please try again.",
            status_code=500,
            details=details or {"reason": reason},
        )


# [Task]: T336
class RateLimitError(ChatException):
    """Raised when rate limit is exceeded (429)."""

    def __init__(self, retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        """Initialize RateLimitError."""
        super().__init__(
            error_code="RATE_LIMIT_EXCEEDED",
            error_message="Too many requests. Please try again later.",
            status_code=429,
            details=details or {"retry_after": retry_after},
        )


# [Task]: T336
class AgentTimeoutError(ChatException):
    """Raised when agent execution times out (504)."""

    def __init__(self, timeout_seconds: int, details: Optional[Dict[str, Any]] = None):
        """Initialize AgentTimeoutError."""
        super().__init__(
            error_code="AGENT_TIMEOUT",
            error_message="AI is thinking, please wait or refresh the page.",
            status_code=504,
            details=details or {"timeout_seconds": timeout_seconds},
        )


# [Task]: T336
class InvalidConversationAccessError(ChatException):
    """Raised when conversation doesn't belong to user."""

    def __init__(self, details: Optional[Dict[str, Any]] = None):
        """Initialize InvalidConversationAccessError."""
        super().__init__(
            error_code="INVALID_ACCESS",
            error_message="Cannot access this resource",
            status_code=403,
            details=details,
        )
