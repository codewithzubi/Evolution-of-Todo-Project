"""Task API routes for CRUD operations."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.api.deps import get_session, get_current_user_id
from app.models.task import Task, TaskCreate, TaskUpdate, TaskResponse
from app.services.task_service import TaskService


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id),
    status: str = Query("all", regex="^(all|pending|completed)$")
) -> List[TaskResponse]:
    """
    List all tasks for authenticated user with optional status filtering.

    Query Parameters:
    - status: Filter by status ('all', 'pending', 'completed') - default: 'all'

    Returns:
        List of tasks for the authenticated user
    """
    tasks = TaskService.get_tasks(session, user_id, status)
    return tasks


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_create: TaskCreate,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
) -> TaskResponse:
    """
    Create a new task for authenticated user.

    Request Body:
    - title: Task title (required, max 200 chars)
    - description: Task description (optional, max 1000 chars)

    Returns:
        Created task with 201 status code
    """
    if not task_create.title or len(task_create.title.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required"
        )

    if len(task_create.title) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must be 200 characters or less"
        )

    if task_create.description and len(task_create.description) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description must be 1000 characters or less"
        )

    task = TaskService.create_task(session, user_id, task_create)
    return task


@router.patch("/{task_id}/toggle", response_model=TaskResponse)
async def toggle_task(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
) -> TaskResponse:
    """
    Toggle task completion status.

    Path Parameters:
    - task_id: Task ID to toggle

    Returns:
        Updated task with toggled completion status

    Raises:
        404: If task not found or does not belong to user
    """
    task = TaskService.toggle_task(session, user_id, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
) -> TaskResponse:
    """
    Update task title and/or description.

    Path Parameters:
    - task_id: Task ID to update

    Request Body:
    - title: New task title (optional, max 200 chars)
    - description: New task description (optional, max 1000 chars)

    Returns:
        Updated task

    Raises:
        400: If validation fails
        404: If task not found or does not belong to user
    """
    if task_update.title is not None:
        if not task_update.title or len(task_update.title.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title is required"
            )

        if len(task_update.title) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title must be 200 characters or less"
            )

    if task_update.description is not None and len(task_update.description) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description must be 1000 characters or less"
        )

    task = TaskService.update_task(session, user_id, task_id, task_update)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
) -> dict:
    """
    Delete a task permanently.

    Path Parameters:
    - task_id: Task ID to delete

    Returns:
        Success message

    Raises:
        404: If task not found or does not belong to user
    """
    deleted = TaskService.delete_task(session, user_id, task_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return {"message": "Task deleted successfully"}
