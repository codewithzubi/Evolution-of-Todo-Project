"""Authentication service for user registration and login.

This service handles:
- User registration with email/password
- Email validation and duplicate checking
- Password hashing
- User creation in database
- JWT token generation
"""

from uuid import UUID
from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.models.user import User, RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.services.password_service import hash_password, verify_password
from app.services.jwt_service import create_token


def register_user(
    registration_data: RegisterRequest,
    session: Session,
    secret_key: str
) -> TokenResponse:
    """Register a new user with email and password.

    Args:
        registration_data: User registration data (email, password)
        session: Database session
        secret_key: BETTER_AUTH_SECRET for JWT signing

    Returns:
        TokenResponse with JWT token and user data

    Raises:
        HTTPException 409: Email already registered
        HTTPException 422: Invalid email format (handled by Pydantic)
    """
    # Normalize email to lowercase
    email = registration_data.email.lower()

    # Check if email already exists
    statement = select(User).where(User.email == email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = hash_password(registration_data.password)

    # Create new user
    new_user = User(
        email=email,
        hashed_password=hashed_password
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Generate JWT token
    access_token = create_token(
        user_id=new_user.id,
        email=new_user.email,
        secret_key=secret_key
    )

    # Return token response
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            created_at=new_user.created_at
        )
    )


def login_user(
    login_data: LoginRequest,
    session: Session,
    secret_key: str
) -> TokenResponse:
    """Authenticate user with email and password.

    Args:
        login_data: User login credentials (email, password)
        session: Database session
        secret_key: BETTER_AUTH_SECRET for JWT signing

    Returns:
        TokenResponse with JWT token and user data

    Raises:
        HTTPException 401: Invalid credentials
    """
    # Normalize email to lowercase
    email = login_data.email.lower()

    # Find user by email
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    # Verify user exists and password is correct
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    access_token = create_token(
        user_id=user.id,
        email=user.email,
        secret_key=secret_key
    )

    # Return token response
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            created_at=user.created_at
        )
    )
