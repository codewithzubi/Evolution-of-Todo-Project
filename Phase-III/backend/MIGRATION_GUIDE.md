# Database Migration Guide

## Overview

This guide explains how to use Alembic migrations to manage database schema changes for the Task CRUD API.

## Background: Why Migrations?

During Phase 8 spec alignment, we removed non-spec fields (`priority` and `tags`) from the Task model:

- **Code Change**: Task model in `src/models/task.py` no longer has these fields
- **Schema Impact**: Any production databases still have these columns
- **Solution**: Use Alembic migrations to drop these columns from production databases

## Migration Structure

```
backend/
├── alembic/
│   ├── __init__.py
│   ├── env.py (Alembic runtime configuration)
│   ├── script.py.mako (Template for new migrations)
│   └── versions/
│       ├── __init__.py
│       └── 001_remove_priority_and_tags.py (First migration)
├── alembic.ini (Alembic config file)
└── src/
    ├── models/
    │   ├── task.py (SQLModel without priority/tags)
    │   └── user.py
    └── ...
```

## Current Migration Status

### Migration 001: Remove Priority and Tags

**File**: `alembic/versions/001_remove_priority_and_tags.py`

**What it does**:
- Drops the `priority` column from the `task` table
- Drops the `tags` column from the `task` table
- Includes rollback capability to restore columns if needed

**When to run**:
- ✅ **NEW databases**: Not needed (schema is created fresh without these columns)
- ✅ **DEVELOPMENT**: Not needed (tests use in-memory SQLite)
- ⚠️ **PRODUCTION**: **REQUIRED** - drops columns from existing databases

## How to Run Migrations

### Option 1: Using Alembic CLI (Recommended)

First, ensure Alembic is installed:
```bash
pip install alembic==1.13.0
```

Then run migrations:
```bash
# Change to backend directory
cd backend

# Show migration history
alembic history

# Check current revision
alembic current

# Upgrade to latest migration
alembic upgrade head

# Upgrade to specific revision
alembic upgrade 001

# Downgrade to previous revision (CAUTION: loses data)
alembic downgrade -1

# Downgrade to specific revision (CAUTION: loses data)
alembic downgrade 000
```

### Option 2: Programmatic Migration (Python)

For automated deployments, you can run migrations from Python:

```python
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def run_migrations(database_url: str):
    """Run all pending migrations."""
    # Create async engine
    engine = create_async_engine(database_url)

    # Get Alembic config
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)

    # Run migrations
    async with engine.begin() as connection:
        await connection.run_sync(lambda connection: _run_alembic_migrations(connection, config))

    await engine.dispose()

def _run_alembic_migrations(connection, config):
    """Run Alembic migrations synchronously within async context."""
    context = MigrationContext.configure(connection)
    operations = Operations(context)

    # Get current revision
    script = ScriptDirectory.from_config(config)

    # Get all migrations
    heads = script.get_heads()
    for head in heads:
        # Run migration
        from alembic.runtime.environment import EnvironmentContext
        env_context = EnvironmentContext(config, script)
        env_context.configure(connection)
        env_context.run_migrations()

# Run migrations
# asyncio.run(run_migrations("postgresql+asyncpg://user:password@localhost/dbname"))
```

## Testing Migrations

### Local Development (SQLite)

```bash
# Run migrations on local SQLite database
DATABASE_URL="sqlite:///./test.db" alembic upgrade head

# Verify migration
sqlite3 test.db "SELECT sql FROM sqlite_master WHERE type='table' AND name='task';"
```

### Staging/Production (PostgreSQL)

```bash
# Create backup before migration
pg_dump your_database > backup_$(date +%Y%m%d_%H%M%S).sql

# Run migrations
DATABASE_URL="postgresql+asyncpg://user:password@host:5432/dbname" alembic upgrade head

# Verify migration
psql -c "SELECT column_name FROM information_schema.columns WHERE table_name='task' ORDER BY ordinal_position;"
```

## Migration Checklist

