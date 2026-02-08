# Task CRUD API - Quick Start Guide

## Prerequisites

- Python 3.11+
- pip (Python package manager)
- SQLite (included with Python) or PostgreSQL

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and set your configuration:

```env
# Database URL (SQLite for development, PostgreSQL for production)
DATABASE_URL=sqlite+aiosqlite:///:memory:
# or for PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://user:password@localhost/taskdb

# JWT Secret (use a strong random string in production)
JWT_SECRET=your-super-secret-key-change-in-production

# Better Auth Secret (for authentication integration)
BETTER_AUTH_SECRET=your-better-auth-secret

# Log level
LOG_LEVEL=info

# Debug mode (set to false in production)
DEBUG=false
```

### 3. Initialize Database

For SQLite (in-memory for testing):

```bash
# Database is auto-initialized; no setup needed
```

For PostgreSQL:

```bash
# Create database
createdb taskdb

# Update DATABASE_URL in .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/taskdb
```

## Running the API

### Development Server

```bash
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**Interactive Docs**:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Production Server

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Contract tests only
pytest tests/contract/ -v

# Performance tests
pytest tests/performance/ -v
```

### Run Tests with Coverage

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

Coverage report will be generated in `htmlcov/index.html`

### Run Tests with Markers

```bash
# All tests
pytest -v

# Skip slow tests
pytest -v -m "not performance"

# Only integration tests
pytest -v -m integration
```

## Generating JWT Tokens

### Using Python

```python
from datetime import datetime, timedelta
from jose import jwt
from uuid import uuid4

# Configuration
JWT_SECRET = "your-jwt-secret"
USER_ID = str(uuid4())

# Create payload
payload = {
    "user_id": USER_ID,
    "email": "user@example.com",
    "iat": datetime.utcnow(),
    "exp": datetime.utcnow() + timedelta(hours=24),
}

# Generate token
token = jwt.encode(
    payload,
    JWT_SECRET,
    algorithm="HS256"
)

print(f"User ID: {USER_ID}")
print(f"Token: {token}")
```

### Using OpenSSL (Quick Test Token)

For testing purposes, you can use a simple token:

```bash
# Generate a test user ID
python -c "from uuid import uuid4; print(uuid4())"

# Then create a token using the Python script above
```

## Making API Requests

### Create a Task

```bash
# Set variables
USER_ID="your-user-id-here"
TOKEN="your-jwt-token-here"

# Create task
curl -X POST "http://localhost:8000/api/$USER_ID/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Task",
    "description": "This is my first task",
    "due_date": "2026-02-10T17:00:00"
  }'
```

### List Tasks

```bash
curl -X GET "http://localhost:8000/api/$USER_ID/tasks?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Task Detail

```bash
TASK_ID="task-id-from-create-response"

curl -X GET "http://localhost:8000/api/$USER_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### Update Task

```bash
curl -X PATCH "http://localhost:8000/api/$USER_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Task Title",
    "completed": false
  }'
```

### Mark Task Complete

```bash
curl -X PATCH "http://localhost:8000/api/$USER_ID/tasks/$TASK_ID/complete" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Delete Task

```bash
curl -X DELETE "http://localhost:8000/api/$USER_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"
```

## Complete Workflow Example

```bash
#!/bin/bash

# Configuration
USER_ID=$(python -c "from uuid import uuid4; print(uuid4())")
JWT_SECRET="your-jwt-secret"
API_URL="http://localhost:8000"

# Generate JWT token
TOKEN=$(python -c "
from datetime import datetime, timedelta
from jose import jwt
from uuid import uuid4

payload = {
    'user_id': '$USER_ID',
    'email': 'test@example.com',
    'iat': datetime.utcnow(),
    'exp': datetime.utcnow() + timedelta(hours=24),
}
print(jwt.encode(payload, '$JWT_SECRET', algorithm='HS256'))
")

echo "User ID: $USER_ID"
echo "Token: $TOKEN"
echo ""

# 1. Create a task
echo "1. Creating task..."
CREATE_RESPONSE=$(curl -s -X POST "$API_URL/api/$USER_ID/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI",
    "description": "Complete FastAPI tutorial",
    "due_date": "2026-02-10T17:00:00"
  }')

TASK_ID=$(echo $CREATE_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['data']['id'])")
echo "Created task: $TASK_ID"
echo ""

# 2. List tasks
echo "2. Listing tasks..."
curl -s -X GET "$API_URL/api/$USER_ID/tasks?limit=10" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo ""

# 3. Get task detail
echo "3. Getting task detail..."
curl -s -X GET "$API_URL/api/$USER_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo ""

# 4. Update task
echo "4. Updating task..."
curl -s -X PATCH "$API_URL/api/$USER_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Master FastAPI",
    "description": "Complete advanced FastAPI tutorial"
  }' | python -m json.tool
