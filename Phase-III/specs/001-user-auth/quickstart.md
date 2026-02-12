# Quickstart: User Authentication System

**Feature**: 001-user-auth
**Date**: 2026-02-09
**Purpose**: Local development setup and testing guide for authentication system

## Prerequisites

- Python 3.13+ installed
- Node.js 18+ and npm/pnpm installed
- PostgreSQL database (or Neon account)
- Git installed
- Code editor (VS Code recommended)

## Environment Setup

### 1. Clone Repository and Checkout Branch

```bash
git clone <repository-url>
cd Phase-II
git checkout 001-user-auth
```

### 2. Backend Setup

#### Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies with UV
pip install uv
uv pip install -e .

# Or with pip directly
pip install -r requirements.txt
```

#### Configure Environment Variables

Create `backend/.env` file:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/hackathon_todo
# Or use Neon:
# DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/hackathon_todo

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-min-32-characters-long-random-string
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# CORS
FRONTEND_URL=http://localhost:3000

# Better Auth (optional for backend-only testing)
BETTER_AUTH_SECRET=your-better-auth-secret-key
BETTER_AUTH_URL=http://localhost:3000

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**Generate Secret Keys**:
```bash
# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate Better Auth secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Run Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Create users table"

# Apply migrations
alembic upgrade head
```

#### Start Backend Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with make command (if Makefile exists)
make dev
```

Backend will be available at: http://localhost:8000

**API Documentation**: http://localhost:8000/docs (Swagger UI)

---

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend

# Install with npm
npm install

# Or with pnpm (faster)
pnpm install
```

#### Configure Environment Variables

Create `frontend/.env.local` file:

```env
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth
BETTER_AUTH_SECRET=your-better-auth-secret-key
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://user:password@localhost:5432/hackathon_todo

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

#### Start Frontend Development Server

```bash
# Development mode
npm run dev

# Or with pnpm
pnpm dev
```

Frontend will be available at: http://localhost:3000

---

## Testing the Authentication Flow

### 1. Register New User

**Via UI**:
1. Navigate to http://localhost:3000/login
2. Click "Sign Up" tab
3. Enter email: `test@example.com`
4. Enter password: `password123`
5. Click "Sign Up"
6. Should redirect to dashboard

**Via API (curl)**:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Expected Response**:
```json
{
  "user": {
    "id": 1,
    "email": "test@example.com",
    "created_at": "2026-02-09T12:00:00Z"
  },
  "message": "Registration successful"
}
```

---

### 2. Login with Existing User

**Via UI**:
1. Navigate to http://localhost:3000/login
2. Enter email: `test@example.com`
3. Enter password: `password123`
4. Click "Login"
5. Should redirect to dashboard

**Via API (curl)**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Expected Response**:
```json
{
  "user": {
    "id": 1,
    "email": "test@example.com",
    "created_at": "2026-02-09T12:00:00Z"
  },
  "message": "Login successful"
}
```

**Note**: JWT token is set in httpOnly cookie (check Set-Cookie header)

---

### 3. Get Current User

**Via API (curl)**:
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -b cookies.txt
```

**Expected Response**:
```json
{
  "id": 1,
  "email": "test@example.com",
  "created_at": "2026-02-09T12:00:00Z"
}
```

---

### 4. Logout

**Via UI**:
1. Click "Logout" button in navbar
2. Should redirect to landing page

**Via API (curl)**:
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -b cookies.txt
```

**Expected Response**:
```json
{
  "message": "Logout successful"
}
```

---

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/integration/test_auth_routes.py

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

**Expected Output**:
```
tests/unit/test_password_service.py ✓✓✓
tests/unit/test_token_service.py ✓✓✓
tests/integration/test_auth_routes.py ✓✓✓✓✓

========== 11 passed in 2.5s ==========
Coverage: 85%
```

---

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm run test

# Run with coverage
npm run test:coverage

# Run E2E tests (requires backend running)
npm run test:e2e

# Run E2E in headed mode (see browser)
npm run test:e2e:headed
```

**Expected Output**:
```
✓ components/auth/login-form.test.ts (3)
✓ hooks/use-auth.test.ts (4)
✓ e2e/auth-flow.spec.ts (5)

