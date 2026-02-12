# Data Model Specification - Phase-III

## Overview

This document defines the database models for Phase-III Todo AI Chatbot conversation management using SQLModel. SQLModel combines SQLAlchemy ORM with Pydantic validation, providing both database models and API schemas.

## Database Models

### Conversation Model

Represents a conversation thread between a user and the AI assistant.

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique conversation identifier"
    )

    # Foreign Keys
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Owner of this conversation"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When conversation was created"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When conversation was last updated"
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

**Indexes**:
- `user_id` (automatic via `index=True`) - Fast lookup of all conversations for a user
- Primary key index on `id` (automatic)

**Constraints**:
- `user_id` must reference valid user in `users` table
- `created_at` and `updated_at` cannot be null

**Cascade Behavior**:
- When conversation is deleted, all associated messages are deleted (cascade delete)

---

### Message Model

Represents a single message exchange (user input or assistant response) within a conversation.

```python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text, JSON
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, Literal
from enum import Enum

class MessageRole(str, Enum):
    """Valid message roles"""
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique message identifier"
    )

    # Foreign Keys
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        description="Conversation this message belongs to"
    )

    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User who owns this conversation"
    )

    # Message Data
    role: str = Field(
        nullable=False,
        description="Message role: 'user' or 'assistant'",
        sa_column_kwargs={"check": "role IN ('user', 'assistant')"}
    )

    content: str = Field(
        sa_column=Column(Text),
        nullable=False,
        min_length=1,
        max_length=10000,
        description="Message content"
    )

    tools_used: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="MCP tools invoked (assistant messages only)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="When message was created"
    )

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

**Indexes**:
- `conversation_id` (automatic via `index=True`) - Fast retrieval of all messages in a conversation
- `user_id` (automatic via `index=True`) - Fast filtering by user
- `created_at` (automatic via `index=True`) - Efficient chronological ordering
- Primary key index on `id` (automatic)

**Constraints**:
- `conversation_id` must reference valid conversation
- `user_id` must reference valid user
- `role` must be either "user" or "assistant" (database check constraint)
- `content` must be between 1 and 10,000 characters
- `created_at` cannot be null

**Field Notes**:
- `tools_used`: JSON array, only populated for assistant messages when MCP tools are invoked
- `content`: Uses SQLAlchemy Text type for large text storage

---

## API Models (Pydantic Schemas)

### Conversation Schemas

```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List

class ConversationBase(BaseModel):
    """Base conversation schema"""
    pass

class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation"""
    user_id: UUID

class ConversationRead(ConversationBase):
    """Schema for reading conversation data"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = None

class ConversationWithMessages(ConversationRead):
    """Schema for conversation with full message history"""
    messages: List["MessageRead"]
```

### Message Schemas

```python
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Literal

class MessageBase(BaseModel):
    """Base message schema"""
    content: str

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Content cannot be empty")
        if len(v) > 10000:
            raise ValueError("Content cannot exceed 10,000 characters")
        return v.strip()

