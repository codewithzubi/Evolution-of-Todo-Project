"""Task service for business logic."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from app.models.task import Task, TaskCreate, TaskUpdate, TaskResponse


class TaskService:
    """Service for task CRUD operations."""

    @staticmethod
    def get_tasks(session: Session, user_id: UUID, status: str = "all") -> List[Task]:
        """
        Get all tasks for a user with optional status filtering.

        Args:
            session: Database session
            user_id: User ID from JWT token
            status: Filter by status ('all', 'pending', 'completed')

        Returns:
            List of Task objects filtered by user and status
        """
        query = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())

        if status == "pending":
            query = query.where(Task.is_completed == False)
        elif status == "completed":
            query = query.where(Task.is_completed == True)

        return session.exec(query).all()

    @staticmethod
    def create_task(session: Session, user_id: UUID, task_create: TaskCreate) -> Task:
        """
        Create a new task for a user.

        Args:
            session: Database session
            user_id: User ID from JWT token
            task_create: Task creation data

        Returns:
            Created Task object
        """
        task = Task(
            user_id=user_id,
            title=task_create.title,
            description=task_create.description,
            due_date=task_create.due_date,
            priority=task_create.priority,
            tags=task_create.tags,
            is_completed=False
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def toggle_task(session: Session, user_id: UUID, task_id: int) -> Optional[Task]:
        """
        Toggle task completion status.

        Args:
            session: Database session
            user_id: User ID from JWT token
            task_id: Task ID to toggle

        Returns:
            Updated Task object or None if not found

        Raises:
            ValueError: If task does not belong to user
        """
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            return None

        task.is_completed = not task.is_completed
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def update_task(session: Session, user_id: UUID, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
        """
        Update task fields.

        Args:
            session: Database session
            user_id: User ID from JWT token
            task_id: Task ID to update
            task_update: Task update data

        Returns:
            Updated Task object or None if not found
        """
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            return None

        if task_update.title is not None:
            task.title = task_update.title
        if task_update.description is not None:
            task.description = task_update.description
        if task_update.due_date is not None:
            task.due_date = task_update.due_date
        if task_update.priority is not None:
            task.priority = task_update.priority
        if task_update.tags is not None:
            task.tags = task_update.tags

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def delete_task(session: Session, user_id: UUID, task_id: int) -> bool:
        """
        Delete a task permanently.

        Args:
            session: Database session
            user_id: User ID from JWT token
            task_id: Task ID to delete

        Returns:
            True if task was deleted, False if not found
        """
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            return False

        session.delete(task)
        session.commit()
        return True
