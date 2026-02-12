"""Integration tests for authentication routes.

Tests for User Story 1: New User Registration
- Valid registration
- Duplicate email
- Invalid email format
- Short password
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.models.user import User


@pytest.mark.integration
class TestRegistration:
    """Test suite for POST /api/auth/register endpoint."""

    def test_valid_registration(self, client: TestClient, session: Session):
        """Test successful user registration with valid email and password."""
        # Arrange
        registration_data = {
            "email": "newuser@example.com",
            "password": "password123"
        }

        # Act
        response = client.post("/api/auth/register", json=registration_data)

        # Assert
        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

        # Verify user data
        user_data = data["user"]
        assert user_data["email"] == "newuser@example.com"
        assert "id" in user_data
        assert "created_at" in user_data
        assert "hashed_password" not in user_data  # Password should not be exposed

        # Verify user was created in database
        db_user = session.query(User).filter(User.email == "newuser@example.com").first()
        assert db_user is not None
        assert db_user.email == "newuser@example.com"
        assert db_user.hashed_password != "password123"  # Should be hashed

    def test_duplicate_email_registration(self, client: TestClient, test_user: User):
        """Test registration fails when email already exists."""
        # Arrange - test_user fixture already created a user with test@example.com
        registration_data = {
            "email": "test@example.com",  # Same as test_user
            "password": "newpassword123"
        }

        # Act
        response = client.post("/api/auth/register", json=registration_data)

        # Assert
        assert response.status_code == 409  # Conflict
        data = response.json()
        assert "detail" in data
        assert "already registered" in data["detail"].lower()

    def test_invalid_email_format(self, client: TestClient):
        """Test registration fails with invalid email format."""
        # Arrange
        invalid_emails = [
            "notanemail",
            "missing@domain",
            "@nodomain.com",
            "spaces in@email.com",
            "user@",
        ]

        for invalid_email in invalid_emails:
            registration_data = {
                "email": invalid_email,
                "password": "password123"
            }

            # Act
            response = client.post("/api/auth/register", json=registration_data)

            # Assert
            assert response.status_code == 422  # Unprocessable Entity (validation error)
            data = response.json()
            assert "detail" in data

    def test_short_password(self, client: TestClient):
        """Test registration fails when password is shorter than 8 characters."""
        # Arrange
        registration_data = {
            "email": "user@example.com",
            "password": "short"  # Only 5 characters
        }

        # Act
        response = client.post("/api/auth/register", json=registration_data)

        # Assert
        assert response.status_code == 422  # Unprocessable Entity (validation error)
        data = response.json()
        assert "detail" in data
        # Verify error mentions password length
        error_message = str(data["detail"]).lower()
        assert "password" in error_message or "8" in error_message

    def test_missing_email(self, client: TestClient):
        """Test registration fails when email is missing."""
        # Arrange
        registration_data = {
            "password": "password123"
            # email is missing
        }

        # Act
        response = client.post("/api/auth/register", json=registration_data)

        # Assert
        assert response.status_code == 422  # Unprocessable Entity

    def test_missing_password(self, client: TestClient):
        """Test registration fails when password is missing."""
        # Arrange
        registration_data = {
            "email": "user@example.com"
            # password is missing
        }

        # Act
        response = client.post("/api/auth/register", json=registration_data)

        # Assert
        assert response.status_code == 422  # Unprocessable Entity

    def test_empty_request_body(self, client: TestClient):
        """Test registration fails with empty request body."""
        # Act
        response = client.post("/api/auth/register", json={})

        # Assert
        assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.integration
class TestLogin:
    """Test suite for POST /api/auth/login endpoint."""

    def test_valid_login(self, client: TestClient, test_user: User):
        """Test successful login with valid credentials."""
        # Arrange
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }

        # Act
        response = client.post("/api/auth/login", json=login_data)

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

        # Verify user data
        user_data = data["user"]
        assert user_data["email"] == "test@example.com"
        assert user_data["id"] == str(test_user.id)
        assert "created_at" in user_data
        assert "hashed_password" not in user_data  # Password should not be exposed

    def test_invalid_password(self, client: TestClient, test_user: User):
        """Test login fails with incorrect password."""
        # Arrange
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }

        # Act
        response = client.post("/api/auth/login", json=login_data)

        # Assert
        assert response.status_code == 401  # Unauthorized
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower()

    def test_nonexistent_email(self, client: TestClient):
        """Test login fails with non-existent email."""
        # Arrange
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }

        # Act
        response = client.post("/api/auth/login", json=login_data)

        # Assert
        assert response.status_code == 401  # Unauthorized
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower()

    def test_case_insensitive_email(self, client: TestClient, test_user: User):
        """Test login works with different email case."""
        # Arrange
        login_data = {
            "email": "TEST@EXAMPLE.COM",  # Uppercase
            "password": "password123"
        }

        # Act
        response = client.post("/api/auth/login", json=login_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == "test@example.com"  # Normalized to lowercase

    def test_missing_email_login(self, client: TestClient):
        """Test login fails when email is missing."""
        # Arrange
        login_data = {
            "password": "password123"
            # email is missing
        }

        # Act
        response = client.post("/api/auth/login", json=login_data)

        # Assert
        assert response.status_code == 422  # Unprocessable Entity

    def test_missing_password_login(self, client: TestClient):
        """Test login fails when password is missing."""
        # Arrange
        login_data = {
            "email": "test@example.com"
            # password is missing
        }

        # Act
        response = client.post("/api/auth/login", json=login_data)

        # Assert
        assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.integration
class TestLogout:
    """Test suite for POST /api/auth/logout endpoint."""

    def test_successful_logout(self, client: TestClient):
        """Test successful logout."""
        # Act
        response = client.post("/api/auth/logout")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "logout" in data["message"].lower() or "success" in data["message"].lower()

    def test_logout_without_token(self, client: TestClient):
        """Test logout works even without authentication token (stateless)."""
        # Arrange - no authentication token provided

        # Act
        response = client.post("/api/auth/logout")

        # Assert
        # In stateless JWT architecture, logout endpoint should return success
        # regardless of authentication status (client clears token)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_logout_idempotent(self, client: TestClient):
        """Test logout can be called multiple times (idempotent)."""
        # Act - call logout twice
        response1 = client.post("/api/auth/logout")
        response2 = client.post("/api/auth/logout")

        # Assert - both should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
