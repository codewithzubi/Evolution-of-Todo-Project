# [Task]: T014, [From]: specs/001-task-crud-api/spec.md#Requirements
# [From]: specs/001-task-crud-api/plan.md#Phase-2-Foundational
"""
FastAPI application factory and configuration.

Responsibilities:
- Initialize FastAPI app
- Register middleware (JWT verification)
- Register exception handlers (400, 401, 403, 404, 422, 500)
- Setup database lifecycle (startup, shutdown)
- Include API routers
"""

import logging
import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.errors import APIException
from .api.middleware import jwt_middleware
from .api.schemas import ErrorResponse
from .config import settings
from .database import close_db, init_db

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title="Task CRUD API",
        description="RESTful API for managing user tasks with JWT authentication",
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure based on environment
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # JWT middleware for authentication
    app.middleware("http")(jwt_middleware)

    # Database lifecycle
    @app.on_event("startup")
    async def startup_event():
        """Initialize database on startup."""
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Close database connections on shutdown."""
        logger.info("Closing database connections...")
        await close_db()
        logger.info("Database connections closed")

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint for load balancers."""
        return {"status": "healthy", "service": "task-crud-api"}

    # Exception handlers
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """Handle custom API exceptions."""
        request_id = str(uuid.uuid4())
        logger.warning(
            f"API Exception [{request_id}]: {exc.code} - {exc.message}",
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "data": None,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details or None,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        """Handle Pydantic validation errors."""
        request_id = str(uuid.uuid4())
        logger.warning(
            f"Validation Error [{request_id}]: {exc}",
            extra={"request_id": request_id},
        )

        # Format field-level error details
        details = {}
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"][1:])
            if field not in details:
                details[field] = []
            details[field].append(error["msg"])

        return JSONResponse(
            status_code=422,
            content={
                "data": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": details,
                },
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected errors."""
        request_id = str(uuid.uuid4())
        logger.error(
            f"Unexpected Error [{request_id}]: {exc}",
            exc_info=True,
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=500,
            content={
                "data": None,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {"request_id": request_id},
                },
            },
        )

    # Include authentication routers
    from .api.auth import router as auth_router
    app.include_router(auth_router)

    # [Task]: T021, [From]: specs/001-task-crud-api/spec.md#Requirements
    # Include task routers for CRUD operations
    from .api.tasks import router as tasks_router
    app.include_router(tasks_router)

    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level,
    )
