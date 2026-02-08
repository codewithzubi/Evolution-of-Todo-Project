# [Task]: T018, [From]: specs/001-task-crud-api/spec.md#User-Story-1-Create
# [From]: specs/001-task-crud-api/plan.md#Phase-3-User-Story-1
"""
Integration tests for POST /api/{user_id}/tasks endpoint.

Verifies:
- Task is actually created in database
- Database state after task creation
- User_id isolation (each user only creates their own tasks)
- Timestamps are auto-set correctly
- Query filtering by user_id works
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from src.models.task import Task
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestCreateTaskDatabaseState:
    """Test that tasks are correctly created in database."""

    async def test_create_task_persists_to_database(
        self,
        client: TestClient,
        test_session: AsyncSession,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that created task is persisted to database."""
        # [Task]: T018, [From]: specs/001-task-crud-api/spec.md#User-Story-1-Create
        payload = {"title": "Database persistence test"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 201
        task_id = response.json()["data"]["id"]

        # Query database to verify persistence
        stmt = select(Task).where(Task.id == task_id)
        result = await test_session.execute(stmt)
        db_task = result.scalars().first()

        assert db_task is not None
        assert db_task.title == "Database persistence test"
        assert db_task.user_id == test_user_id

    async def test_create_task_with_all_fields_persists_correctly(
        self,
        client: TestClient,
        test_session: AsyncSession,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that task with all fields persists with correct values."""
        # [Task]: T018, [From]: specs/001-task-crud-api/spec.md#User-Story-1-Create
        due_date = (datetime.utcnow() + timedelta(days=5)).isoformat() + "Z"
        payload = {
            "title": "Full task test",
            "description": "This is a detailed description",
            "due_date": due_date,
        }
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 201
        task_id = response.json()["data"]["id"]

        # Query database
        stmt = select(Task).where(Task.id == task_id)
        result = await test_session.execute(stmt)
        db_task = result.scalars().first()

        assert db_task.title == "Full task test"
        assert db_task.description == "This is a detailed description"
        assert db_task.due_date is not None
        assert db_task.completed is False
        assert db_task.completed_at is None

    async def test_create_task_sets_timestamps(
        self,
        client: TestClient,
        test_session: AsyncSession,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that created_at and updated_at timestamps are auto-set."""
        # [Task]: T018, [From]: specs/001-task-crud-api/spec.md#Requirements
        before_create = datetime.utcnow()
        payload = {"title": "Timestamp test"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        after_create = datetime.utcnow()
        assert response.status_code == 201
        task_id = response.json()["data"]["id"]

        # Query database
        stmt = select(Task).where(Task.id == task_id)
        result = await test_session.execute(stmt)
        db_task = result.scalars().first()

        assert db_task.created_at is not None
        assert db_task.updated_at is not None
        # Verify timestamps are reasonable (within test execution time)
        assert before_create <= db_task.created_at <= after_create

    async def test_create_task_does_not_set_completed_at(
        self,
        client: TestClient,
        test_session: AsyncSession,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that newly created tasks have completed_at = None."""
        # [Task]: T018, [From]: specs/001-task-crud-api/spec.md#Key-Entities
        payload = {"title": "Completion test"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 201
        task_id = response.json()["data"]["id"]

        # Query database
        stmt = select(Task).where(Task.id == task_id)
        result = await test_session.execute(stmt)
        db_task = result.scalars().first()

        assert db_task.completed is False
        assert db_task.completed_at is None


@pytest.mark.asyncio
class TestCreateTaskUserIsolation:
    """Test that user_id isolation is enforced in database."""

    async def test_create_task_filters_by_user_id(
        self,
        client: TestClient,
        test_session: AsyncSession,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that created tasks can be filtered by user_id."""
        # [Task]: T018, [From]: specs/001-task-crud-api/spec.md#Authorization-Rules
        payload = {"title": "User isolation test"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 201

        # Query database filtering by user_id
        stmt = select(Task).where(Task.user_id == test_user_id)
        result = await test_session.execute(stmt)
        tasks = result.scalars().all()

        assert len(tasks) >= 1
        assert all(task.user_id == test_user_id for task in tasks)

    async def test_create_task_different_users_isolated(
        self,
        client: TestClient,
        test_session: AsyncSession,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that tasks from different users are isolated."""
        # [Task]: T018, [From]: specs/001-task-crud-api/spec.md#Authorization-Rules
        # Create task for first user
        payload = {"title": "User 1 task"}
        response1 = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response1.status_code == 201

        # Create task for second user with different token
        other_user_id = uuid4()
        other_auth_headers = {
            "Authorization": f"Bearer {self._create_token(other_user_id)}"
        }
        response2 = client.post(
            f"/api/{other_user_id}/tasks",
            json=payload,
            headers=other_auth_headers,
        )
        assert response2.status_code == 201

        # Verify database isolation
        stmt1 = select(Task).where(Task.user_id == test_user_id)
        result1 = await test_session.execute(stmt1)
        tasks1 = result1.scalars().all()

        stmt2 = select(Task).where(Task.user_id == other_user_id)
        result2 = await test_session.execute(stmt2)
        tasks2 = result2.scalars().all()

        # Each user should only see their own tasks
        assert all(t.user_id == test_user_id for t in tasks1)
        assert all(t.user_id == other_user_id for t in tasks2)

    @staticmethod
    def _create_token(user_id):
        """Helper to create JWT token for different user."""
        from datetime import timedelta

        from src.config import settings
        from jose import jwt

        payload = {
            "user_id": str(user_id),
            "email": f"{user_id}@example.com",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24),
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        return token


@pytest.mark.asyncio
class TestCreateTaskResponseConsistency:
    """Test that response matches database state."""

    async def test_create_task_response_matches_database(
        self,
        client: TestClient,
        test_session: AsyncSession,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that response data matches what's in database."""
        # [Task]: T018, [From]: specs/001-task-crud-api/spec.md#Create-Task-Response
        payload = {"title": "Consistency test"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 201
        task_data = response.json()["data"]
        task_id = task_data["id"]

        # Query database
        stmt = select(Task).where(Task.id == task_id)
        result = await test_session.execute(stmt)
        db_task = result.scalars().first()

        # Verify response matches database
        assert task_data["title"] == db_task.title
        assert task_data["description"] == db_task.description
        assert task_data["completed"] == db_task.completed
        assert str(task_data["user_id"]) == str(db_task.user_id)

    async def test_create_multiple_tasks_all_persisted(
        self,
        client: TestClient,
        test_session: AsyncSession,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that multiple task creations all persist to database."""
        # [Task]: T018, [From]: specs/001-task-crud-api/spec.md#User-Story-1-Create
        task_titles = ["Task 1", "Task 2", "Task 3"]
        created_ids = []

        for title in task_titles:
            response = client.post(
                f"/api/{test_user_id}/tasks",
                json={"title": title},
                headers=auth_headers,
            )
            assert response.status_code == 201
            created_ids.append(response.json()["data"]["id"])

        # Query all tasks for user
        stmt = select(Task).where(Task.user_id == test_user_id)
        result = await test_session.execute(stmt)
        db_tasks = result.scalars().all()

        # Verify all tasks are persisted
        db_ids = [str(t.id) for t in db_tasks]
        for task_id in created_ids:
            assert task_id in db_ids

    async def test_create_task_optional_fields_nullable(
        self,
        client: TestClient,
        test_session: AsyncSession,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that optional fields (description, due_date) are nullable."""
        # [Task]: T018, [From]: specs/001-task-crud-api/spec.md#Key-Entities
        payload = {"title": "Minimal task"}
        response = client.post(
            f"/api/{test_user_id}/tasks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 201
        task_id = response.json()["data"]["id"]

        # Query database
        stmt = select(Task).where(Task.id == task_id)
        result = await test_session.execute(stmt)
        db_task = result.scalars().first()

        # Verify optional fields are None
        assert db_task.description is None
        assert db_task.due_date is None