Before running migrations in production:

- [ ] **Backup**: Create full database backup
- [ ] **Test**: Run migrations on staging environment first
- [ ] **Verify**: Confirm priority and tags columns are removed
- [ ] **Rollback Plan**: Have downgrade command ready if needed
- [ ] **Monitoring**: Watch logs for errors after deployment
- [ ] **Client Check**: Verify no API clients are sending priority/tags

## Verification After Migration

### Check Columns Removed (PostgreSQL)

```sql
SELECT column_name
FROM information_schema.columns
WHERE table_name='task'
ORDER BY ordinal_position;
```

Expected output should NOT include `priority` or `tags`:
```
        column_name
--------------------------
 id
 created_at
 updated_at
 user_id
 title
 description
 due_date
 completed
 completed_at
(9 rows)
```

### Check Columns Removed (SQLite)

```sql
PRAGMA table_info(task);
```

### Verify Application Works

```bash
# Run health check
curl http://localhost:8000/health

# Test create endpoint
curl -X POST http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task"}'

# Test list endpoint
curl -X GET http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer <token>"
```

## Troubleshooting

### Migration Fails: Column Doesn't Exist

If you see an error like "column 'priority' does not exist":

**Cause**: The database schema was already updated or never had these columns.

**Solution**:
- This is not an error - it means the migration already ran or the database is fresh
- Mark migration as complete: `alembic stamp 001`

### Migration Fails: SQLite Version Too Old

If you see SQLite errors about DROP COLUMN:

**Cause**: SQLite version < 3.35.0 doesn't support DROP COLUMN

**Solution**:
1. Upgrade SQLite to 3.35.0+
2. Or recreate database (development only)
3. Or manually alter table schema

### Need to Rollback

**CAUTION**: Downgrading will lose data integrity. Only use if migration caused issues.

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade 000

# Verify current revision
alembic current
```

## Creating New Migrations

To create new migrations for future schema changes:

```bash
# Generate new migration (auto-detect changes)
alembic revision --autogenerate -m "description of changes"

# Generate blank migration for manual edits
alembic revision -m "description of changes"

# Edit the generated file in alembic/versions/
# Then run it
alembic upgrade head
```

## Migration Naming Convention

Migrations follow this pattern:

```
{sequence}_{short_description}.py

Examples:
001_remove_priority_and_tags.py
002_add_task_categories.py
003_create_task_tags_index.py
```

## FAQ

**Q: Do I need to run migrations on development?**
A: No. Tests use in-memory SQLite with fresh schema each time.

**Q: Do I need to run migrations for new databases?**
A: No. New PostgreSQL instances should use the application startup to create tables, OR run migrations to ensure schema consistency.

**Q: Can I skip migrations and manually update the database?**
A: Not recommended. Migrations ensure:
  - Consistency across environments
  - Trackable history
  - Reproducible rollbacks
  - Team collaboration

**Q: What if migration fails halfway?**
A: Alembic tracks the migration state. You can:
  1. Fix the issue
  2. Run the migration again
  3. Or downgrade and try again

**Q: How often do migrations run?**
A: Only when you explicitly run `alembic upgrade`. Deployments should include migration step before starting service.

## Deployment Integration

### Docker Deployment

Add to your Dockerfile or startup script:

```bash
#!/bin/bash
cd /app/backend

# Run pending migrations
alembic upgrade head

# Start application
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Kubernetes Deployment

Add init container before main app:

```yaml
initContainers:
  - name: migrate
    image: task-api:latest
    command: ["alembic", "upgrade", "head"]
    env:
      - name: DATABASE_URL
        valueFrom:
          secretKeyRef:
            name: db-credentials
            key: url
```

### CI/CD Pipeline

Add migration step in your pipeline:

```yaml
# GitHub Actions example
- name: Run Database Migrations
  env:
    DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
  run: |
    cd backend
    alembic upgrade head
```

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [SQLModel Documentation](https://sqlmodel.tiangelo.com/)
