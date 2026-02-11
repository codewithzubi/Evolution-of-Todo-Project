# Implementation Plan: User Authentication System

**Branch**: `001-user-auth` | **Date**: 2026-02-10 | **Spec**: [spec.md](./spec.md)

## Summary

Implement secure multi-user authentication using Better Auth 1.4+ (frontend) and FastAPI (backend) with stateless JWT tokens. Better Auth handles registration, login, and optional Google OAuth, issuing JWT tokens upon successful authentication. FastAPI verifies JWT signatures using BETTER_AUTH_SECRET and extracts user_id from token payload to enforce strict data isolation. No server-side sessions, no sessions table—purely stateless architecture.

## Technical Context

**Stack**:
- Frontend: Next.js 16.1.6 (App Router), Better Auth 1.4+, TanStack Query v5, shadcn/ui
- Backend: FastAPI 0.128.5, SQLModel 0.0.32, python-jose[cryptography], passlib[bcrypt]
- Database: Neon Serverless PostgreSQL (users table only)
- Testing: pytest (backend), Vitest + Playwright (frontend)

**Performance**:
- Registration: <60s end-to-end
- Login: <30s end-to-end
- JWT verification: <50ms per request
- Concurrent users: 100+

**Constraints**:
- Stateless JWT (no server-side sessions, no sessions table)
- JWT stored client-side (Better Auth manages secure storage)
- Password hashing: bcrypt (12 rounds)
- Rate limiting: 5 attempts per 15 minutes per IP
- JWT expiration: 7 days (configurable)
- CORS: Frontend origin only
- BETTER_AUTH_SECRET shared between frontend and backend

**Scope**:
- 3 auth endpoints: register, login, logout
- 1 database table: users (id UUID, email, hashed_password, created_at)
- Google OAuth: Optional (P2)

## Constitution Check

### I. Locked Tech Stack ✅ PASS
- ✅ Next.js 16.1.6, Better Auth 1.4+, TanStack Query v5, shadcn/ui
- ✅ FastAPI 0.128.5, SQLModel 0.0.32, Python 3.13+
- ✅ Neon Serverless PostgreSQL
- ✅ pytest, Vitest, Playwright

### II. Feature Scope Discipline ✅ PASS
- ✅ Authentication is infrastructure (enables 5 core task features)
- ✅ Scope: registration, login, logout, JWT verification, optional OAuth
- ✅ Out of scope: password reset, 2FA, email verification, account lockout

### III. User-Scoped Security ✅ PASS
- ✅ JWT tokens include user_id claim
- ✅ Backend validates JWT signature using BETTER_AUTH_SECRET on every protected endpoint
- ✅ All database queries filtered by user_id from JWT
- ✅ Better Auth handles secure client-side token storage
- ✅ SQLModel parameterized queries prevent SQL injection
- ✅ CORS restricted to frontend origin
- ✅ Stateless architecture (no sessions table)

### IV. UI/UX Standards ✅ PASS
- ✅ Login/Signup: Centered card with dark gradient background
- ✅ Toggle between login/signup forms
- ✅ Better Auth integration
- ✅ Dark mode default
- ✅ shadcn/ui components exclusively
- ✅ Responsive design

### V. Clean Architecture ✅ PASS
- ✅ Monorepo: frontend/ and backend/ directories
- ✅ Backend: routes → services → models (minimal layering)
- ✅ Frontend: Server Components default, Client Components for forms
- ✅ API: RESTful with proper HTTP status codes
- ✅ State: TanStack Query for auth state
- ✅ No over-engineering: stateless design, single users table

### VI. Test-First Development ✅ PASS
- ✅ TDD cycle: Red → Green → Refactor
- ✅ Backend: pytest (unit), TestClient (integration)
- ✅ Frontend: Vitest (unit), Playwright (E2E)
- ✅ Target: 80% coverage for auth logic
- ✅ Critical flows: register → login → logout

**Gate Status**: ✅ PASS - All constitution principles satisfied

## Project Structure

### Documentation

```
specs/001-user-auth/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Architectural decisions
├── data-model.md        # User entity schema
├── quickstart.md        # Development setup
├── contracts/
│   ├── auth.openapi.yaml
│   └── README.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Implementation tasks (next)
```

### Source Code

