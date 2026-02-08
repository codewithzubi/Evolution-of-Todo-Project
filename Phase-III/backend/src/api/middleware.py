# [Task]: T012, [From]: specs/001-task-crud-api/spec.md#Authentication
# [From]: specs/001-task-crud-api/plan.md#Phase-2-Foundational
"""
JWT authentication middleware for FastAPI.

Responsibilities:
- Extract JWT token from Authorization header (Bearer <token>)
- Verify JWT signature using JWT_SECRET
- Extract and validate user_id claim
- Set request.state.user_id for downstream handlers
- Return 401 Unauthorized if token missing or invalid
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import Request
from fastapi.responses import JSONResponse
from jose import JWTError, jwt

from ..config import settings
from .errors import UnauthorizedException

logger = logging.getLogger(__name__)


def extract_user_id_from_token(token: str) -> Optional[UUID]:
    """
    Extract and validate user_id from JWT token.

    Args:
        token: JWT token string

    Returns:
        user_id UUID if valid, None if invalid

    Raises:
        UnauthorizedException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = payload.get("user_id")
        if not user_id:
            raise UnauthorizedException("Missing user_id in JWT claims")
        return UUID(user_id)
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise UnauthorizedException(f"Invalid JWT token: {str(e)}")
    except (ValueError, TypeError) as e:
        logger.warning(f"user_id validation error: {e}")
        raise UnauthorizedException(f"Invalid user_id in token: {str(e)}")


async def jwt_middleware(request: Request, call_next):
    """
    FastAPI middleware to verify JWT tokens on all requests.

    Skips verification for:
    - GET /health
    - GET /docs
    - GET /openapi.json
    - OPTIONS /* (CORS preflight requests)
    - POST /api/auth/... (auth endpoints)

    For protected endpoints:
    - Extracts token from Authorization header
    - Verifies signature
    - Sets request.state.user_id
    - Returns 401 if token missing or invalid
    """
    # Skip auth for public endpoints and CORS preflight
    public_paths = {"/health", "/docs", "/openapi.json", "/redoc.html"}
    if request.url.path in public_paths or "/auth/" in request.url.path or request.method == "OPTIONS":
        return await call_next(request)

    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        logger.warning("Missing Authorization header")
        return JSONResponse(
            status_code=401,
            content={
                "data": None,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Missing Authorization header",
                    "details": None,
                },
            },
        )

    # Verify Bearer scheme
    if not auth_header.startswith("Bearer "):
        logger.warning("Invalid Authorization header format")
        return JSONResponse(
            status_code=401,
            content={
                "data": None,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Invalid Authorization header format",
                    "details": None,
                },
            },
        )

    # Extract token
    token = auth_header[7:]  # Remove "Bearer " prefix

    # Verify token and extract user_id
    try:
        user_id = extract_user_id_from_token(token)
        request.state.user_id = user_id
    except UnauthorizedException as e:
        logger.warning(f"Authorization failed: {e.message}")
        return JSONResponse(
            status_code=401,
            content={
                "data": None,
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "details": e.details or None,
                },
            },
        )

    # Continue to next middleware/handler
    return await call_next(request)
