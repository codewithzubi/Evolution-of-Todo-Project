from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Optional
from datetime import timedelta
from ..models.user import User
from ..database.connection import get_session_dep
from ..core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from pydantic import BaseModel
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256
import uuid
import logging

# Configure logging to catch bcrypt issues
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# Password hashing function using pbkdf2 (more reliable than bcrypt)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pbkdf2_sha256.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pbkdf2_sha256.hash(password)

class UserCreate(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, session: Session = Depends(get_session_dep)):
    # Check if user already exists
    existing_user = session.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Validate password length (bcrypt limitation is 72 bytes)
    if len(user.password.encode('utf-8')) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password cannot be longer than 72 bytes"
        )

    # Create new user
    try:
        hashed_password = get_password_hash(user.password)
    except Exception as e:
        logger.error(f"Password hashing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password hashing failed"
        )

    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name
    )
    session.add(db_user)
    try:
        session.commit()
        session.refresh(db_user)
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

    return db_user

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, session: Session = Depends(get_session_dep)):
    # Find user by email
    user = session.query(User).filter(User.email == user_credentials.email).first()

    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}