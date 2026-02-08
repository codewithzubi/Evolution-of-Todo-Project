# Phase-III Database Schema and Migration Guide

## Table of Contents

1. [Overview](#overview)
2. [Entity-Relationship Diagram](#entity-relationship-diagram)
3. [Table Schemas](#table-schemas)
4. [Soft Delete Strategy](#soft-delete-strategy)
5. [Indexes and Performance](#indexes-and-performance)
6. [Foreign Key Relationships](#foreign-key-relationships)
7. [Migration Guide](#migration-guide)
8. [Common Queries](#common-queries)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This document describes the Phase-III database schema for the AI Todo Chatbot application. The schema extends Phase-II (Task Management) with conversation persistence and message history storage.

**Key Features**:
- User-scoped conversations and messages (multi-tenant isolation)
- Soft deletes for audit trail preservation
- Optimized indexes for query performance
- JSONB columns for flexible metadata storage
- Async-friendly schema design for Neon serverless PostgreSQL

**Database**: Neon PostgreSQL
**ORM**: SQLModel (Pydantic + SQLAlchemy)
**Migrations**: Alembic

---

## Entity-Relationship Diagram

```
┌─────────────┐
│    users    │  (Phase-II)
│ (PK: id)    │
└──────┬──────┘
       │
       ├─── 1:N ──→ ┌──────────────┐
       │            │    tasks     │  (Phase-II)
       │            │ (PK: id)     │
       │            └──────────────┘
       │
       ├─── 1:N ──→ ┌──────────────────────┐
       │            │  conversations       │  (Phase-III)
       │            │  (PK: id)            │
       │            │  (FK: user_id)       │
       │            │  (Indexes: user_id)  │
       │            └──────────┬───────────┘
       │                       │
       │                       ├─── 1:N ──→ ┌──────────────────────┐
       │                       │            │    messages          │  (Phase-III)
       │                       │            │    (PK: id)          │
       │                       │            │    (FK: conv_id)     │
       │                       │            │    (FK: user_id)     │
       │                       │            │    (Indexes: multi)  │
       │                       │            └──────────────────────┘
       │                       │
       └──────────────────────┘  (Cascade Delete)
```

**Legend**:
- `PK`: Primary Key
- `FK`: Foreign Key
- `1:N`: One-to-Many Relationship
- Cascade Delete: Deleting user/conversation cascades to related records

---

## Table Schemas

### Phase-II Tables (Unchanged)

#### users table

| Column | Type | Constraints | Index | Notes |
|--------|------|-------------|-------|-------|
| id | UUID | PRIMARY KEY | YES | Generated UUID |
| email | VARCHAR(255) | UNIQUE NOT NULL | YES | Login identifier |
| name | VARCHAR(255) | NOT NULL | NO | User display name |
| password_hash | VARCHAR(255) | NOT NULL | NO | Hashed password |
| image | VARCHAR(2048) | | NO | Profile image URL |
| email_verified | BOOLEAN | DEFAULT false | NO | Email confirmation status |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NO | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NO | Last update timestamp |

**Indexes**:
- `PRIMARY KEY (id)`
- `UNIQUE (email)`

**Foreign Key References**:
- tasks.user_id → users.id (CASCADE DELETE)
- conversations.user_id → users.id (CASCADE DELETE)
- messages.user_id → users.id (CASCADE DELETE)

#### task table

| Column | Type | Constraints | Index | Notes |
|--------|------|-------------|-------|-------|
| id | UUID | PRIMARY KEY | YES | Generated UUID |
| user_id | UUID | FOREIGN KEY, NOT NULL | YES | Owner of task |
| title | VARCHAR(255) | NOT NULL | NO | Task title |
| description | TEXT | | NO | Detailed description |
| is_completed | BOOLEAN | DEFAULT false | NO | Completion status |
| priority | VARCHAR(10) | DEFAULT 'medium' | NO | low/medium/high |
| tags | VARCHAR(500) | | NO | Comma-separated tags |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NO | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NO | Last update timestamp |

**Indexes**:
- `PRIMARY KEY (id)`
- `FOREIGN KEY (user_id) → users.id`
- `INDEX (user_id, created_at)`

---

### Phase-III Tables (New)

#### conversations table

**Purpose**: Store chat sessions between users and AI chatbot

| Column | Type | Constraints | Index | Notes |
|--------|------|-------------|-------|-------|
| id | UUID | PRIMARY KEY | YES | Generated UUID |
| user_id | UUID | FOREIGN KEY, NOT NULL | YES | Conversation owner |
| title | VARCHAR(255) | | NO | User-friendly name |
| metadata | JSONB | | NO | Configuration, tags, settings |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NO | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NO | Last update timestamp |
| deleted_at | TIMESTAMP WITH TIME ZONE | | NO | Soft delete marker |

**Indexes**:
- `PRIMARY KEY (id)`
- `FOREIGN KEY (user_id) → users.id CASCADE DELETE`
- `COMPOSITE (user_id, created_at)` - Primary query pattern
- `COMPOSITE (user_id, deleted_at)` - Active conversations filter
- `SIMPLE (user_id)` - Foreign key lookup

**Data Type Details**:
- `id`: Auto-generated UUID v4
- `user_id`: Foreign key to users.id (enforces user ownership)
- `title`: Optional conversation name (e.g., "Project Planning", "Bug Fix")
- `metadata`: JSONB for flexible storage (tags, model params, conversation mode)
- `deleted_at`: NULL = active, non-NULL = soft-deleted at this timestamp

**Metadata Examples**:
```json
{
  "tags": ["important", "project-a"],
  "conversation_mode": "task-creation",
  "model": "gpt-4-turbo",
  "system_prompt_version": 2,
  "archived": false
}
```

#### messages table

**Purpose**: Store individual messages within conversations

| Column | Type | Constraints | Index | Notes |
|--------|------|-------------|-------|-------|
| id | UUID | PRIMARY KEY | YES | Generated UUID |
| conversation_id | UUID | FOREIGN KEY, NOT NULL | YES | Belongs to conversation |
| user_id | UUID | FOREIGN KEY, NOT NULL | YES | Message sender |
| role | VARCHAR(20) | NOT NULL | YES | user/assistant/system |
| content | TEXT | NOT NULL | NO | Message body |
| tool_calls | JSONB | | NO | OpenAI tool calls |
| tool_results | JSONB | | NO | MCP tool execution results |
| metadata | JSONB | | NO | Tracing, tokens, etc. |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NO | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NO | Last update timestamp |
| deleted_at | TIMESTAMP WITH TIME ZONE | | NO | Soft delete marker |

**Indexes**:
- `PRIMARY KEY (id)`
- `FOREIGN KEY (conversation_id) → conversations.id CASCADE DELETE`
- `FOREIGN KEY (user_id) → users.id CASCADE DELETE`
- `COMPOSITE (conversation_id, created_at)` - List messages in conversation
- `COMPOSITE (user_id, created_at)` - List user's messages
- `COMPOSITE (conversation_id, deleted_at)` - Filter active messages
- `SIMPLE (conversation_id)` - Foreign key lookup
- `SIMPLE (user_id)` - Foreign key lookup
- `SIMPLE (role)` - Filter by message role

**Data Type Details**:
- `id`: Auto-generated UUID v4
- `conversation_id`: Foreign key to conversations.id (enables cascade delete)
- `user_id`: Foreign key to users.id (optimizes user-scoped queries)
- `role`: ENUM-like VARCHAR(20) - 'user', 'assistant', 'system'
- `content`: TEXT (no size limit for message body)
- `tool_calls`: JSONB (OpenAI Agents SDK format)
- `tool_results`: JSONB (MCP tool execution output)
- `metadata`: JSONB (embedding tokens, tracing, correlation IDs)
- `deleted_at`: NULL = active, non-NULL = soft-deleted

**Role Values**:
- `'user'`: Message from human user
- `'assistant'`: Message from AI assistant
- `'system'`: System message (context, instructions, error messages)

**tool_calls Example** (when assistant invokes a tool):
```json
{
  "tool_call_id": "call_abc123xyz",
  "function": {
    "name": "add_task",
    "arguments": {
      "title": "Buy groceries",
      "description": "Weekly shopping",
      "priority": "medium"
    }
  }
}
```

**tool_results Example** (when MCP tool executes):
```json
{
  "tool_call_id": "call_abc123xyz",
  "status": "success",
  "result": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "created_at": "2026-02-07T10:30:00Z"
  }
}
```

**metadata Example** (for debugging and tracing):
```json
{
  "embedding_tokens": 150,
  "completion_tokens": 50,
  "reasoning_trace": "User wants to create a task...",
  "correlation_id": "req-12345-abcde",
  "model_used": "gpt-4-turbo",
  "response_latency_ms": 1250
}
```

---

## Soft Delete Strategy

### Why Soft Deletes?

**Benefits**:
- **Audit Trail**: Preserve data for compliance and forensics
- **Accident Recovery**: Restore accidentally deleted conversations/messages
- **Traceability**: Know when and what was deleted
- **Data Integrity**: Avoid cascading orphaned records

**Drawbacks**:
- All queries must exclude soft-deleted records (extra WHERE clause)
- Database size grows with deleted data
- Recovery requires manual intervention

### Implementation

**Soft Delete Column**: `deleted_at: TIMESTAMP WITH TIME ZONE`
- `NULL` (default) = record is active
- Non-null timestamp = record was deleted at this time

### Querying with Soft Deletes

**Always filter out soft-deleted records**:

```sql
-- ✅ CORRECT: Get active conversations for user
SELECT * FROM conversations
WHERE user_id = $1
  AND deleted_at IS NULL
ORDER BY created_at DESC;

-- ❌ WRONG: Includes deleted conversations
SELECT * FROM conversations
WHERE user_id = $1
ORDER BY created_at DESC;
```

### Soft Delete vs Hard Delete

| Operation | Use Case | SQL | Recoverable |
|-----------|----------|-----|-------------|
| **Soft Delete** | Normal deletion (conversations, messages) | `UPDATE ... SET deleted_at = NOW()` | Yes |
| **Hard Delete** | GDPR "right to be forgotten" or data cleanup | `DELETE FROM ...` | No |

### Hard Delete Examples

```sql
-- Hard delete: Permanently remove conversation and all messages
BEGIN;
DELETE FROM messages WHERE conversation_id = $1;
DELETE FROM conversations WHERE id = $1;
COMMIT;

-- Hard delete: Purge old deleted conversations (30 days+)
DELETE FROM conversations
WHERE deleted_at IS NOT NULL
  AND deleted_at < NOW() - INTERVAL '30 days';
```

### Restoring Soft-Deleted Records

```sql
-- Restore a soft-deleted conversation
UPDATE conversations
SET deleted_at = NULL
WHERE id = $1
  AND user_id = $2;

-- Restore all soft-deleted messages in a conversation
UPDATE messages
SET deleted_at = NULL
WHERE conversation_id = $1
  AND user_id = $2
  AND deleted_at IS NOT NULL;
```

---

## Indexes and Performance

### Index Design Strategy

**Principles**:
1. Index the columns used in WHERE clauses
2. Use composite indexes for common query combinations
3. Avoid over-indexing (trade-off: slower writes, faster reads)
4. Monitor index usage with EXPLAIN ANALYZE

### Phase-III Indexes

#### Conversations Table

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| conversations_pkey | id | PRIMARY KEY | Unique identification |
| ix_conversations_user_id_created_at | (user_id, created_at) | BTREE | **Primary**: List user's conversations |
| ix_conversations_user_id_deleted_at | (user_id, deleted_at) | BTREE | Filter active conversations |
| ix_conversations_user_id | (user_id) | BTREE | Foreign key lookup |

#### Messages Table

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| messages_pkey | id | PRIMARY KEY | Unique identification |
| ix_messages_conversation_id_created_at | (conversation_id, created_at) | BTREE | **Primary**: List messages in conversation |
| ix_messages_user_id_created_at | (user_id, created_at) | BTREE | List all user's messages |
| ix_messages_conversation_id_deleted_at | (conversation_id, deleted_at) | BTREE | Filter active messages |
| ix_messages_conversation_id | (conversation_id) | BTREE | Foreign key lookup |
| ix_messages_user_id | (user_id) | BTREE | Foreign key lookup |
| ix_messages_role | (role) | BTREE | Filter by message role |

### Query Performance Baselines

**Expected Performance** (with proper indexes):

| Query | Expected Time | Table Size |
|-------|--------------|-----------|
| Get single message by ID | < 10ms | 1M+ messages |
| Get 50 messages in conversation | < 50ms | 1M+ messages |
| List 20 conversations for user | < 100ms | 100K+ conversations |
| Get messages by role in conversation | < 30ms | 1M+ messages |
| Soft delete filter overhead | < 5ms | 1M+ records |

### EXPLAIN ANALYZE Examples

**Query**: Get last 50 messages in a conversation, ordered by recency

```sql
EXPLAIN ANALYZE
SELECT * FROM messages
WHERE conversation_id = $1
  AND deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 50;

-- Output (with index ix_messages_conversation_id_created_at):
--
-- Index Scan using ix_messages_conversation_id_created_at (...)
--   Index Cond: (conversation_id = $1 AND deleted_at IS NULL)
--   -> Limit (cost=0.42..8.43 rows=50 width=...)
-- Execution time: 15.245 ms
--
-- ✅ GOOD: Uses index, fast execution
```

**Query (without index on deleted_at)**:

```sql
-- Would use sequential scan (BAD):
-- Seq Scan on messages (cost=0.00..45678.90 rows=500 width=...)
--   Filter: (conversation_id = $1 AND deleted_at IS NULL)
-- Execution time: 523.456 ms
--
-- ❌ SLOW: Table scan for 1M+ rows
```

### Monitoring Index Health

```sql
-- Find unused indexes
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
  AND idx_scan = 0  -- Not used
ORDER BY idx_blks_hit DESC;

-- Find index size and usage
SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Analyze query plan
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM conversations WHERE user_id = $1;
```

---

## Foreign Key Relationships

### users → conversations (1:N)

```
users.id ──(1:N)──→ conversations.user_id
```

**Constraint**: `FOREIGN KEY (conversations.user_id) REFERENCES users.id ON DELETE CASCADE`

**Behavior**:
- When a user is deleted, all their conversations are deleted
- When a conversation is deleted, all related messages are deleted (cascade)

### users → messages (1:N)

```
users.id ──(1:N)──→ messages.user_id
```

**Constraint**: `FOREIGN KEY (messages.user_id) REFERENCES users.id ON DELETE CASCADE`

**Behavior**:
- When a user is deleted, all their messages are deleted
- Prevents orphaned messages

### conversations → messages (1:N)

```
conversations.id ──(1:N)──→ messages.conversation_id
```

**Constraint**: `FOREIGN KEY (messages.conversation_id) REFERENCES conversations.id ON DELETE CASCADE`

**Behavior**:
- When a conversation is deleted, all its messages are deleted
- Prevents orphaned messages

### Cascade Delete Sequence

When a user is deleted:
1. User deletion triggers CASCADE on conversations
2. Each conversation deletion triggers CASCADE on messages
3. All related data removed in atomic transaction

```sql
-- Example: Delete user cascades to all related data
DELETE FROM users WHERE id = $1;
-- → Cascades to: conversations where user_id = $1
--   → Cascades to: messages where conversation_id in (those conversations)
```

---

## Migration Guide

### Prerequisites

- Neon PostgreSQL database set up
- Python 3.13+ installed
- Backend dependencies installed: `pip install -r requirements.txt`
- Alembic configured with database URL

### Initial Setup

1. **Set database URL**:
   ```bash
   export DATABASE_URL="postgresql://user:password@host/dbname?sslmode=require"
   ```

2. **Check Alembic configuration**:
   ```bash
   cat backend/alembic.ini | grep sqlalchemy.url
   ```

3. **Verify Alembic is installed**:
   ```bash
   python -m pip list | grep -i alembic
   ```

### Running Migrations

#### Upgrade to Latest Version

```bash
cd backend
python -m alembic upgrade head
```

**Output**:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl with target metadata
INFO  [alembic.runtime.migration] Alembic version table not created as default empty
INFO  [alembic.runtime.migration] Running upgrade  -> 001_remove_priority_and_tags, done
INFO  [alembic.runtime.migration] Running upgrade 001_remove_priority_and_tags -> 002_add_priority_and_tags_fields, done
INFO  [alembic.runtime.migration] Running upgrade 002_add_priority_and_tags_fields -> 003_create_conversations_and_messages_tables, done
```

#### Verify Migration

```bash
# Connect to database
psql $DATABASE_URL

# Check tables exist
\dt conversations messages

# Check table schema
\d conversations
\d messages

# Check indexes
\di conversations*
\di messages*
```

#### Rollback to Previous Version

```bash
# Rollback one migration
python -m alembic downgrade -1

# Rollback to specific revision
python -m alembic downgrade 002

# Rollback all migrations
python -m alembic downgrade base
```

### Creating New Migrations

```bash
# Generate a new migration file
python -m alembic revision --autogenerate -m "Add new_column to conversations"

# Edit the generated file
# vim alembic/versions/XXXX_add_new_column_to_conversations.py

# Run the migration
python -m alembic upgrade head
```

### Migration File Template

```python
"""Add new_column to conversations table."""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"

def upgrade():
    """Add new_column to conversations."""
    op.add_column(
        'conversations',
        sa.Column('new_column', sa.String(255), nullable=True)
    )

def downgrade():
    """Remove new_column from conversations."""
    op.drop_column('conversations', 'new_column')
```

### Testing Migrations

**In-Memory SQLite for Local Testing**:

```python
# backend/tests/test_migrations.py
import pytest
from alembic.config import Config
from alembic import command

@pytest.fixture
def alembic_config():
    config = Config("alembic.ini")
    config.set_main_option(
        "sqlalchemy.url",
        "sqlite:///:memory:"
    )
    return config

def test_migration_upgrade(alembic_config):
    command.upgrade(alembic_config, "head")
    # Verify tables exist
    # ...

def test_migration_downgrade(alembic_config):
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")
    # Verify tables removed
    # ...
```

---

## Common Queries

### Conversations

#### Create a New Conversation

```sql
INSERT INTO conversations (
  id, user_id, title, metadata, created_at, updated_at, deleted_at
) VALUES (
  gen_random_uuid(),
  $1,  -- user_id
  $2,  -- title
  $3,  -- metadata (JSONB)
  NOW(),
  NOW(),
  NULL
) RETURNING *;
```

#### List User's Conversations (Most Recent First)

```sql
SELECT * FROM conversations
WHERE user_id = $1
  AND deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;
```

#### Get Conversation by ID

```sql
SELECT * FROM conversations
WHERE id = $1
  AND user_id = $2  -- Enforce user ownership
  AND deleted_at IS NULL;
```

#### Update Conversation Title

```sql
UPDATE conversations
SET title = $1,
    updated_at = NOW()
WHERE id = $2
  AND user_id = $3
  AND deleted_at IS NULL
RETURNING *;
```

#### Soft Delete Conversation

```sql
UPDATE conversations
SET deleted_at = NOW(),
    updated_at = NOW()
WHERE id = $1
  AND user_id = $2
RETURNING *;
```

### Messages

#### Create a New Message

```sql
INSERT INTO messages (
  id, conversation_id, user_id, role, content,
  tool_calls, tool_results, metadata,
  created_at, updated_at, deleted_at
) VALUES (
  gen_random_uuid(),
  $1,  -- conversation_id
  $2,  -- user_id
  $3,  -- role ('user' | 'assistant' | 'system')
  $4,  -- content
  $5,  -- tool_calls (JSON or NULL)
  $6,  -- tool_results (JSON or NULL)
  $7,  -- metadata (JSON or NULL)
  NOW(),
  NOW(),
  NULL
) RETURNING *;
```

#### List Messages in Conversation

```sql
SELECT * FROM messages
WHERE conversation_id = $1
  AND deleted_at IS NULL
ORDER BY created_at ASC;
```

#### Get Last 50 Messages (Paginated)

```sql
SELECT * FROM messages
WHERE conversation_id = $1
  AND deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 50;
```

#### Get Messages by Role (User vs Assistant)

```sql
SELECT * FROM messages
WHERE conversation_id = $1
  AND role = $2  -- 'user' or 'assistant'
  AND deleted_at IS NULL
ORDER BY created_at ASC;
```

#### Get Messages with Tool Calls

```sql
SELECT * FROM messages
WHERE conversation_id = $1
  AND tool_calls IS NOT NULL
  AND deleted_at IS NULL
ORDER BY created_at ASC;
```

#### Soft Delete Message

```sql
UPDATE messages
SET deleted_at = NOW()
WHERE id = $1
  AND user_id = $2
RETURNING *;
```

---

## Troubleshooting

### Problem: "Duplicate Key Violation"

**Cause**: Attempting to insert a record with duplicate primary key or unique constraint

**Solution**:
```sql
-- Check for existing record
SELECT * FROM conversations WHERE id = $1;

-- Use INSERT ... ON CONFLICT for upsert
INSERT INTO conversations (id, user_id, ...)
VALUES (...)
ON CONFLICT (id) DO UPDATE SET
  title = EXCLUDED.title,
  updated_at = NOW();
```

### Problem: "Foreign Key Constraint Violation"

**Cause**: Inserting message with non-existent conversation_id or user_id

**Solution**:
```sql
-- Verify conversation exists
SELECT * FROM conversations WHERE id = $1 AND deleted_at IS NULL;

-- Verify user exists
SELECT * FROM users WHERE id = $1;

-- Then insert message with valid foreign keys
INSERT INTO messages (conversation_id, user_id, ...) VALUES ...;
```

### Problem: "Too Many Indexes - Slow Writes"

**Cause**: Excessive indexes slow down INSERT/UPDATE operations

**Solution**:
```sql
-- Review index usage
SELECT indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0  -- Unused indexes
ORDER BY pg_relation_size DESC LIMIT 10;

-- Drop unused indexes
DROP INDEX IF EXISTS ix_unused_index;
```

### Problem: "Query Timeout - Slow SELECT"

**Cause**: Missing indexes or table scan on large tables

**Solution**:
```sql
-- Use EXPLAIN ANALYZE to identify bottleneck
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM messages
WHERE conversation_id = $1
  AND deleted_at IS NULL;

-- Add missing index if needed
CREATE INDEX ix_messages_conv_id_deleted_at
ON messages (conversation_id, deleted_at)
WHERE deleted_at IS NULL;
```

### Problem: "Cascade Delete Failed"

**Cause**: Orphaned records or constraint violation during cascade

**Solution**:
```sql
-- Check for constraint violations
SELECT * FROM messages
WHERE conversation_id NOT IN (
  SELECT id FROM conversations
);

-- Remove orphaned records
DELETE FROM messages
WHERE conversation_id NOT IN (
  SELECT id FROM conversations
);

-- Then retry cascade delete
DELETE FROM conversations WHERE user_id = $1;
```

### Problem: "Soft Delete Records Still Appearing"

**Cause**: Query missing `deleted_at IS NULL` filter

**Solution**:
```sql
-- ✅ CORRECT: Always filter out deleted records
SELECT * FROM conversations
WHERE user_id = $1
  AND deleted_at IS NULL;

-- ❌ WRONG: Includes deleted records
SELECT * FROM conversations WHERE user_id = $1;
```

---

## References

- **Database Models**: backend/src/models/
  - conversation.py
  - message.py
  - user.py
  - base.py

- **Migrations**: backend/alembic/versions/
  - 001_remove_priority_and_tags.py
  - 002_add_priority_and_tags_fields.py
  - 003_create_conversations_and_messages_tables.py

- **ORM Guide**: backend/src/models/README.md

- **Specification**: specs/004-ai-chatbot/spec.md

- **Architecture Plan**: specs/004-ai-chatbot/plan.md

---

**Last Updated**: 2026-02-07
**Status**: Ready for Development
**Next Review**: After Phase-III Implementation Complete
