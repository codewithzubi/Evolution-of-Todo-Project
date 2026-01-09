from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from ..models.task import Task, TaskCreate, TaskUpdate, TaskResponse
from ..models.user import User
from ..database.connection import get_session_dep
from ..core.security import get_current_user
import uuid

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session_dep)
):
    """
    Create a new task for the authenticated user.
    """
    db_task = Task(
        title=task.title,
        description=task.description,
        user_id=current_user.id
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session_dep)
):
    """
    Get all tasks for the authenticated user.
    """
    statement = select(Task).where(Task.user_id == current_user.id)
    tasks = session.exec(statement).all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session_dep)
):
    """
    Get a specific task by ID for the authenticated user.
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    task = session.exec(statement).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session_dep)
):
    """
    Update a specific task by ID for the authenticated user.
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    db_task = session.exec(statement).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update task fields
    if task_update.title is not None:
        db_task.title = task_update.title
    if task_update.description is not None:
        db_task.description = task_update.description
    if task_update.status is not None:
        db_task.status = task_update.status

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
async def delete_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session_dep)
):
    """
    Delete a specific task by ID for the authenticated user.
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    db_task = session.exec(statement).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    session.delete(db_task)
    session.commit()
    return {"message": "Task deleted successfully"}

@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: uuid.UUID,
    status_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session_dep)
):
    """
    Update the status of a specific task by ID for the authenticated user.
    """
    if status_update.status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status field is required"
        )

    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    db_task = session.exec(statement).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    db_task.status = status_update.status
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task