```
backend/
├── app/
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # BETTER_AUTH_SECRET config
│   ├── models/
│   │   └── user.py                # User SQLModel (no session model)
│   ├── services/
│   │   ├── auth_service.py        # Registration/login logic
│   │   └── jwt_service.py         # JWT verification
│   ├── api/
│   │   ├── deps.py                # get_current_user_id dependency
│   │   └── routes/
│   │       └── auth.py            # Auth endpoints
│   └── middleware/
│       └── rate_limit.py          # Rate limiting
├── tests/
│   ├── unit/
│   │   └── test_jwt_service.py
│   └── integration/
│       └── test_auth_routes.py
├── alembic/                       # Migrations
├── pyproject.toml
└── .env.example

frontend/
├── app/
│   ├── (auth)/
│   │   └── login/
│   │       └── page.tsx           # Login/Signup page
│   ├── (protected)/
│   │   └── dashboard/
│   │       └── page.tsx           # Dashboard (requires auth)
│   ├── layout.tsx
│   └── page.tsx                   # Landing page
├── components/
│   ├── ui/                        # shadcn/ui
│   └── auth/
│       ├── login-form.tsx         # Client Component
│       ├── signup-form.tsx        # Client Component
│       └── auth-provider.tsx      # Better Auth provider
├── lib/
│   ├── auth.ts                    # Better Auth config
│   ├── api-client.ts              # Backend API client (includes JWT)
│   └── utils.ts
├── hooks/
│   ├── use-auth.ts                # TanStack Query
│   └── use-user.ts
├── tests/
│   ├── unit/
│   └── e2e/
│       └── auth-flow.spec.ts
├── package.json
└── .env.local.example
```

## Phase 0: Research ✅ COMPLETE

**Output**: `research.md`

**Decisions Documented**:
1. Better Auth 1.4+ for frontend authentication
2. Stateless JWT with client-side storage (7-day expiration)
3. bcrypt password hashing (12 rounds)
4. Token bucket rate limiting (5/15min per IP)
5. No server-side sessions (stateless architecture)
6. Google OAuth via Better Auth social provider
7. CORS restricted to frontend origin
8. Single users table (UUID, email, hashed_password, created_at)
9. python-jose for JWT verification
10. User isolation via user_id filtering

## Phase 1: Design & Contracts ✅ COMPLETE

**Outputs**: `data-model.md`, `contracts/`, `quickstart.md`

**Data Model**:
- User entity (UUID, email, hashed_password, created_at)
- Pydantic models (RegisterRequest, LoginRequest, UserResponse, TokenResponse)
- Alembic migration for users table
- No sessions table

**API Contracts**:
- OpenAPI 3.1 spec with 3 endpoints
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- Error responses (400, 401, 409, 429, 500)

**Quickstart**:
- Local dev setup
- Environment config
- Database migrations
- Testing procedures

## Phase 2: Task Generation (Next)

**Command**: `/sp.tasks`

Generate actionable task list organized by user story:
- User Story 1: Registration (P1)
- User Story 2: Login (P1)
- User Story 3: JWT Token Management (P1)
- User Story 4: Logout (P1)
- User Story 5: Google OAuth (P2)

Each task includes:
- Exact file paths
- Acceptance criteria
- Dependencies
- Test requirements

## Architecture Highlights

**Stateless JWT Flow**:
1. User registers/logs in via Better Auth
2. Better Auth issues JWT token (user_id, email, exp, iat)
3. Client stores token (Better Auth manages storage)
4. Client includes token in Authorization header: `Bearer <token>`
5. Backend verifies JWT signature using BETTER_AUTH_SECRET
6. Backend extracts user_id from verified token
7. Backend filters all queries by user_id

**Security**:
- Passwords: bcrypt (12 rounds, ~250ms)
- JWT: HS256 algorithm, BETTER_AUTH_SECRET (32+ chars)
- Rate limiting: 5 attempts per 15 minutes per IP
- CORS: Frontend origin only
- User isolation: All queries filtered by user_id
- No XSS: Better Auth encrypts tokens in localStorage

**Database**:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX idx_users_email ON users(email);
```

**No Sessions Table**: Stateless architecture eliminates need for server-side session storage.

## Summary

**Status**: ✅ PLANNING COMPLETE

**Artifacts**:
- ✅ plan.md (this file)
- ✅ research.md (10 decisions)
- ✅ data-model.md (User entity)
- ✅ contracts/auth.openapi.yaml (3 endpoints)
- ✅ contracts/README.md
- ✅ quickstart.md

**Constitution**: ✅ PASS (6/6 principles)

**Next**: `/sp.tasks` to generate implementation tasks

**Key Points**:
- Stateless JWT (no sessions table)
- Better Auth issues tokens
- FastAPI verifies with BETTER_AUTH_SECRET
- Every query filtered by user_id
- Minimal architecture, no over-engineering