class MessageCreate(MessageBase):
    """Schema for creating a new message"""
    conversation_id: UUID
    user_id: UUID
    role: Literal["user", "assistant"]
    tools_used: Optional[List[str]] = None

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ["user", "assistant"]:
            raise ValueError("Role must be 'user' or 'assistant'")
        return v

    @field_validator('tools_used')
    @classmethod
    def validate_tools_used(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
        # tools_used should only be set for assistant messages
        if v is not None and info.data.get('role') == 'user':
            raise ValueError("tools_used can only be set for assistant messages")
        return v

class MessageRead(MessageBase):
    """Schema for reading message data"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    user_id: UUID
    role: Literal["user", "assistant"]
    tools_used: Optional[List[str]] = None
    created_at: datetime

class MessageUpdate(BaseModel):
    """Schema for updating message (limited use case)"""
    content: Optional[str] = None
```

---

## Validation Rules

### Conversation Validation

1. **User Ownership**:
   - `user_id` must reference an existing user
   - User must be authenticated to create conversations
   - User can only access their own conversations

2. **Timestamps**:
   - `created_at` set automatically on creation
   - `updated_at` updated automatically when conversation or messages change
   - Both timestamps use UTC

### Message Validation

1. **Role Validation**:
   - Must be exactly "user" or "assistant"
   - Case-sensitive
   - Enforced at database level via CHECK constraint

2. **Content Validation**:
   - Minimum length: 1 character (after trimming whitespace)
   - Maximum length: 10,000 characters
   - Cannot be null or empty string
   - Whitespace trimmed before storage

3. **Tools Used Validation**:
   - Only valid for assistant messages
   - Must be JSON array of strings
   - Each string should be a valid MCP tool name
   - Null for user messages

4. **Conversation Ownership**:
   - `user_id` in message must match `user_id` of parent conversation
   - Enforced at application level before insert

5. **Chronological Ordering**:
   - Messages ordered by `created_at` ascending
   - `created_at` is immutable after creation

---

## Database Indexes

### Conversations Table

```sql
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at);
```

**Purpose**:
- `user_id`: Fast lookup of all conversations for a user
- `created_at`: Chronological ordering of conversations
- `updated_at`: Finding recently active conversations

### Messages Table

```sql
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
```

**Purpose**:
- `conversation_id`: Fast retrieval of all messages in a conversation
- `user_id`: Fast filtering by user (security checks)
- `created_at`: Chronological ordering within conversations
- `conversation_id, created_at` (composite): Optimized query for paginated message history

---

## Relationships

### One-to-Many: Conversation → Messages

```python
# In Conversation model
messages: List["Message"] = Relationship(
    back_populates="conversation",
    sa_relationship_kwargs={"cascade": "all, delete-orphan"}
)

# In Message model
conversation: Conversation = Relationship(back_populates="messages")
```

**Behavior**:
- One conversation can have many messages
- Deleting a conversation deletes all its messages (cascade)
- Orphaned messages (conversation deleted) are automatically removed
- Messages are ordered by `created_at` when accessed via relationship

**Usage Example**:
```python
# Get all messages for a conversation
conversation = session.get(Conversation, conversation_id)
messages = conversation.messages  # Lazy loaded

# Get conversation from message
message = session.get(Message, message_id)
parent_conversation = message.conversation
```

---

## Migration Script

```python
"""Add conversation and message tables for Phase-III

Revision ID: 003_phase_iii_conversations
Revises: 002_phase_ii_tasks
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create indexes for conversations
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_created_at', 'conversations', ['created_at'])
    op.create_index('idx_conversations_updated_at', 'conversations', ['updated_at'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('conversation_id', UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('tools_used', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_message_role')
    )

    # Create indexes for messages
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_user_id', 'messages', ['user_id'])
    op.create_index('idx_messages_created_at', 'messages', ['created_at'])
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

---

## Usage Examples

### Creating a New Conversation

```python
from sqlmodel import Session, select
from uuid import UUID

def create_conversation(session: Session, user_id: UUID) -> Conversation:
    """Create a new conversation for a user"""
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation
```

### Adding Messages to Conversation

```python
def add_message(
    session: Session,
    conversation_id: UUID,
    user_id: UUID,
    role: str,
    content: str,
    tools_used: Optional[List[str]] = None
) -> Message:
    """Add a message to a conversation"""
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
        tools_used=tools_used
    )
    session.add(message)

    # Update conversation's updated_at timestamp
    conversation = session.get(Conversation, conversation_id)
    conversation.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(message)
    return message
```

### Retrieving Conversation History

```python
def get_conversation_history(
    session: Session,
    conversation_id: UUID,
    user_id: UUID,
    limit: int = 50
) -> List[Message]:
    """Get message history for a conversation"""
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.user_id == user_id)  # Security check
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    messages = session.exec(statement).all()
    return messages
```

### Listing User's Conversations

```python
def get_user_conversations(
    session: Session,
    user_id: UUID,
    limit: int = 20
) -> List[Conversation]:
    """Get all conversations for a user, ordered by most recent"""
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    )
    conversations = session.exec(statement).all()
    return conversations
```

---

## Security Considerations

1. **User Isolation**:
   - Always filter by `user_id` when querying conversations or messages
   - Verify `user_id` matches authenticated user before any operation
   - Use parameterized queries to prevent SQL injection

2. **Data Validation**:
   - Validate all input at API layer using Pydantic schemas
   - Enforce constraints at database level (CHECK constraints)
   - Sanitize content before storage (trim whitespace, check length)

3. **Cascade Deletes**:
   - Conversation deletion cascades to messages (intentional)
   - User deletion should cascade to conversations (configure at users table level)
   - Audit trail: consider soft deletes for compliance requirements

4. **Performance**:
   - Limit message history retrieval (default 50 messages)
   - Use pagination for large conversation histories
   - Index all foreign keys and frequently queried columns
   - Consider archiving old conversations for performance
