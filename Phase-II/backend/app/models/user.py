"""User model and schemas."""
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

from sqlmodel import SQLModel, Field
from pydantic import BaseModel, EmailStr


# Database Model
class User(SQLModel, table=True):
    """User account model for authentication."""
    
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Request Models
class RegisterRequest(BaseModel):
    """Request model for user registration."""
    
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    }


class LoginRequest(BaseModel):
    """Request model for user login."""
    
    email: EmailStr
    password: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    }


# Response Models
class UserResponse(BaseModel):
    """Response model for user data (excludes password)."""
    
    id: UUID
    email: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2026-02-10T12:00:00Z"
            }
        }
    }


class TokenResponse(BaseModel):
    """Response model for authentication (includes JWT token)."""
    
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "created_at": "2026-02-10T12:00:00Z"
                }
            }
        }
    }
