"""Authentication API routes.

Endpoints:
- POST /api/auth/register - User registration
- POST /api/auth/login - User login
- POST /api/auth/logout - User logout
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.models.user import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth_service import register_user, login_user
from app.config import get_settings
from app.api.deps import get_session

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password. Returns JWT token upon success."
)
async def register(
    registration_data: RegisterRequest,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """Register a new user with email and password.

    Args:
        registration_data: User registration data (email, password)
        session: Database session (injected)

    Returns:
        TokenResponse with JWT token and user data

    Raises:
        409: Email already registered
        422: Invalid email format or password too short
    """
    settings = get_settings()
    return register_user(
        registration_data=registration_data,
        session=session,
        secret_key=settings.BETTER_AUTH_SECRET
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user with email and password. Returns JWT token upon success."
)
async def login(
    login_data: LoginRequest,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """Authenticate user with email and password.

    Args:
        login_data: User login credentials (email, password)
        session: Database session (injected)

    Returns:
        TokenResponse with JWT token and user data

    Raises:
        401: Invalid credentials
    """
    settings = get_settings()
    return login_user(
        login_data=login_data,
        session=session,
        secret_key=settings.BETTER_AUTH_SECRET
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout user (client-side token clearing). Server returns success message."
)
async def logout() -> dict:
    """Logout user.

    Note: In stateless JWT architecture, logout is handled client-side by clearing the token.
    This endpoint returns a success message for consistency.

    Returns:
        Success message
    """
    return {"message": "Logout successful. Please clear your token on the client side."}
