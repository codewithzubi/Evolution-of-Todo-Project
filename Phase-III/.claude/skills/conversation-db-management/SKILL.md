# Conversation DB Management

## Purpose
Design and implement database schema and operations for persisting complete chat history, linking conversations to users, and enabling conversation resumption across client refreshes and server restarts.

## Key Principles
- **Full History Persistence**: Every message is persisted; nothing is lost on disconnect/restart
- **User-Scoped Data**: All conversations and messages linked to user_id for multi-user isolation
- **Resumability**: Clients can fetch full history and continue conversation seamlessly
- **Audit Trail**: Timestamps and message metadata preserved for compliance and debugging
- **Efficient Queries**: Proper indexing for fast history retrieval and pagination
- **Scalability**: Schema designed for serverless PostgreSQL with connection pooling

## Core Responsibilities

### 1. Database Schema Design

#### Conversations Table
```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,  -- soft delete support

  CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX idx_user_conversations (user_id, created_at DESC),
  INDEX idx_user_updated (user_id, updated_at DESC)
);
```

#### Messages Table
```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  -- Optional: metadata for tool calls, attachments, etc.
  metadata JSONB DEFAULT NULL,  -- {"tool_call_id": "...", "tool_name": "..."}

  CONSTRAINT fk_conversation FOREIGN KEY (conversation_id) REFERENCES conversations(id),
  CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX idx_conversation_messages (conversation_id, created_at ASC),
  INDEX idx_user_messages (user_id, created_at DESC),
  INDEX idx_created_at (created_at)
);
```

### 2. SQLModel ORM Models

#### Conversation Model
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class ConversationBase(SQLModel):
    title: str
    description: Optional[str] = None
    user_id: UUID

class Conversation(ConversationBase, table=True):
    __tablename__ = "conversations"

    id: Optional[UUID] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

class ConversationRead(ConversationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
```

#### Message Model
```python
class MessageBase(SQLModel):
    role: str  # "user" | "assistant" | "system"
    content: str
    conversation_id: UUID
    user_id: UUID

class Message(MessageBase, table=True):
    __tablename__ = "messages"

    id: Optional[UUID] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))

class MessageRead(MessageBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    metadata: Optional[dict] = None
```

### 3. Core Database Operations

#### Create Conversation
```python
async def create_conversation(
    session: Session,
    user_id: UUID,
    title: str,
    description: Optional[str] = None
) -> Conversation:
    """Create new conversation for user."""
    conversation = Conversation(
        user_id=user_id,
        title=title,
        description=description
    )
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation
```

#### Store Message
```python
async def store_message(
    session: Session,
    conversation_id: UUID,
    user_id: UUID,
    role: str,  # "user" | "assistant"
    content: str,
    metadata: Optional[dict] = None
) -> Message:
    """Store message in conversation."""
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
        metadata=metadata
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message
```

#### Fetch Conversation History
```python
async def get_conversation_messages(
    session: Session,
    conversation_id: UUID,
    user_id: UUID,
    limit: int = 100,
    offset: int = 0
) -> tuple[list[Message], int]:
    """Fetch paginated message history for conversation.

    Returns:
        (messages, total_count) - ordered chronologically
    """
    # Validate user owns conversation
    conversation = await session.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Fetch messages
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).offset(offset).limit(limit)

    result = await session.execute(statement)
    messages = result.scalars().all()

    # Get total count
    count_statement = select(func.count(Message.id)).where(
        Message.conversation_id == conversation_id
    )
    count_result = await session.execute(count_statement)
    total = count_result.scalar()

    return messages, total
```

#### Fetch All Conversations
```python
async def get_user_conversations(
    session: Session,
    user_id: UUID,
    limit: int = 20,
    offset: int = 0
) -> tuple[list[Conversation], int]:
    """Fetch user's conversations ordered by most recent."""
    statement = select(Conversation).where(
        Conversation.user_id == user_id,
        Conversation.deleted_at.is_(None)  # exclude soft-deleted
    ).order_by(Conversation.updated_at.desc()).offset(offset).limit(limit)

    result = await session.execute(statement)
    conversations = result.scalars().all()

    count_statement = select(func.count(Conversation.id)).where(
        Conversation.user_id == user_id,
        Conversation.deleted_at.is_(None)
    )
    count_result = await session.execute(count_statement)
    total = count_result.scalar()

    return conversations, total
```

#### Update Conversation
```python
async def update_conversation(
    session: Session,
    conversation_id: UUID,
    user_id: UUID,
    **updates
) -> Conversation:
    """Update conversation (title, description)."""
    conversation = await session.get(Conversation, conversation_id)

    if not conversation or conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    for key, value in updates.items():
        if key in ["title", "description"]:
            setattr(conversation, key, value)

    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation
