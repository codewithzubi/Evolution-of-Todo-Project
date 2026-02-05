# [Task]: T015, [From]: specs/001-task-crud-api/spec.md#Error-Handling
# [From]: specs/001-task-crud-api/plan.md#Phase-2-Foundational
"""
Custom exception classes for API error handling.

Each exception maps to a specific HTTP status code:
- UnauthorizedException → 401 Unauthorized
- ForbiddenException → 403 Forbidden
- NotFoundException → 404 Not Found
- ValidationException → 422 Unprocessable Entity
"""

from typing import Any, Dict, Optional


class APIException(Exception):
    """Base exception for all API errors."""

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class UnauthorizedException(APIException):
    """Raised when JWT token is missing, invalid, or expired (401)."""

    def __init__(
        self,
        message: str = "Missing or invalid JWT token",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
            details=details,
        )


class ForbiddenException(APIException):
    """Raised when user lacks permission (403)."""

    def __init__(
        self,
        message: str = "You do not have permission to access this resource",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
            details=details,
        )


class NotFoundException(APIException):
    """Raised when resource is not found (404)."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class ValidationException(APIException):
    """Raised on request validation failure (422)."""

    def __init__(
        self,
        message: str = "Request validation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details or {},
        )


class ConflictException(APIException):
    """Raised on resource conflict (409)."""

    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
            details=details,
        )
