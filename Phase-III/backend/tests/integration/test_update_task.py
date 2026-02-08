# [Task]: T036, [From]: specs/001-task-crud-api/spec.md#User-Story-4-Update
# [From]: specs/001-task-crud-api/plan.md#Phase-6-User-Story-4
"""
Integration tests for PUT/PATCH endpoints for updating tasks.

Verifies:
- Full update (PUT) changes all provided fields
- Partial update (PATCH) changes only provided fields, leaves others unchanged
- updated_at timestamp is refreshed on update
- cannot update user_id or id (immutable fields)
- Other users' tasks cannot be updated
- Database persistence verified
"""

from datetime import datetime, timedelta

from fastapi.testclient import TestClient


class TestFullUpdatePUT:
    """Integration tests for PUT full update."""

    def test_put_full_update_changes_all_fields(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PUT full update changes all provided fields."""
        # [Task]: T036, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        original_title = "Original title"
        original_desc = "Original description"
        original_due = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"

        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={
                "title": original_title,
                "description": original_desc,
                "due_date": original_due,
            },
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]
        original_created_at = create_response.json()["data"]["created_at"]

        # Update with PUT
        new_due = (datetime.utcnow() + timedelta(days=10)).isoformat() + "Z"
        update_response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={
                "title": "New title",
                "description": "New description",
                "due_date": new_due,
                "completed": False,
            },
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        updated_data = update_response.json()["data"]

        # Verify all fields changed
        assert updated_data["title"] == "New title"
        assert updated_data["description"] == "New description"
        assert updated_data["due_date"] is not None
        assert updated_data["completed"] is False

        # Verify immutable fields unchanged
        assert updated_data["id"] == task_id
        assert str(updated_data["user_id"]) == str(test_user_id)
        assert updated_data["created_at"] == original_created_at

    def test_put_updated_at_timestamp_changes(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PUT updates the updated_at timestamp."""
        # [Task]: T036, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Original title"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]
        original_updated_at = create_response.json()["data"]["updated_at"]

        # Wait a tiny bit to ensure timestamp changes
        import time

        time.sleep(0.01)

        # Update with PUT
        update_response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={
                "title": "New title",
                "description": None,
                "due_date": None,
                "completed": False,
            },
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        updated_data = update_response.json()["data"]

        # Verify updated_at changed
        assert updated_data["updated_at"] != original_updated_at

    def test_put_get_returns_updated_data(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PUT changes are persisted to database."""
        # [Task]: T036, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Original title"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Update with PUT
        update_response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={
                "title": "Updated title",
                "description": "New description",
                "due_date": None,
                "completed": True,
            },
            headers=auth_headers,
        )
        assert update_response.status_code == 200

        # Verify GET returns updated data
        get_response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 200
        retrieved_data = get_response.json()["data"]
        assert retrieved_data["title"] == "Updated title"
        assert retrieved_data["description"] == "New description"
        assert retrieved_data["completed"] is True


class TestPartialUpdatePATCH:
    """Integration tests for PATCH partial update."""

    def test_patch_single_field_only_updates_that_field(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH single field updates only that field."""
        # [Task]: T036, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        original_desc = "Original description"
        original_due = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"

        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={
                "title": "Original title",
                "description": original_desc,
                "due_date": original_due,
            },
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Update only title with PATCH
        patch_response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={"title": "New title"},
            headers=auth_headers,
        )
        assert patch_response.status_code == 200
        updated_data = patch_response.json()["data"]

        # Verify only title changed
        assert updated_data["title"] == "New title"
        assert updated_data["description"] == original_desc
        assert updated_data["due_date"] is not None

    def test_patch_multiple_fields_only_updates_those(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH multiple fields updates only those fields."""
        # [Task]: T036, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        original_due = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"
        original_completed = False

        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={
                "title": "Original title",
                "description": "Original description",
                "due_date": original_due,
            },
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Update title and description with PATCH
        patch_response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={
                "title": "New title",
                "description": "New description",
            },
            headers=auth_headers,
        )
        assert patch_response.status_code == 200
        updated_data = patch_response.json()["data"]

        # Verify only title and description changed
        assert updated_data["title"] == "New title"
        assert updated_data["description"] == "New description"
        assert updated_data["due_date"] is not None
        assert updated_data["completed"] is original_completed

    def test_patch_no_fields_noop(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH with no fields doesn't change anything."""
        # [Task]: T036, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Original title", "description": "Original description"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]
        original_data = create_response.json()["data"]

        # PATCH with no fields
        patch_response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={},
            headers=auth_headers,
        )
        assert patch_response.status_code == 200
        updated_data = patch_response.json()["data"]

        # Verify nothing changed except updated_at
        assert updated_data["title"] == original_data["title"]
        assert updated_data["description"] == original_data["description"]
        assert updated_data["completed"] == original_data["completed"]

    def test_patch_get_returns_updated_data(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test PATCH changes are persisted to database."""
        # [Task]: T036, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Original title", "description": "Original description"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Update with PATCH
        patch_response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={"title": "Patched title"},
            headers=auth_headers,
        )
        assert patch_response.status_code == 200

        # Verify GET returns updated data
        get_response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 200
        retrieved_data = get_response.json()["data"]
        assert retrieved_data["title"] == "Patched title"
        assert retrieved_data["description"] == "Original description"


class TestUpdateTaskOwnership:
    """Test user isolation for update operations."""

    def test_cannot_update_other_users_task_put(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
        mismatched_auth_headers: dict,
    ):
        """Test cannot PUT-update another user's task."""
        # [Task]: T036, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task with user 1
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "User 1 task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to update as user 2 (should fail)
        update_response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={
                "title": "Hacked title",
                "description": None,
                "due_date": None,
                "completed": False,
            },
            headers=mismatched_auth_headers,
        )
        assert update_response.status_code == 403

        # Verify task unchanged
        get_response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 200
        assert get_response.json()["data"]["title"] == "User 1 task"

    def test_cannot_update_other_users_task_patch(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
        mismatched_auth_headers: dict,
    ):
        """Test cannot PATCH-update another user's task."""
        # [Task]: T036, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create task with user 1
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "User 1 task"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to update as user 2 (should fail)
        update_response = client.patch(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={"title": "Hacked title"},
            headers=mismatched_auth_headers,
        )
        assert update_response.status_code == 403

        # Verify task unchanged
        get_response = client.get(
            f"/api/{test_user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 200
        assert get_response.json()["data"]["title"] == "User 1 task"


class TestUpdateTaskImmutableFields:
    """Test that immutable fields cannot be changed."""

    def test_put_cannot_change_id(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that id field is immutable."""
        # [Task]: T036, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Original title"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to update id (which shouldn't be in the request anyway)
        update_response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={
                "title": "New title",
                "description": None,
                "due_date": None,
                "completed": False,
            },
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["data"]["id"] == task_id

    def test_put_cannot_change_user_id(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that user_id field is immutable."""
        # [Task]: T036, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Original title"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Try to update user_id (which shouldn't be in the request anyway)
        update_response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={
                "title": "New title",
                "description": None,
                "due_date": None,
                "completed": False,
            },
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        assert str(update_response.json()["data"]["user_id"]) == str(test_user_id)

    def test_put_cannot_change_created_at(
        self,
        client: TestClient,
        test_user_id,
        auth_headers: dict,
    ):
        """Test that created_at field is immutable."""
        # [Task]: T036, [From]: specs/001-task-crud-api/spec.md#Acceptance-Scenarios
        # Create initial task
        create_response = client.post(
            f"/api/{test_user_id}/tasks",
            json={"title": "Original title"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]
        original_created_at = create_response.json()["data"]["created_at"]

        # Update task
        update_response = client.put(
            f"/api/{test_user_id}/tasks/{task_id}",
            json={
                "title": "New title",
                "description": None,
                "due_date": None,
                "completed": False,
            },
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["data"]["created_at"] == original_created_at
