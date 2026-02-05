# [Task]: T020, T037, T038, [From]: specs/001-task-crud-api/spec.md#Requirements
# [From]: specs/001-task-crud-api/plan.md#Phase-3-User-Story-1
"""
Business logic service for task operations.

Provides:
- create_task: Create a new task with validation and persistence
- list_tasks: List user's tasks with pagination
- get_task: Retrieve specific task by ID
- update_task: Full update (PUT) with all required fields
- partial_update_task: Partial update (PATCH) with optional fields
- Query-level filtering by user_id for data isolation
- Timestamp auto-population
"""

import logging
from datetime import datetime
import datetime as dt_module
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.errors import ForbiddenException, NotFoundException
from ..api.schemas import TaskCreate, TaskPatch, TaskUpdate
from ..models.task import Task

logger = logging.getLogger(__name__)


def to_naive_utc(dt: datetime) -> datetime:
    """Convert timezone-aware datetime to naive UTC datetime."""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        # Convert to UTC and remove timezone info
        return dt.astimezone(dt_module.timezone.utc).replace(tzinfo=None)
    return dt


class TaskService:
    """Service layer for task business logic."""

    def __init__(self, session: AsyncSession):
        """
        Initialize TaskService with database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def create_task(
        self,
        user_id: UUID,
        task_create: TaskCreate,
    ) -> Task:
        """
        Create a new task for the user.

        Args:
            user_id: UUID of the task owner
            task_create: TaskCreate schema with title, priority, description, due_date, tags

        Returns:
            Task: Created task object with id, timestamps, and all fields

        Raises:
            Exception: If database operation fails (handled at endpoint)
        """
        # [Task]: T010, [From]: specs/001-task-crud-api/spec.md#Functional-Requirements
        # Create task instance with user_id and current timestamps
        now = datetime.utcnow()
        task = Task(
            user_id=user_id,
            title=task_create.title,
            description=task_create.description,
            due_date=to_naive_utc(task_create.due_date),
            priority=task_create.priority or 'medium',
            tags=task_create.tags,
            completed=False,
            completed_at=None,
            created_at=now,
            updated_at=now,
        )

        # Persist to database
        self.session.add(task)
        await self.session.flush()  # Ensure ID is generated
        await self.session.commit()  # Commit transaction

        # Refresh to get all generated values
        await self.session.refresh(task)

        logger.info(
            f"Task created: id={task.id}, user_id={user_id}, "
            f"title={task.title!r}",
        )

        return task

    async def list_tasks(
        self,
        user_id: UUID,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[Task], int]:
        """
        List tasks for a user with pagination.

        Args:
            user_id: UUID of the task owner
            limit: Number of items per page (default 10)
            offset: Number of items to skip (default 0)

        Returns:
            Tuple of (List[Task], int): List of Task objects and total count

        Raises:
            Exception: If database operation fails (handled at endpoint)
        """
        # [Task]: T026, [From]: specs/001-task-crud-api/spec.md#Functional-Requirements
        # Query to count total tasks for user
        count_stmt = select(func.count(Task.id)).where(Task.user_id == user_id)
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar() or 0

        # Query tasks ordered by created_at DESC with pagination
        stmt = (
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(desc(Task.created_at))
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        tasks = result.scalars().all()

        logger.info(
            f"Listed tasks: user_id={user_id}, limit={limit}, "
            f"offset={offset}, total={total_count}, returned={len(tasks)}",
        )

        return list(tasks), total_count

    async def get_task(
        self,
        user_id: UUID,
        task_id: UUID,
    ) -> Task:
        """
        Retrieve a specific task by ID for a user.

        Args:
            user_id: UUID of the task owner (authenticated user)
            task_id: UUID of the task to retrieve

        Returns:
            Task: The Task object

        Raises:
            ForbiddenException: If task exists but doesn't belong to user
            NotFoundException: If task doesn't exist
        """
        # [Task]: T032, [From]: specs/001-task-crud-api/spec.md#Functional-Requirements
        # First, check if task exists (regardless of user_id)
        stmt = select(Task).where(Task.id == task_id)
        result = await self.session.execute(stmt)
        task = result.scalars().first()

        # If task doesn't exist, return 404
        if not task:
            logger.warning(
                f"Task not found: task_id={task_id}",
            )
            raise NotFoundException("Task not found")

        # If task exists but doesn't belong to user, return 403
        if task.user_id != user_id:
            logger.warning(
                f"Unauthorized task access: task_id={task_id}, "
                f"task_user_id={task.user_id}, requesting_user_id={user_id}",
            )
            raise ForbiddenException(
                "You do not have permission to access this task"
            )

        logger.info(
            f"Task retrieved: id={task_id}, user_id={user_id}, "
            f"title={task.title!r}",
        )

        return task

    async def update_task(
        self,
        user_id: UUID,
        task_id: UUID,
        task_update: TaskUpdate,
    ) -> Task:
        """
        Full update a task (PUT - all fields required).

        Args:
            user_id: UUID of the task owner (authenticated user)
            task_id: UUID of the task to update
            task_update: TaskUpdate schema with all required fields

        Returns:
            Task: Updated task object

        Raises:
            ForbiddenException: If task doesn't belong to user
            NotFoundException: If task doesn't exist
        """
        # [Task]: T037, [From]: specs/001-task-crud-api/spec.md#Functional-Requirements
        # Query task by both id AND user_id for ownership check
        stmt = select(Task).where(
            (Task.id == task_id) & (Task.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        task = result.scalars().first()

        # If task doesn't exist for this user, check if it exists at all
        if not task:
            # Check if task exists but owned by different user
            stmt_check = select(Task).where(Task.id == task_id)
            result_check = await self.session.execute(stmt_check)
            task_check = result_check.scalars().first()

            if task_check:
                logger.warning(
                    f"Unauthorized task update: task_id={task_id}, "
                    f"task_user_id={task_check.user_id}, requesting_user_id={user_id}",
                )
                raise ForbiddenException(
                    "You do not have permission to update this task"
                )
            else:
                logger.warning(
                    f"Task not found for update: task_id={task_id}",
                )
                raise NotFoundException("Task not found")

        # Update all fields
        task.title = task_update.title
        task.description = task_update.description
        task.due_date = to_naive_utc(task_update.due_date)
        task.priority = task_update.priority or 'medium'
        task.tags = task_update.tags
        task.completed = task_update.completed
        task.updated_at = datetime.utcnow()

        # If marking complete, set completed_at; if marking incomplete, clear it
        if task_update.completed:
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None

        # Persist changes
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        logger.info(
            f"Task updated: id={task_id}, user_id={user_id}, "
            f"title={task.title!r}",
        )

        return task

    async def partial_update_task(
        self,
        user_id: UUID,
        task_id: UUID,
        task_patch: TaskPatch,
    ) -> Task:
        """
        Partial update a task (PATCH - all fields optional).

        Args:
            user_id: UUID of the task owner (authenticated user)
            task_id: UUID of the task to update
            task_patch: TaskPatch schema with optional fields

        Returns:
            Task: Updated task object

        Raises:
            ForbiddenException: If task doesn't belong to user
            NotFoundException: If task doesn't exist
        """
        # [Task]: T038, [From]: specs/001-task-crud-api/spec.md#Functional-Requirements
        # Query task by both id AND user_id for ownership check
        stmt = select(Task).where(
            (Task.id == task_id) & (Task.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        task = result.scalars().first()

        # If task doesn't exist for this user, check if it exists at all
        if not task:
            # Check if task exists but owned by different user
            stmt_check = select(Task).where(Task.id == task_id)
            result_check = await self.session.execute(stmt_check)
            task_check = result_check.scalars().first()

            if task_check:
                logger.warning(
                    f"Unauthorized task update: task_id={task_id}, "
                    f"task_user_id={task_check.user_id}, requesting_user_id={user_id}",
                )
                raise ForbiddenException(
                    "You do not have permission to update this task"
                )
            else:
                logger.warning(
                    f"Task not found for update: task_id={task_id}",
                )
                raise NotFoundException("Task not found")

        # Update only provided fields
        if task_patch.title is not None:
            task.title = task_patch.title

        if task_patch.description is not None:
            task.description = task_patch.description

        if task_patch.due_date is not None:
            task.due_date = to_naive_utc(task_patch.due_date)

        if task_patch.priority is not None:
            task.priority = task_patch.priority

        if task_patch.tags is not None:
            task.tags = task_patch.tags

        if task_patch.completed is not None:
            task.completed = task_patch.completed
            # If marking complete, set completed_at; if marking incomplete, clear it
            if task_patch.completed:
                task.completed_at = datetime.utcnow()
            else:
                task.completed_at = None

        # Always update updated_at
        task.updated_at = datetime.utcnow()

        # Persist changes
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        logger.info(
            f"Task patched: id={task_id}, user_id={user_id}, "
            f"title={task.title!r}",
        )

        return task

    async def mark_complete(
        self,
        user_id: UUID,
        task_id: UUID,
    ) -> Task:
        """
        Toggle task completion status. Sets completed=true and completed_at timestamp
        if currently incomplete, or sets completed=false and clears completed_at if
        currently complete.

        Args:
            user_id: UUID of the task owner (authenticated user)
            task_id: UUID of the task to toggle

        Returns:
            Task: Updated task object with new completion status

        Raises:
            ForbiddenException: If task doesn't belong to user
            NotFoundException: If task doesn't exist
        """
        # [Task]: T044, [From]: specs/001-task-crud-api/spec.md#FR-006
        # Query task by both id AND user_id for ownership check
        stmt = select(Task).where(
            (Task.id == task_id) & (Task.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        task = result.scalars().first()

        # If task doesn't exist for this user, check if it exists at all
        if not task:
            # Check if task exists but owned by different user
            stmt_check = select(Task).where(Task.id == task_id)
            result_check = await self.session.execute(stmt_check)
            task_check = result_check.scalars().first()

            if task_check:
                logger.warning(
                    f"Unauthorized task completion: task_id={task_id}, "
                    f"task_user_id={task_check.user_id}, requesting_user_id={user_id}",
                )
                raise ForbiddenException(
                    "You do not have permission to mark this task complete"
                )
            else:
                logger.warning(
                    f"Task not found for completion: task_id={task_id}",
                )
                raise NotFoundException("Task not found")

        # Toggle completion status
        new_completed_status = not task.completed
        task.completed = new_completed_status

        # Set or clear completed_at based on new status
        if new_completed_status:
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None

        # Always update updated_at
        task.updated_at = datetime.utcnow()

        # Persist changes
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        logger.info(
            f"Task completion toggled: id={task_id}, user_id={user_id}, "
            f"completed={new_completed_status}",
        )

        return task

    async def delete_task(
        self,
        user_id: UUID,
        task_id: UUID,
    ) -> None:
        """
        Delete a task permanently from the database (hard delete).

        Args:
            user_id: UUID of the task owner (authenticated user)
            task_id: UUID of the task to delete

        Returns:
            None

        Raises:
            ForbiddenException: If task exists but doesn't belong to user
            NotFoundException: If task doesn't exist
        """
        # [Task]: T049, [From]: specs/001-task-crud-api/spec.md#User-Story-6-Delete
        # Query task by both id AND user_id for ownership check
        stmt = select(Task).where(
            (Task.id == task_id) & (Task.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        task = result.scalars().first()

        # If task doesn't exist for this user, check if it exists at all
        if not task:
            # Check if task exists but owned by different user
            stmt_check = select(Task).where(Task.id == task_id)
            result_check = await self.session.execute(stmt_check)
            task_check = result_check.scalars().first()

            if task_check:
                logger.warning(
                    f"Unauthorized task deletion: task_id={task_id}, "
                    f"task_user_id={task_check.user_id}, requesting_user_id={user_id}",
                )
                raise ForbiddenException(
                    "You do not have permission to delete this task"
                )
            else:
                logger.warning(
                    f"Task not found for deletion: task_id={task_id}",
                )
                raise NotFoundException("Task not found")

        # Delete the task
        await self.session.delete(task)
        await self.session.commit()

        logger.info(
            f"Task deleted: id={task_id}, user_id={user_id}, "
            f"title={task.title!r}",
        )