```

#### Soft Delete Conversation
```python
async def delete_conversation(
    session: Session,
    conversation_id: UUID,
    user_id: UUID
) -> None:
    """Soft-delete conversation (preserves history for audit)."""
    conversation = await session.get(Conversation, conversation_id)

    if not conversation or conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    conversation.deleted_at = datetime.utcnow()
    session.add(conversation)
    await session.commit()
```

### 4. Resumption Flow

When client reconnects or refreshes:
1. Client sends: `GET /api/v1/conversations/{conversation_id}`
2. Backend validates user ownership
3. Backend fetches conversation metadata
4. Client sends: `GET /api/v1/conversations/{conversation_id}/messages`
5. Backend returns paginated message history (most recent first for UI scrollback)
6. Client reconstructs conversation UI from message history
7. Client can continue sending messages to same conversation_id

### 5. User Isolation & Security
- All queries filter by `user_id` from JWT token
- Foreign key constraints: `REFERENCES users(id) ON DELETE CASCADE`
- Soft deletes preserve data for audits but hide from normal queries
- Prevent cross-user access: 403 if `conversation.user_id != authenticated_user_id`

### 6. Performance & Indexing
- `idx_user_conversations`: Fast lookup of user's conversations
- `idx_conversation_messages`: Fast retrieval of messages for a conversation
- `idx_created_at`: Support for time-range queries
- Consider: Partitioning large tables by user_id for horizontal scaling

### 7. Data Integrity

#### Constraints
- Conversations.user_id: NOT NULL, REFERENCES users(id)
- Messages.conversation_id: NOT NULL, REFERENCES conversations(id)
- Messages.user_id: NOT NULL, REFERENCES users(id)
- Messages.role: CHECK (role IN ('user', 'assistant', 'system'))

#### Cascade Delete
- Delete user → Delete all conversations + messages
- Delete conversation → Delete all messages
- Preserves referential integrity

### 8. Migration Strategy

#### Alembic Migration Example
```python
# Create initial schema
def upgrade():
    op.create_table('conversations',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.func.gen_random_uuid()),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    op.create_index('idx_user_conversations', 'conversations', ['user_id', 'created_at'], postgresql_using='btree')

    op.create_table('messages',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.func.gen_random_uuid()),
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('metadata', sa.JSON()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')"),
    )

    op.create_index('idx_conversation_messages', 'messages', ['conversation_id', 'created_at'])
```

## Implementation Workflow

1. **Design Schema**
   - Create Conversations and Messages tables with proper relationships
   - Add indexes for common queries
   - Define constraints and cascade rules

2. **Implement SQLModel Models**
   - Conversation model with timestamps and soft delete
   - Message model with role, content, and metadata
   - Read/Create schemas for API contracts

3. **Implement CRUD Operations**
   - Create conversation, store messages, fetch history
   - Update conversation metadata
   - Soft delete with preserved audit trail
   - Efficient pagination for large histories

4. **Create Database Migrations**
   - Use Alembic to version schema changes
   - Support rollback on deployment issues
   - Document migration rationale

5. **Testing & Validation**
   - Test conversation creation and message persistence
   - Test resumption: create conversation, stop, resume, verify history
   - Test user isolation: verify users can't access other's data
   - Test pagination: large conversations load efficiently
   - Test cascade delete: deleting user cascades to conversations and messages

## Success Criteria
✅ Conversations and Messages tables created with proper relationships
✅ All messages persisted to database immediately
✅ User isolation enforced (conversation.user_id matches JWT user_id)
✅ Conversation can be resumed after client refresh
✅ Message history preserved across server restarts
✅ Soft deletes preserve audit trail
✅ Pagination works efficiently for large conversations
✅ Cascade delete maintains referential integrity
✅ Indexes support common query patterns
✅ Migrations are version-controlled and reversible

## Related Components
- **Neon Database**: PostgreSQL storage
- **SQLAlchemy/SQLModel**: ORM layer
- **FastAPI Backend**: Endpoint handlers
- **JWT Auth**: User context extraction
- **Alembic**: Schema migration tool

## Scalability Considerations
- Connection pooling (pgbouncer/PgPool) for serverless
- Lazy loading of messages for UI (pagination)
- Archive old conversations to cold storage
- Consider table partitioning by user_id for very large deployments
- Monitor query latency; optimize N+1 patterns

## Data Retention Policy
- Active conversations: Keep all messages indefinitely
- Soft-deleted conversations: Consider retention period (e.g., 30 days before hard delete)
- Archived conversations: Move to read-only storage
- Compliance: Ensure deletion respects data protection regulations (GDPR, etc.)
