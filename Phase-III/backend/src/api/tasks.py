# [Task]: T013-T027, [From]: specs/001-task-crud-api/spec.md#Requirements
# [From]: specs/001-task-crud-api/plan.md#Phase-3-Phase-8
"""
FastAPI router for Task CRUD endpoints.

Implements all 7 endpoints for complete CRUD operations:
- POST /api/{user_id}/tasks: Create a new task (US1)
- GET /api/{user_id}/tasks: List user's tasks with pagination (US2)
- GET /api/{user_id}/tasks/{task_id}: Get specific task details (US3)
- PUT /api/{user_id}/tasks/{task_id}: Full update task (US4)
- PATCH /api/{user_id}/tasks/{task_id}: Partial update task (US4)
- PATCH /api/{user_id}/tasks/{task_id}/complete: Toggle completion (US5)
- DELETE /api/{user_id}/tasks/{task_id}: Delete task (US6)

All endpoints:
- Require valid JWT token in Authorization header
- Verify JWT user_id matches URL user_id (403 Forbidden if mismatch)
- Enforce ownership checks (403 Forbidden if user doesn't own task)
- Return consistent SuccessResponse/ErrorResponse format
- Include proper HTTP status codes and error messages
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..services.task_service import TaskService
from .errors import ForbiddenException
from .schemas import (
    PaginatedResponse,
    PaginationMetadata,
    SuccessResponse,
    TaskComplete,
    TaskCreate,
    TaskPatch,
    TaskResponse,
    TaskUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Tasks"])


def _verify_user_id_match(
    user_id_from_url: UUID,
    user_id_from_jwt: UUID,
) -> None:
    """
    Verify that JWT user_id matches URL user_id.

    Args:
        user_id_from_url: User ID from URL path
        user_id_from_jwt: User ID from JWT token (set by middleware)

    Raises:
        ForbiddenException: If user IDs don't match
    """
    # [Task]: T021, [From]: specs/001-task-crud-api/spec.md#Authorization-Rules
    if user_id_from_url != user_id_from_jwt:
        logger.warning(
            f"User ID mismatch: URL={user_id_from_url}, JWT={user_id_from_jwt}",
        )
        raise ForbiddenException(
            "You do not have permission to access this resource"
        )


@router.post(
    "/{user_id}/tasks",
    status_code=201,
    response_model=SuccessResponse[TaskResponse],
    summary="Create a new task",
    description="Create a new task for the authenticated user with title, "
    "optional description, and optional due date.",
)
async def create_task(
    user_id: UUID,
    task_create: TaskCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> SuccessResponse:
    """
    Create a new task for the authenticated user.

    Path Parameters:
    - user_id: UUID of the user creating the task

    Request Body:
    - title: Task title (required, 1-255 chars)
    - description: Task description (optional, max 2000 chars)
    - due_date: Task due date (optional, ISO 8601 format)

    Returns:
    - 201 Created: Task created successfully
    - 401 Unauthorized: Missing or invalid JWT token
    - 403 Forbidden: user_id in JWT doesn't match URL user_id
    - 422 Unprocessable Entity: Validation error in request body

    Response:
    - data: TaskResponse with all task fields and timestamps
    - error: null on success
    """
    # [Task]: T021, [From]: specs/001-task-crud-api/spec.md#Functional-Requirements
    # Extract authenticated user_id from JWT (set by middleware)
    jwt_user_id: UUID = request.state.user_id

    # Verify user_id in URL matches JWT user_id
    _verify_user_id_match(user_id, jwt_user_id)

    # Create task via service layer
    service = TaskService(session)
    task = await service.create_task(user_id, task_create)

    # Log successful creation
    logger.info(
        f"Task created successfully: id={task.id}, user_id={user_id}, "
        f"title={task.title!r}",
    )

    # Return response
    return SuccessResponse(
        data=TaskResponse.model_validate(task),
        error=None,
    )


@router.get(
    "/{user_id}/tasks",
    status_code=200,
    response_model=SuccessResponse[PaginatedResponse],
    summary="List user's tasks",
    description="List all tasks for the authenticated user with pagination.",
)
async def list_tasks(
    user_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of items per page (1-100)",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of items to skip (offset-based pagination)",
    ),
) -> SuccessResponse:
    """
    List tasks for the authenticated user.

    Path Parameters:
    - user_id: UUID of the user listing tasks

    Query Parameters:
    - limit: Number of items per page (default 10, min 1, max 100)
    - offset: Number of items to skip (default 0, must be >= 0)

    Returns:
    - 200 OK: List of tasks with pagination metadata
    - 401 Unauthorized: Missing or invalid JWT token
    - 403 Forbidden: user_id in JWT doesn't match URL user_id
    - 422 Unprocessable Entity: Invalid limit or offset

    Response:
    - items: Array of TaskResponse objects
    - pagination: PaginationMetadata with limit, offset, total, has_more
    """
    # [Task]: T027, [From]: specs/001-task-crud-api/spec.md#Functional-Requirements
    # Extract authenticated user_id from JWT (set by middleware)
    jwt_user_id: UUID = request.state.user_id

    # Verify user_id in URL matches JWT user_id
    _verify_user_id_match(user_id, jwt_user_id)

    # List tasks via service layer
    service = TaskService(session)
    tasks, total_count = await service.list_tasks(user_id, limit, offset)

    # Calculate has_more flag
    has_more = (offset + limit) < total_count

    # Log successful list
    logger.info(
        f"Tasks listed: user_id={user_id}, limit={limit}, offset={offset}, "
        f"total={total_count}, returned={len(tasks)}",
    )

    # Return response
    return SuccessResponse(
        data=PaginatedResponse(
            items=[TaskResponse.model_validate(task) for task in tasks],
            pagination=PaginationMetadata(
                limit=limit,
                offset=offset,
                total=total_count,
                has_more=has_more,
            ),
        ),
        error=None,
    )


@router.get(
    "/{user_id}/tasks/{task_id}",
    status_code=200,
    response_model=SuccessResponse[TaskResponse],
    summary="Get task details",
    description="Get the complete details of a specific task by ID.",
)
async def get_task(
    user_id: UUID,
    task_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> SuccessResponse:
    """
    Retrieve a specific task by ID.

    Path Parameters:
    - user_id: UUID of the user
    - task_id: UUID of the task to retrieve

    Returns:
    - 200 OK: Task retrieved successfully
    - 401 Unauthorized: Missing or invalid JWT token
    - 403 Forbidden: user_id in JWT doesn't match URL user_id, or task doesn't belong to user
    - 404 Not Found: Task doesn't exist
    - 422 Unprocessable Entity: Invalid task_id format

    Response:
    - data: TaskResponse with all task fields
    - error: null on success
    """
    # [Task]: T033, [From]: specs/001-task-crud-api/spec.md#Functional-Requirements
    # Extract authenticated user_id from JWT (set by middleware)
    jwt_user_id: UUID = request.state.user_id

    # Verify user_id in URL matches JWT user_id
    _verify_user_id_match(user_id, jwt_user_id)

    # Get task via service layer
    service = TaskService(session)
    task = await service.get_task(user_id, task_id)

    # Log successful retrieval
    logger.info(
        f"Task retrieved successfully: id={task_id}, user_id={user_id}, "
        f"title={task.title!r}",
    )

    # Return response
    return SuccessResponse(
        data=TaskResponse.model_validate(task),
        error=None,
    )


@router.put(
    "/{user_id}/tasks/{task_id}",
    status_code=200,
    response_model=SuccessResponse[TaskResponse],
    summary="Update a task (full)",
    description="Fully update a task with all required fields (title, description, "
    "due_date, completed).",
)
async def update_task(
    user_id: UUID,
    task_id: UUID,
    task_update: TaskUpdate,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> SuccessResponse:
    """
    Fully update a task (PUT - all fields required).

    Path Parameters:
    - user_id: UUID of the user
    - task_id: UUID of the task to update

    Request Body (all fields required):
    - title: Task title (required, 1-255 chars)
    - description: Task description (optional for PUT body, but field accepted)
    - due_date: Task due date (optional for PUT body, but field accepted)
    - completed: Task completion status (boolean)

    Returns:
    - 200 OK: Task updated successfully
    - 401 Unauthorized: Missing or invalid JWT token
    - 403 Forbidden: user_id in JWT doesn't match URL user_id, or task doesn't belong to user
    - 404 Not Found: Task doesn't exist
    - 422 Unprocessable Entity: Validation error in request body

    Response:
    - data: TaskResponse with all task fields including updated timestamps
    - error: null on success
    """
    # [Task]: T039, [From]: specs/001-task-crud-api/spec.md#Functional-Requirements
    # Extract authenticated user_id from JWT (set by middleware)
    jwt_user_id: UUID = request.state.user_id

    # Verify user_id in URL matches JWT user_id
    _verify_user_id_match(user_id, jwt_user_id)

    # Update task via service layer
    service = TaskService(session)
    task = await service.update_task(user_id, task_id, task_update)

    # Log successful update
    logger.info(
        f"Task updated successfully: id={task_id}, user_id={user_id}, "
        f"title={task.title!r}",
    )

    # Return response
    return SuccessResponse(
        data=TaskResponse.model_validate(task),
        error=None,
    )


@router.patch(
    "/{user_id}/tasks/{task_id}",
    status_code=200,
    response_model=SuccessResponse[TaskResponse],
    summary="Partial update a task",
    description="Partially update a task with optional fields (title, description, "
    "due_date, completed).",
)
async def partial_update_task(
    user_id: UUID,
    task_id: UUID,
    task_patch: TaskPatch,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> SuccessResponse:
    """
    Partially update a task (PATCH - all fields optional).

    Path Parameters:
    - user_id: UUID of the user
    - task_id: UUID of the task to update

    Request Body (all fields optional):
    - title: Task title (optional, 1-255 chars if provided)
    - description: Task description (optional, max 2000 chars if provided)
    - due_date: Task due date (optional, ISO 8601 format if provided)
    - completed: Task completion status (optional, boolean if provided)

    Returns:
    - 200 OK: Task updated successfully (even if no fields were updated)
    - 401 Unauthorized: Missing or invalid JWT token
    - 403 Forbidden: user_id in JWT doesn't match URL user_id, or task doesn't belong to user
    - 404 Not Found: Task doesn't exist
    - 422 Unprocessable Entity: Validation error in request body

    Response:
    - data: TaskResponse with all task fields including updated timestamps
    - error: null on success
    """
    # [Task]: T040, [From]: specs/001-task-crud-api/spec.md#Functional-Requirements
    # Extract authenticated user_id from JWT (set by middleware)
    jwt_user_id: UUID = request.state.user_id

    # Verify user_id in URL matches JWT user_id
    _verify_user_id_match(user_id, jwt_user_id)

    # Partial update task via service layer
    service = TaskService(session)
    task = await service.partial_update_task(user_id, task_id, task_patch)

    # Log successful update
    logger.info(
        f"Task partially updated: id={task_id}, user_id={user_id}, "
        f"title={task.title!r}",
    )

    # Return response
    return SuccessResponse(
        data=TaskResponse.model_validate(task),
        error=None,
    )


@router.patch(
    "/{user_id}/tasks/{task_id}/complete",
    status_code=200,
    response_model=SuccessResponse[TaskResponse],
    summary="Toggle task completion status",
    description="Toggle a task's completion status. Marks complete if not complete, "
    "marks incomplete if complete. Sets completed_at timestamp when marking complete, "
    "clears it when marking incomplete.",
)
async def mark_task_complete(
    user_id: UUID,
    task_id: UUID,
    task_complete: TaskComplete,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> SuccessResponse:
    """
    Toggle task completion status.

    Path Parameters:
    - user_id: UUID of the user
    - task_id: UUID of the task to toggle

    Request Body:
    - completed: Boolean to set completion status (required)

    Returns:
    - 200 OK: Task completion toggled successfully
    - 401 Unauthorized: Missing or invalid JWT token
    - 403 Forbidden: user_id in JWT doesn't match URL user_id, or task doesn't belong to user
    - 404 Not Found: Task doesn't exist
    - 422 Unprocessable Entity: Validation error in request body

    Response:
    - data: TaskResponse with updated completed status and completed_at timestamp
    - error: null on success
    """
    # [Task]: T045, [From]: specs/001-task-crud-api/spec.md#FR-006
    # Extract authenticated user_id from JWT (set by middleware)
    jwt_user_id: UUID = request.state.user_id

    # Verify user_id in URL matches JWT user_id
    _verify_user_id_match(user_id, jwt_user_id)

    # Mark complete via service layer
    service = TaskService(session)
    task = await service.mark_complete(user_id, task_id)

    # Log successful completion toggle
    logger.info(
        f"Task completion toggled: id={task_id}, user_id={user_id}, "
        f"completed={task.completed}",
    )

    # Return response
    return SuccessResponse(
        data=TaskResponse.model_validate(task),
        error=None,
    )


@router.delete(
    "/{user_id}/tasks/{task_id}",
    status_code=204,
    summary="Delete a task",
    description="Permanently delete a task by ID. This is a hard delete and cannot be undone.",
)
async def delete_task(
    user_id: UUID,
    task_id: UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> None:
    """
    Delete a task permanently.

    Path Parameters:
    - user_id: UUID of the user
    - task_id: UUID of the task to delete

    Returns:
    - 204 No Content: Task deleted successfully (no response body)
    - 401 Unauthorized: Missing or invalid JWT token
    - 403 Forbidden: user_id in JWT doesn't match URL user_id, or task doesn't belong to user
    - 404 Not Found: Task doesn't exist
    - 422 Unprocessable Entity: Invalid task_id format

    Response:
    - No content (empty response body)
    """
    # [Task]: T050, [From]: specs/001-task-crud-api/spec.md#User-Story-6-Delete
    # Extract authenticated user_id from JWT (set by middleware)
    jwt_user_id: UUID = request.state.user_id

    # Verify user_id in URL matches JWT user_id
    _verify_user_id_match(user_id, jwt_user_id)

    # Delete task via service layer
    service = TaskService(session)
    await service.delete_task(user_id, task_id)

    # Log successful deletion
    logger.info(
        f"Task deleted successfully: id={task_id}, user_id={user_id}",
    )

    # Return 204 No Content with no response body
    return None
