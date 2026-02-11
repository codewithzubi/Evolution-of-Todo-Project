"""Unit tests for JWT service.

Tests for User Story 3: JWT Token Management
- Valid token creation and verification
- Expired token handling
- Invalid signature detection
- User ID extraction
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from jose import jwt

from app.services.jwt_service import (
    create_token,
    verify_token,
    extract_user_id,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_DAYS
)


@pytest.mark.unit
class TestJWTService:
    """Test suite for JWT token operations."""

    def test_create_token_valid(self):
        """Test creating a valid JWT token."""
        # Arrange
        user_id = uuid4()
        email = "test@example.com"
        secret_key = "test-secret-key-32-characters-long"

        # Act
        token = create_token(user_id, email, secret_key)

        # Assert
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token can be decoded
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        assert payload["user_id"] == str(user_id)
        assert payload["email"] == email
        assert "exp" in payload
        assert "iat" in payload

    def test_verify_token_valid(self):
        """Test verifying a valid JWT token."""
        # Arrange
        user_id = uuid4()
        email = "test@example.com"
        secret_key = "test-secret-key-32-characters-long"
        token = create_token(user_id, email, secret_key)

        # Act
        payload = verify_token(token, secret_key)

        # Assert
        assert payload is not None
        assert payload["user_id"] == str(user_id)
        assert payload["email"] == email
        assert "exp" in payload
        assert "iat" in payload

    def test_verify_token_expired(self):
        """Test verifying an expired JWT token."""
        # Arrange
        user_id = uuid4()
        email = "test@example.com"
        secret_key = "test-secret-key-32-characters-long"

        # Create an expired token (expired 1 day ago)
        expire = datetime.utcnow() - timedelta(days=1)
        payload = {
            "user_id": str(user_id),
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow() - timedelta(days=2)
        }
        expired_token = jwt.encode(payload, secret_key, algorithm=ALGORITHM)

        # Act
        result = verify_token(expired_token, secret_key)

        # Assert
        assert result is None  # Expired tokens should return None

    def test_verify_token_invalid_signature(self):
        """Test verifying a token with invalid signature."""
        # Arrange
        user_id = uuid4()
        email = "test@example.com"
        secret_key = "test-secret-key-32-characters-long"
        wrong_secret_key = "wrong-secret-key-32-characters-long"

        # Create token with one secret
        token = create_token(user_id, email, secret_key)

        # Act - try to verify with different secret
        result = verify_token(token, wrong_secret_key)

        # Assert
        assert result is None  # Invalid signature should return None

    def test_verify_token_malformed(self):
        """Test verifying a malformed JWT token."""
        # Arrange
        secret_key = "test-secret-key-32-characters-long"
        malformed_token = "not.a.valid.jwt.token"

        # Act
        result = verify_token(malformed_token, secret_key)

        # Assert
        assert result is None  # Malformed tokens should return None

    def test_verify_token_empty(self):
        """Test verifying an empty token."""
        # Arrange
        secret_key = "test-secret-key-32-characters-long"
        empty_token = ""

        # Act
        result = verify_token(empty_token, secret_key)

        # Assert
        assert result is None  # Empty tokens should return None

    def test_extract_user_id_valid(self):
        """Test extracting user_id from a valid token."""
        # Arrange
        user_id = uuid4()
        email = "test@example.com"
        secret_key = "test-secret-key-32-characters-long"
        token = create_token(user_id, email, secret_key)

        # Act
        extracted_user_id = extract_user_id(token, secret_key)

        # Assert
        assert extracted_user_id is not None
        assert isinstance(extracted_user_id, UUID)
        assert extracted_user_id == user_id

    def test_extract_user_id_invalid_token(self):
        """Test extracting user_id from an invalid token."""
        # Arrange
        secret_key = "test-secret-key-32-characters-long"
        invalid_token = "invalid.token.here"

        # Act
        extracted_user_id = extract_user_id(invalid_token, secret_key)

        # Assert
        assert extracted_user_id is None

    def test_extract_user_id_expired_token(self):
        """Test extracting user_id from an expired token."""
        # Arrange
        user_id = uuid4()
        email = "test@example.com"
        secret_key = "test-secret-key-32-characters-long"

        # Create an expired token
        expire = datetime.utcnow() - timedelta(days=1)
        payload = {
            "user_id": str(user_id),
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow() - timedelta(days=2)
        }
        expired_token = jwt.encode(payload, secret_key, algorithm=ALGORITHM)

        # Act
        extracted_user_id = extract_user_id(expired_token, secret_key)

        # Assert
        assert extracted_user_id is None  # Expired tokens should return None

    def test_token_expiration_time(self):
        """Test that token expiration is set correctly."""
        # Arrange
        user_id = uuid4()
        email = "test@example.com"
        secret_key = "test-secret-key-32-characters-long"

        # Act
        token = create_token(user_id, email, secret_key)
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])

        # Assert
        exp_timestamp = payload["exp"]
        iat_timestamp = payload["iat"]

        # Convert timestamps to datetime
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        iat_datetime = datetime.fromtimestamp(iat_timestamp)

        # Check that expiration is approximately ACCESS_TOKEN_EXPIRE_DAYS from issued time
        time_diff = exp_datetime - iat_datetime
        expected_diff = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

        # Allow 1 second tolerance for test execution time
        assert abs(time_diff.total_seconds() - expected_diff.total_seconds()) < 1

    def test_token_contains_required_claims(self):
        """Test that token contains all required claims."""
        # Arrange
        user_id = uuid4()
        email = "test@example.com"
        secret_key = "test-secret-key-32-characters-long"

        # Act
        token = create_token(user_id, email, secret_key)
        payload = verify_token(token, secret_key)

        # Assert
        assert payload is not None
        assert "user_id" in payload
        assert "email" in payload
        assert "exp" in payload  # Expiration time
        assert "iat" in payload  # Issued at time

    def test_extract_user_id_missing_user_id_claim(self):
        """Test extracting user_id when user_id claim is missing."""
        # Arrange
        secret_key = "test-secret-key-32-characters-long"

        # Create token without user_id claim
        payload = {
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(days=1),
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, secret_key, algorithm=ALGORITHM)

        # Act
        extracted_user_id = extract_user_id(token, secret_key)

        # Assert
        assert extracted_user_id is None

    def test_extract_user_id_invalid_uuid_format(self):
        """Test extracting user_id when user_id is not a valid UUID."""
        # Arrange
        secret_key = "test-secret-key-32-characters-long"

        # Create token with invalid UUID
        payload = {
            "user_id": "not-a-valid-uuid",
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(days=1),
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, secret_key, algorithm=ALGORITHM)

        # Act
        extracted_user_id = extract_user_id(token, secret_key)

        # Assert
        assert extracted_user_id is None
