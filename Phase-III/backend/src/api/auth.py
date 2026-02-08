# [Task]: Authentication endpoints for user login and signup
# REST API endpoints for user authentication

from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import hashlib
import secrets

from ..database import get_session
from ..models.base import User
from ..config import settings
from .schemas import LoginRequest, SignupRequest, AuthResponse, ErrorResponse
from jose import jwt, JWTError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


def _hash_password(password: str) -> str:
    """Hash password using PBKDF2."""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${hashed.hex()}"


def _verify_password(password: str, hash_str: str) -> bool:
    """Verify password against hash."""
    try:
        salt, hashed = hash_str.split('$')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return new_hash.hex() == hashed
    except:
        return False


@router.post(
    "/signup",
    status_code=201,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        400: {"model": ErrorResponse, "description": "Bad request"},
    },
)
async def signup(request: SignupRequest, session: AsyncSession = Depends(get_session)):
    """
    Register a new user with email and password.

    Creates a new user account and returns JWT token.
    """
    try:
        # Check if user already exists
        stmt = select(User).where(User.email == request.email)
        existing = await session.execute(stmt)
        if existing.scalars().first():
            raise HTTPException(status_code=400, detail="User already exists")

        # Hash password
        password_hash = _hash_password(request.password)

        # Create new user
        user_id = uuid4()
        new_user = User(
            id=user_id,
            email=request.email,
            name=request.email.split("@")[0],  # Use email prefix as name
            password_hash=password_hash,
            email_verified=True,
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        # Generate JWT token
        token = _generate_token(str(user_id), request.email)

        logger.info(f"User signed up: {request.email}")

        return {
            "data": {
                "user": {
                    "id": str(new_user.id),
                    "email": new_user.email,
                    "name": new_user.name,
                    "createdAt": new_user.created_at.isoformat(),
                },
                "token": token,
                "expiresIn": 86400,  # 24 hours in seconds
            },
            "error": None,
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create account")


@router.post(
    "/login",
    status_code=200,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
async def login(request: LoginRequest, session: AsyncSession = Depends(get_session)):
    """
    Authenticate user with email and password.

    Returns JWT token if credentials are valid.
    """
    try:
        # Find user by email
        stmt = select(User).where(User.email == request.email)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if not user or not _verify_password(request.password, user.password_hash):
            logger.warning(f"Login attempt with invalid credentials: {request.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Generate JWT token
        token = _generate_token(str(user.id), user.email)

        logger.info(f"User logged in: {request.email}")

        return {
            "data": {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.name,
                    "createdAt": user.created_at.isoformat(),
                },
                "token": token,
                "expiresIn": 86400,  # 24 hours in seconds
            },
            "error": None,
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Failed to authenticate")


@router.post(
    "/refresh",
    status_code=200,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid or missing token"},
    },
)
async def refresh(request: Request):
    """
    Refresh JWT token using current token from Authorization header.

    Allows expired tokens to be refreshed.
    """
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

        token = auth_header[7:]  # Remove "Bearer " prefix

        # Decode token without verifying expiration (we want to refresh expired tokens)
        # but still verify the signature
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
                options={"verify_exp": False}  # Allow expired tokens
            )
        except JWTError as e:
            logger.warning(f"JWT decode error during refresh: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")

        user_id = payload.get("user_id")
        email = payload.get("email")

        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid token claims")

        # Generate new token
        new_token = _generate_token(user_id, email)

        logger.info(f"Token refreshed for user: {email}")

        return {
            "data": {
                "token": new_token,
                "expiresIn": 86400,  # 24 hours in seconds
            },
            "error": None,
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=401, detail="Token refresh failed")


def _generate_token(user_id: str, email: str) -> str:
    """
    Generate JWT token for authenticated user.

    Args:
        user_id: User's UUID as string
        email: User's email address

    Returns:
        JWT token string
    """
    now = datetime.utcnow()
    expires = now + timedelta(hours=24)

    payload = {
        "user_id": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    return token