echo ""

# 5. Mark complete
echo "5. Marking task complete..."
curl -s -X PATCH "$API_URL/api/$USER_ID/tasks/$TASK_ID/complete" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}' | python -m json.tool
echo ""

# 6. Delete task
echo "6. Deleting task..."
curl -s -X DELETE "$API_URL/api/$USER_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"
echo "Task deleted"
```

Save as `test_workflow.sh` and run:

```bash
chmod +x test_workflow.sh
./test_workflow.sh
```

## Using Postman

Import the following collection:

1. Create a new Postman collection
2. Add these requests:

**Create Task**:
- Method: POST
- URL: `{{base_url}}/api/{{user_id}}/tasks`
- Header: `Authorization: Bearer {{token}}`
- Body (JSON):
  ```json
  {
    "title": "My Task",
    "description": "Task description",
    "due_date": "2026-02-10T17:00:00"
  }
  ```

**List Tasks**:
- Method: GET
- URL: `{{base_url}}/api/{{user_id}}/tasks?limit=10&offset=0`
- Header: `Authorization: Bearer {{token}}`

**Get Task**:
- Method: GET
- URL: `{{base_url}}/api/{{user_id}}/tasks/{{task_id}}`
- Header: `Authorization: Bearer {{token}}`

**Update Task**:
- Method: PATCH
- URL: `{{base_url}}/api/{{user_id}}/tasks/{{task_id}}`
- Header: `Authorization: Bearer {{token}}`
- Body (JSON):
  ```json
  {
    "title": "Updated Title"
  }
  ```

**Complete Task**:
- Method: PATCH
- URL: `{{base_url}}/api/{{user_id}}/tasks/{{task_id}}/complete`
- Header: `Authorization: Bearer {{token}}`
- Body (JSON):
  ```json
  {
    "completed": true
  }
  ```

**Delete Task**:
- Method: DELETE
- URL: `{{base_url}}/api/{{user_id}}/tasks/{{task_id}}`
- Header: `Authorization: Bearer {{token}}`

## Troubleshooting

### Issue: "Module not found" error

**Solution**: Ensure you're in the `backend` directory and have installed dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### Issue: "Database connection error"

**Solution**: Check your DATABASE_URL in `.env`:

```env
# For development
DATABASE_URL=sqlite+aiosqlite:///:memory:

# For PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@localhost/taskdb
```

### Issue: "Invalid JWT token"

**Solution**: Ensure:
1. Token is generated with correct JWT_SECRET
2. Token is not expired
3. Authorization header format is correct: `Authorization: Bearer <token>`

### Issue: "401 Unauthorized - Signature verification failed"

**Solution**: The JWT_SECRET used to generate the token doesn't match the server's JWT_SECRET. Update `.env` and regenerate tokens.

### Issue: "403 Forbidden - user_id mismatch"

**Solution**: The user_id in the URL must match the user_id in the JWT token.

## Code Quality

### Run Linting

```bash
ruff check src/ tests/
```

### Format Code

```bash
ruff format src/ tests/
```

### Check Coverage

```bash
pytest --cov=src --cov-report=term-missing
```

Target: ≥70% coverage

## Database Migrations

(If using PostgreSQL with Alembic)

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## API Documentation

Full API documentation is available in `docs/API.md`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | sqlite:///:memory: | Database connection string |
| JWT_SECRET | test_secret_key | Secret for JWT signing |
| BETTER_AUTH_SECRET | test_secret | Better Auth secret |
| LOG_LEVEL | info | Logging level (debug, info, warning, error) |
| DEBUG | false | Debug mode |

## Next Steps

1. Review the full API documentation in `docs/API.md`
2. Run the test suite: `pytest`
3. Explore the interactive docs at `http://localhost:8000/docs`
4. Check the project README for architecture details
