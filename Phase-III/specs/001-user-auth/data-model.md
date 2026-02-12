# Data Model: User Authentication System

**Feature**: 001-user-auth
**Date**: 2026-02-09
**Purpose**: Define database entities, relationships, and validation rules for authentication system

## Overview

The authentication system requires minimal database schema focused on user accounts. Better Auth may create additional tables automatically for session management and OAuth providers.

## Entities

### User

**Purpose**: Represents a registered user account with authentication credentials

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key | Unique user identifier (UUID v4) |
| email | String (255) | Unique, Not Null, Index | User's email address (login identifier) |
| hashed_password | String (255) | Not Null | bcrypt-hashed password (never store plain text) |
| created_at | DateTime | Not Null, Default: now() | Account creation timestamp |

**Indexes**:
- Primary: `id` (clustered index for fast lookups)
- Unique: `email` (enforce uniqueness, fast email-based queries)

**Validation Rules**:
- Email: Must match regex pattern `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- Email: Maximum length 255 characters
- Email: Case-insensitive (normalize to lowercase before storage)
- Password (plain): Minimum 8 characters (validated before hashing)
- Password (hashed): bcrypt format `$2b$12$...` (60 characters)

**Business Rules**:
- Email must be unique across all users
- Password must be hashed with bcrypt before storage (never store plain text)
- created_at is immutable after creation
- UUID v4 generated automatically on user creation

**Relationships**:
- One-to-Many with Tasks (future feature): `User.id` → `Task.user_id`
- No sessions table (stateless JWT architecture)

**SQLModel Schema**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4

class User(SQLModel, table=True):
    """User account model for authentication"""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User's email address (login identifier)"
    )
    hashed_password: str = Field(
        max_length=255,
        description="bcrypt-hashed password"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "hashed_password": "$2b$12$...",
                "created_at": "2026-02-09T12:00:00Z"
            }
        }
```

**Pydantic Models (API)**:
```python
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    """Request model for user registration"""
    email: EmailStr
    password: str = Field(min_length=8, description="Minimum 8 characters")

class UserLogin(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Response model for user data (excludes password)"""
    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Response model for authentication (includes JWT token)"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

---

## Entity Relationships

```
┌─────────────────┐
│     User        │
├─────────────────┤
│ id (PK)         │
│ email (UNIQUE)  │
│ hashed_password │
│ created_at      │
│ updated_at      │
└─────────────────┘
        │
        │ 1:N (future)
        ▼
┌─────────────────┐
│     Task        │  (Future feature)
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ title           │
│ description     │
│ completed       │
│ created_at      │
└─────────────────┘
```

---

## State Transitions

### User Account Lifecycle

```
[No Account]
    │
    │ Registration (POST /api/auth/register)
    ▼
[Active Account]
    │
    ├─→ Login (POST /api/auth/login) → [Authenticated Session]
    │
    ├─→ Logout (POST /api/auth/logout) → [Unauthenticated]
    │
    └─→ (Future) Delete Account → [Deleted]
```

### Authentication Session Lifecycle

```
[Unauthenticated]
    │
    │ Login Success
    ▼
[Authenticated]
    │
    ├─→ Token Expires (7 days) → [Unauthenticated]
    │
    ├─→ Explicit Logout → [Unauthenticated]
    │
    └─→ Token Refresh → [Authenticated] (Better Auth handles automatically)
```

---

## Database Migrations

### Initial Migration (Alembic)

**Migration**: `001_create_users_table.py`

```python
"""Create users table

Revision ID: 001
Create Date: 2026-02-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

def downgrade():
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
```

**Migration Command**:
```bash
# Generate migration
alembic revision --autogenerate -m "Create users table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## Data Validation

### Email Validation

**Format**: RFC 5322 compliant email address
**Regex**: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
**Normalization**: Convert to lowercase before storage
**Max Length**: 255 characters

**Valid Examples**:
- user@example.com
- john.doe+tag@company.co.uk
- test_user123@subdomain.example.com

**Invalid Examples**:
- user@example (no TLD)
- @example.com (no local part)
- user @example.com (space in email)
- user@.com (invalid domain)

### Password Validation

**Plain Password (before hashing)**:
- Minimum length: 8 characters
- No maximum length (bcrypt handles truncation at 72 bytes)
- No complexity requirements (balance security and UX)

**Hashed Password (after bcrypt)**:
- Format: `$2b$12$...` (bcrypt identifier + cost + salt + hash)
- Length: 60 characters
- Cost factor: 12 rounds (~250ms hashing time)

---

## Security Considerations

### Password Storage
- ✅ Never store plain text passwords
- ✅ Use bcrypt with cost factor 12
- ✅ Salt automatically generated by bcrypt
- ✅ Hashed password never exposed in API responses

### Email Privacy
- ✅ Email addresses are PII (Personally Identifiable Information)
- ✅ Never expose email in public APIs without authentication
- ✅ Use case-insensitive comparison for login
- ✅ Normalize to lowercase to prevent duplicate accounts (user@example.com vs USER@example.com)

### Data Retention
- User accounts persist indefinitely (no automatic deletion)
- Future enhancement: Account deletion endpoint
- Comply with data protection regulations (GDPR, CCPA) if deployed publicly

---

## Performance Considerations

### Query Optimization
- Email index enables fast lookups: O(log n) instead of O(n)
- Primary key index for fast user_id lookups
- created_at/updated_at not indexed (rarely queried directly)

### Expected Query Patterns
1. **Login**: `SELECT * FROM users WHERE email = ?` (indexed, fast)
2. **Registration**: `INSERT INTO users (email, hashed_password, ...)` (fast)
3. **Check email exists**: `SELECT COUNT(*) FROM users WHERE email = ?` (indexed, fast)
4. **Get user by ID**: `SELECT * FROM users WHERE id = ?` (primary key, very fast)

### Scalability
- Single users table scales to millions of records with proper indexing
- No N+1 query problems (no relationships in Phase II)
- Connection pooling handled by SQLModel/SQLAlchemy

---

## Testing Data

### Test Users (for development/testing)

```python
test_users = [
    {
        "email": "test@example.com",
        "password": "password123",  # Will be hashed
        "created_at": "2026-02-09T12:00:00Z"
    },
    {
        "email": "admin@example.com",
        "password": "adminpass123",
        "created_at": "2026-02-09T12:00:00Z"
    }
]
```

**Note**: Test users should only exist in development/test databases, never in production.

---

## Future Enhancements (Out of Scope for Phase II)

- Email verification status (boolean field)
- Last login timestamp
- Failed login attempts counter
- Account status (active, suspended, deleted)
- User profile fields (name, avatar, preferences)
- OAuth provider linkage (Better Auth handles this)
- Two-factor authentication secrets
- Password reset tokens

---

## Summary

The authentication data model is intentionally minimal, focusing on core user account management. The `users` table stores email and hashed password, with proper indexing for performance. Better Auth handles additional complexity (sessions, OAuth) through its own tables. This design aligns with constitution principles of simplicity and clean architecture.
