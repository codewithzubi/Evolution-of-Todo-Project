# SQLModel ORM and Database Schema Documentation

## Overview

This document provides comprehensive guidance for using SQLModel ORM models, database schema design, and data access patterns in the Phase-II and Phase-III Todo Application.

**Key Principles**:
- Type-safe ORM using SQLModel (Pydantic + SQLAlchemy)
- User-scoped data isolation (every query filters by user_id)
- Soft deletes for audit trail preservation
- Optimized indexes for query performance
- Async/await patterns for non-blocking database operations

---

## Table of Contents

1. [Database Schema Overview](#database-schema-overview)
2. [Phase-II Tables (Task Management)](#phase-ii-tables)
3. [Phase-III Tables (Conversation Persistence)](#phase-iii-tables)
4. [User Isolation and Data Scoping](#user-isolation-and-data-scoping)
5. [Soft Delete Strategy](#soft-delete-strategy)
6. [Index Strategy and Query Optimization](#index-strategy-and-query-optimization)
7. [Example Queries](#example-queries)
8. [Best Practices](#best-practices)
9. [Performance Considerations](#performance-considerations)

---

## Database Schema Overview

### ER Diagram

```
users (Phase-II)
  ├── 1:N → tasks (Phase-II)
  ├── 1:N → conversations (Phase-III)
  └── 1:N → messages (Phase-III)

conversations (Phase-III)
  └── 1:N → messages (Phase-III)
```

### Key Relationships

**Phase-II** (existing):
- `users` table: authenticated users
- `tasks` table: user-owned tasks with title, description, completion status

**Phase-III** (new):
- `conversations` table: chat sessions between user and AI
- `messages` table: individual messages within conversations

---

## Phase-II Tables

### Users Table

**Purpose**: Store authenticated user information (from Better Auth)

**Schema**:
```python
class User(BaseModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str
    password_hash: str
    image: Optional[str] = None
    email_verified: bool = False
    created_at: datetime
    updated_at: datetime
```

**Indexes**:
- PRIMARY KEY (id)
- UNIQUE INDEX (email) - enables login by email

**Foreign Key References**:
- tasks.user_id → users.id (CASCADE DELETE)
- conversations.user_id → users.id (CASCADE DELETE)
- messages.user_id → users.id (CASCADE DELETE)

### Tasks Table

**Purpose**: Store user-owned tasks (project management)

**Schema**:
```python
class Task(SQLModel, table=True):
    __tablename__ = "task"  # Note: singular table name

    id: UUID = Field(primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = None
    is_completed: bool = Field(default=False)
    priority: str = Field(default="medium")  # low, medium, high
    tags: Optional[str] = None  # comma-separated
    created_at: datetime
    updated_at: datetime
```

**Indexes**:
- PRIMARY KEY (id)
- INDEX (user_id, created_at) - optimize "get user's tasks, ordered by recency"

---

## Phase-III Tables

### Conversations Table

**Purpose**: Store chat sessions between users and AI chatbot

**Schema**:
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(max_length=255)
    metadata: Optional[dict[str, Any]] = None  # JSONB: tags, settings, etc.
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None  # Soft delete
```

**Indexes**:
- PRIMARY KEY (id)
- INDEX (user_id, created_at) - optimize "get conversations for user, ordered by recency"
- INDEX (user_id, deleted_at) - optimize "get active conversations for user"
- INDEX (user_id) - explicit index for foreign key lookup

**Foreign Keys**:
- user_id → users.id (CASCADE DELETE)

**Metadata Examples**:
```python
{
    "tags": ["important", "project-a"],
    "model": "gpt-4-turbo",
    "system_prompt_version": 2,
    "conversation_mode": "task-creation"
}
```

### Messages Table

**Purpose**: Store individual messages within conversations

**Schema**:
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    role: MessageRole = Field()  # user, assistant, system
    content: str = Field()  # Text content
    tool_calls: Optional[dict[str, Any]] = None  # JSONB
    tool_results: Optional[dict[str, Any]] = None  # JSONB
    metadata: Optional[dict[str, Any]] = None  # JSONB
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None  # Soft delete
```

**Indexes**:
- PRIMARY KEY (id)
- INDEX (conversation_id, created_at) - "get messages in conversation, ordered by recency"
- INDEX (user_id, created_at) - "get all user's messages, ordered by recency"
- INDEX (conversation_id, deleted_at) - "filter active messages in conversation"
- INDEX (conversation_id) - explicit foreign key lookup
- INDEX (user_id) - explicit foreign key lookup
- INDEX (role) - "get messages by role (user vs assistant)"

**Foreign Keys**:
- conversation_id → conversations.id (CASCADE DELETE)
- user_id → users.id (CASCADE DELETE)

**MessageRole Enum**:
```python
class MessageRole(str, Enum):
    USER = "user"        # Human user message
    ASSISTANT = "assistant"  # AI assistant response
    SYSTEM = "system"    # System/context message
```

**tool_calls Example** (OpenAI Agents SDK):
```python
{
    "tool_call_id": "call_abc123xyz",
    "function": {
        "name": "add_task",
        "arguments": {
            "title": "Buy groceries",
            "description": "Weekly shopping"
        }
    }
}
```

**tool_results Example** (MCP execution):
```python
{
    "tool_call_id": "call_abc123xyz",
    "status": "success",
    "result": {
        "task_id": "uuid-here",
        "title": "Buy groceries",
        "created_at": "2026-02-07T10:30:00Z"
    }
}
```

**metadata Example**:
```python
{
    "embedding_tokens": 150,
    "reasoning_trace": "...",
    "correlation_id": "conv-msg-123",
    "model_used": "gpt-4-turbo",
    "response_latency_ms": 1250
}
```

---

## User Isolation and Data Scoping

### The Golden Rule

**ALWAYS filter queries by the authenticated user_id**

### Why User Isolation?

- **Security**: Prevent users from accessing each other's data
- **Privacy**: Ensure data confidentiality in multi-tenant system
- **Compliance**: Meet GDPR and data protection regulations
- **Audit Trail**: Enable user-scoped forensics

### Implementing User Isolation

Every query MUST include a WHERE clause filtering by user_id:

```python
# ✅ CORRECT: Query filtered by user_id
async def get_user_conversations(
    session: AsyncSession,
    user_id: UUID
) -> list[Conversation]:
    """Get conversations for specific user only."""
    stmt = select(Conversation).where(
        Conversation.user_id == user_id,
        Conversation.deleted_at.is_(None)  # Also exclude soft-deleted
    )
    result = await session.execute(stmt)
    return result.scalars().all()

# ❌ WRONG: Query without user_id filter (SECURITY ISSUE!)
async def get_all_conversations(session: AsyncSession) -> list[Conversation]:
    """Dangerous: Returns all conversations for all users!"""
    stmt = select(Conversation)
    result = await session.execute(stmt)
    return result.scalars().all()  # Data leak!
```

### Application-Level Enforcement (Until RLS is Added)

**All FastAPI endpoints must**:
1. Extract user_id from JWT token
2. Pass user_id to all database queries
3. Verify result.user_id == authenticated_user_id before returning
4. Return 403 Forbidden (not 404) if cross-user access attempted

```python
@router.get("/api/v1/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: UUID,
    session: AsyncSession = Depends(get_session),
    user_id: UUID = Depends(get_user_from_jwt),  # Extract from token
):
    """Get a specific conversation."""
    stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,  # MUST filter by authenticated user
    )
    result = await session.execute(stmt)
    conversation = result.scalar_one_or_none()

    if not conversation:
        # Return 403 (not 404) to avoid leaking resource existence
        raise HTTPException(status_code=403, detail="Access denied")

    return conversation
```

### Row-Level Security (RLS) - Future Enhancement

PostgreSQL supports Row-Level Security policies for database-level enforcement:

```sql
-- Enable RLS on conversations table
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- Create policy: users can only see their own conversations
CREATE POLICY conversations_isolation ON conversations
    FOR ALL
    USING (user_id = current_user_id());  -- Function to extract from JWT

-- Create policy: users can only see their own messages
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY messages_isolation ON messages
    FOR ALL
    USING (user_id = current_user_id());
```

---

## Soft Delete Strategy

### Why Soft Deletes?

- **Audit Trail**: Preserve data for compliance and forensics
- **Recovery**: Recover accidentally deleted data
- **Traceability**: Track when data was deleted and by whom
- **Relationships**: Avoid orphaned foreign key references

### Implementation

**Soft Delete Column**: `deleted_at: Optional[datetime] = None`

- NULL (default) = record is active
- Non-null timestamp = record was deleted at this time

### Querying with Soft Deletes

**Always exclude soft-deleted records in queries**:

```python
# ✅ CORRECT: Exclude soft-deleted records
async def get_active_conversations(
    session: AsyncSession,
    user_id: UUID
) -> list[Conversation]:
    """Get active conversations for user (exclude deleted)."""
    stmt = select(Conversation).where(
        Conversation.user_id == user_id,
        Conversation.deleted_at.is_(None),  # Only active
    )
    result = await session.execute(stmt)
    return result.scalars().all()

# ❌ WRONG: Includes deleted records
async def get_conversations_unsafe(
    session: AsyncSession,
    user_id: UUID
) -> list[Conversation]:
    """Bug: Returns deleted conversations too!"""
    stmt = select(Conversation).where(Conversation.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().all()  # Includes deleted_at != NULL
```

### Soft Delete vs Hard Delete

**Soft Delete** (use for conversations/messages):
```python
# Soft delete: set deleted_at timestamp
conversation.deleted_at = datetime.utcnow()
session.add(conversation)
await session.commit()
```

**Hard Delete** (use sparingly, only for GDPR "right to be forgotten"):
```python
# Hard delete: remove from database completely
await session.delete(conversation)
await session.commit()
```

### Restoring Soft-Deleted Records

```python
# Restore a soft-deleted conversation
conversation.deleted_at = None
session.add(conversation)
await session.commit()
```

---

## Index Strategy and Query Performance

### Index Design Principles

1. **Avoid N+1 Queries**: Use eager loading with `selectinload()`
2. **Composite Indexes**: Index common query patterns (e.g., user_id + created_at)
3. **Covering Indexes**: Include all columns needed by query without table lookup
4. **Write Trade-offs**: More indexes = slower writes, faster reads

### Phase-III Indexes

#### Conversations Table Indexes

| Index | Columns | Purpose | Query Pattern |
|-------|---------|---------|---------------|
| PRIMARY KEY | id | Unique identification | Get conversation by ID |
| ix_conversations_user_id_created_at | (user_id, created_at) | **Primary** - list user's conversations | "Get conversations for user, ordered by recency" |
| ix_conversations_user_id_deleted_at | (user_id, deleted_at) | Filter active conversations | "Get active conversations for user" |
| ix_conversations_user_id | (user_id) | Foreign key lookup | Join on user_id |

#### Messages Table Indexes

| Index | Columns | Purpose | Query Pattern |
|-------|---------|---------|---------------|
| PRIMARY KEY | id | Unique identification | Get message by ID |
| ix_messages_conversation_id_created_at | (conversation_id, created_at) | **Primary** - list conversation messages | "Get messages in conversation, ordered by recency" |
| ix_messages_user_id_created_at | (user_id, created_at) | List user's messages across conversations | "Get all messages sent by user, ordered by recency" |
| ix_messages_conversation_id_deleted_at | (conversation_id, deleted_at) | Filter active messages | "Get active messages in conversation" |
| ix_messages_conversation_id | (conversation_id) | Foreign key lookup | Join on conversation_id |
| ix_messages_user_id | (user_id) | Foreign key lookup | Join on user_id |
| ix_messages_role | (role) | Filter by message role | "Get assistant messages vs user messages" |

### Example: Query Plan Analysis

**Query**: Get last 50 messages in a conversation, ordered by recency

```python
stmt = select(Message).where(
    Message.conversation_id == conversation_id,
    Message.deleted_at.is_(None)
).order_by(Message.created_at.desc()).limit(50)
```

**Expected Plan** (with index ix_messages_conversation_id_created_at):
```
Index Scan using ix_messages_conversation_id_created_at (...)
  Index Cond: (conversation_id = $1 AND deleted_at IS NULL)
  -> Sort (Limit) -> 50 rows returned
Execution time: < 50ms (for typical conversation)
```

**Without Index** (Table Scan - SLOW):
```
Seq Scan on messages
  Filter: (conversation_id = $1 AND deleted_at IS NULL)
Execution time: 500ms+ (for large tables)
```

### Performance Baselines

**Target Performance**:
- Single message fetch: < 10ms
- Get 50 messages in conversation: < 50ms
- List 20 conversations for user: < 100ms
- Soft delete filtering: < 5ms overhead

**Measured at**:
- Table size: 1M+ messages
- Database: Neon PostgreSQL
- Connection pool: NullPool (serverless)

---

## Example Queries

### Conversations

#### Create a Conversation

```python
from datetime import datetime
from uuid import uuid4

async def create_conversation(
    session: AsyncSession,
    user_id: UUID,
    title: str,
    metadata: Optional[dict] = None
) -> Conversation:
    """Create a new conversation for a user."""
    conversation = Conversation(
        id=uuid4(),
        user_id=user_id,
        title=title,
        metadata=metadata,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        deleted_at=None,  # Active by default
    )
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation
```

#### List Conversations for User

```python
async def list_user_conversations(
    session: AsyncSession,
    user_id: UUID,
    limit: int = 20,
    offset: int = 0
) -> list[Conversation]:
    """List active conversations for a user, ordered by recency."""
    stmt = select(Conversation).where(
        Conversation.user_id == user_id,
        Conversation.deleted_at.is_(None),  # Only active
    ).order_by(
        Conversation.created_at.desc()  # Most recent first
    ).limit(limit).offset(offset)

    result = await session.execute(stmt)
    return result.scalars().all()
```

#### Get Conversation by ID (with User Check)

```python
async def get_conversation(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: UUID
) -> Optional[Conversation]:
    """Get a specific conversation (user isolation enforced)."""
    stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,  # MUST verify ownership
        Conversation.deleted_at.is_(None),
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
```

#### Update Conversation

```python
async def update_conversation(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: UUID,
    title: Optional[str] = None,
    metadata: Optional[dict] = None
) -> Optional[Conversation]:
    """Update conversation title or metadata."""
    conversation = await get_conversation(
        session, conversation_id, user_id
    )
    if not conversation:
        return None

    if title is not None:
        conversation.title = title
    if metadata is not None:
        conversation.metadata = metadata
    conversation.updated_at = datetime.utcnow()

    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation
```

#### Soft Delete Conversation

```python
async def soft_delete_conversation(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: UUID
) -> Optional[Conversation]:
    """Soft delete a conversation (preserves data for audit)."""
    conversation = await get_conversation(
        session, conversation_id, user_id
    )
    if not conversation:
        return None

    conversation.deleted_at = datetime.utcnow()
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation
```

### Messages

#### Create a Message

```python
async def create_message(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: UUID,
    role: MessageRole,
    content: str,
    tool_calls: Optional[dict] = None,
    tool_results: Optional[dict] = None,
    metadata: Optional[dict] = None
) -> Message:
    """Create a new message in a conversation."""
    message = Message(
        id=uuid4(),
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
        tool_calls=tool_calls,
        tool_results=tool_results,
        metadata=metadata,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        deleted_at=None,  # Active by default
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message
```

#### List Messages in Conversation

```python
async def list_conversation_messages(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: UUID,  # Verify user owns conversation
    limit: int = 50
) -> list[Message]:
    """List messages in a conversation, ordered by creation time."""
    # Verify user owns this conversation first
    conversation = await get_conversation(
        session, conversation_id, user_id
    )
    if not conversation:
        raise ValueError("Conversation not found or access denied")

    stmt = select(Message).where(
        Message.conversation_id == conversation_id,
        Message.deleted_at.is_(None),  # Only active
    ).order_by(
        Message.created_at.asc()  # Oldest first (chronological)
    ).limit(limit)

    result = await session.execute(stmt)
    return result.scalars().all()
```

#### Get Messages by Role

```python
async def list_conversation_messages_by_role(
    session: AsyncSession,
    conversation_id: UUID,
    user_id: UUID,
    role: MessageRole
) -> list[Message]:
    """Get messages of specific role (user vs assistant) in conversation."""
    conversation = await get_conversation(
        session, conversation_id, user_id
    )
    if not conversation:
        raise ValueError("Conversation not found or access denied")

    stmt = select(Message).where(
        Message.conversation_id == conversation_id,
        Message.role == role,
        Message.deleted_at.is_(None),
    ).order_by(Message.created_at.asc())

    result = await session.execute(stmt)
    return result.scalars().all()
```

---

## Best Practices

### 1. Always Enforce User Isolation

```python
# ✅ DO THIS
stmt = select(Conversation).where(
    Conversation.id == conv_id,
    Conversation.user_id == authenticated_user_id,  # Enforce ownership
)

# ❌ NEVER DO THIS
stmt = select(Conversation).where(Conversation.id == conv_id)
```

### 2. Always Exclude Soft-Deleted Records

```python
# ✅ DO THIS
stmt = select(Message).where(
    Message.conversation_id == conv_id,
    Message.deleted_at.is_(None),  # Exclude deleted
)

# ❌ NEVER DO THIS
stmt = select(Message).where(Message.conversation_id == conv_id)
```

### 3. Use Eager Loading to Avoid N+1 Queries

```python
from sqlalchemy.orm import selectinload

# ✅ DO THIS: Fetch conversation and related messages in one query
stmt = select(Conversation).where(
    Conversation.id == conv_id,
    Conversation.user_id == user_id
).options(selectinload(Conversation.messages))

# ❌ NEVER DO THIS: Loop causes N+1 problem
conversations = [...]  # Fetch conversations
for conv in conversations:
    messages = conv.messages  # Triggers query for EACH conversation
```

### 4. Use Bulk Operations for Performance

```python
# ✅ DO THIS: Bulk insert
messages = [Message(...) for _ in range(100)]
session.add_all(messages)
await session.commit()

# ❌ SLOW: Insert one at a time
for msg in messages:
    session.add(msg)
    await session.commit()  # Commits N times!
```

### 5. Index Your Common Query Patterns

```python
# ✅ If you often query "get messages for conversation ordered by creation"
# Create INDEX: (conversation_id, created_at)

# ✅ If you often query "get user's conversations ordered by recency"
# Create INDEX: (user_id, created_at)
```

### 6. Use Connection Pooling Appropriately

```python
# For Neon serverless (NullPool - no persistent connections):
engine = create_async_engine(
    settings.database_url,
    poolclass=NullPool,  # Create new connection each time
)

# For traditional PostgreSQL (QueuePool - connection reuse):
engine = create_async_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=5,      # Keep 5 connections open
    max_overflow=10,  # Allow up to 10 temporary connections
)
```

---

## Performance Considerations

### Query Optimization Tips

1. **Use EXPLAIN ANALYZE** to verify index usage:
   ```python
   result = await session.execute(text(
       "EXPLAIN ANALYZE SELECT * FROM conversations WHERE user_id = ?"
   ))
   ```

2. **Monitor slow queries** (> 200ms):
   - Add database logging to identify bottlenecks
   - Check for missing indexes
   - Look for N+1 query problems

3. **Pagination** for large result sets:
   ```python
   stmt = select(Message).where(...).limit(50).offset(offset)
   ```

4. **Caching** for frequently accessed data:
   - Cache conversation list (refresh on new message)
   - Cache recent messages (cache invalidation needed)
   - Use Redis or in-memory cache for speed

### Connection Pool Tuning

**Neon Serverless** (recommended):
- poolclass=NullPool (no persistent connections)
- Each request creates new connection
- Auto-scaling handled by Neon

**Traditional PostgreSQL**:
- pool_size=5 (initial connections)
- max_overflow=10 (additional connections)
- pool_recycle=3600 (reset connections after 1 hour)

### Monitoring Metrics

Track these metrics for performance health:
- Query response time (p50, p95, p99)
- Database connection count
- Index usage statistics
- Slow query log (queries > 1 second)

---

## Schema Evolution

### Adding a New Column

1. **Create Alembic migration**:
   ```python
   def upgrade():
       op.add_column('conversations', sa.Column('new_field', sa.String))

   def downgrade():
       op.drop_column('conversations', 'new_field')
   ```

2. **Update SQLModel**:
   ```python
   class Conversation(SQLModel, table=True):
       new_field: Optional[str] = None
   ```

3. **Test migration**:
   ```bash
   alembic upgrade head  # Test upgrade
   alembic downgrade base  # Test downgrade
   ```

### Adding a New Index

```python
def upgrade():
    op.create_index(
        'ix_conversations_metadata',
        'conversations',
        ['metadata'],
        postgresql_using='gin'  # GIN index for JSONB
    )

def downgrade():
    op.drop_index('ix_conversations_metadata')
```

---

## References

- **Spec**: specs/004-ai-chatbot/spec.md
- **Architecture Plan**: specs/004-ai-chatbot/plan.md
- **Migrations**: backend/alembic/versions/
- **Models**: backend/src/models/
- **Tests**: backend/tests/unit/test_user_isolation.py

---

**Last Updated**: 2026-02-07
**Author**: Database Architect
**Review Status**: Ready for Development