Test Files: 3 passed (3)
Tests: 12 passed (12)
```

---

## Common Issues and Solutions

### Issue: Database Connection Error

**Error**: `could not connect to server: Connection refused`

**Solution**:
1. Ensure PostgreSQL is running: `pg_ctl status`
2. Check DATABASE_URL in `.env` file
3. Verify database exists: `psql -l`
4. Create database if missing: `createdb hackathon_todo`

---

### Issue: Port Already in Use

**Error**: `Address already in use: 8000` or `3000`

**Solution**:
```bash
# Find process using port
# Windows:
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

---

### Issue: JWT Token Not Set

**Error**: `401 Unauthorized` on protected endpoints

**Solution**:
1. Check CORS configuration in backend
2. Ensure `allow_credentials=True` in CORSMiddleware
3. Verify cookie is set in browser DevTools (Application → Cookies)
4. Check cookie attributes (HttpOnly, SameSite, Secure)

---

### Issue: Better Auth Configuration Error

**Error**: `Better Auth initialization failed`

**Solution**:
1. Verify BETTER_AUTH_SECRET is set in both frontend and backend `.env`
2. Ensure DATABASE_URL is accessible from frontend (for Better Auth)
3. Check Better Auth version: `npm list better-auth`
4. Reinstall if needed: `npm install better-auth@1.4.18`

---

## Development Workflow

### 1. Make Changes

```bash
# Backend: Edit files in backend/app/
# Frontend: Edit files in frontend/app/, frontend/components/

# Backend auto-reloads with uvicorn --reload
# Frontend auto-reloads with Next.js dev server
```

### 2. Run Tests

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm run test
```

### 3. Check Code Quality

```bash
# Backend linting
cd backend
ruff check .
ruff format .

# Frontend linting
cd frontend
npm run lint
npm run format
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat(auth): implement user registration endpoint"
```

---

## API Testing with Postman/Insomnia

### Import OpenAPI Spec

1. Open Postman/Insomnia
2. Import → OpenAPI 3.0
3. Select `specs/001-user-auth/contracts/auth.openapi.yaml`
4. All endpoints will be imported with examples

### Test Collection

**Collection**: Authentication API
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me
- POST /api/auth/logout
- POST /api/auth/refresh

**Environment Variables**:
- `base_url`: http://localhost:8000
- `email`: test@example.com
- `password`: password123

---

## Database Management

### View Users

```bash
# Connect to database
psql hackathon_todo

# Query users
SELECT id, email, created_at FROM users;

# Count users
SELECT COUNT(*) FROM users;

# Exit
\q
```

### Reset Database

```bash
# Drop and recreate database
dropdb hackathon_todo
createdb hackathon_todo

# Re-run migrations
cd backend
alembic upgrade head
```

### Seed Test Data

```python
# backend/scripts/seed_users.py
from app.models.user import User
from app.services.password_service import hash_password
from sqlmodel import Session, create_engine
import os

engine = create_engine(os.getenv("DATABASE_URL"))

test_users = [
    {"email": "test@example.com", "password": "password123"},
    {"email": "admin@example.com", "password": "adminpass123"},
]

with Session(engine) as session:
    for user_data in test_users:
        user = User(
            email=user_data["email"],
            hashed_password=hash_password(user_data["password"])
        )
        session.add(user)
    session.commit()
    print(f"Seeded {len(test_users)} test users")
```

Run: `python backend/scripts/seed_users.py`

---

## Next Steps

1. ✅ Authentication system running locally
2. ⏭️ Implement task CRUD endpoints (next feature)
3. ⏭️ Build landing page UI
4. ⏭️ Integrate all features
5. ⏭️ Deploy to production

---

## Useful Commands

```bash
# Backend
cd backend
uvicorn app.main:app --reload          # Start dev server
pytest                                  # Run tests
alembic upgrade head                    # Apply migrations
alembic downgrade -1                    # Rollback migration
ruff check .                            # Lint code

# Frontend
cd frontend
npm run dev                             # Start dev server
npm run test                            # Run tests
npm run lint                            # Lint code
npm run build                           # Production build
npm run start                           # Start production server

# Database
psql hackathon_todo                     # Connect to database
alembic revision --autogenerate -m "msg" # Create migration
```

---

## Support

- **Documentation**: See `specs/001-user-auth/` directory
- **API Docs**: http://localhost:8000/docs
- **Constitution**: `.specify/memory/constitution.md`
- **Issues**: Create GitHub issue with `auth` label
