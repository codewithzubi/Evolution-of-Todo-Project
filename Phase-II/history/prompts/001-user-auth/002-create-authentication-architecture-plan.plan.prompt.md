---
id: 002
title: Create Authentication Architecture Plan
stage: plan
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-user-auth
branch: 001-user-auth
user: user
command: /sp.plan
labels: ["architecture", "planning", "authentication", "design"]
links:
  spec: specs/001-user-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-user-auth/plan.md
  - specs/001-user-auth/research.md
  - specs/001-user-auth/data-model.md
  - specs/001-user-auth/contracts/auth.openapi.yaml
  - specs/001-user-auth/contracts/README.md
  - specs/001-user-auth/quickstart.md
  - CLAUDE.md
tests:
  - none
---

## Prompt

(empty - continuation from /sp.specify)

## Response snapshot

Completed comprehensive architecture planning for authentication system with full constitution compliance.

**Phase 0: Research & Architectural Decisions**
- Documented 8 key architectural decisions in research.md
- Better Auth 1.4.18 for frontend authentication management
- JWT tokens in httpOnly cookies (7-day expiration, stateless)
- bcrypt password hashing (12 rounds, ~250ms)
- Rate limiting: 5 attempts per 15 minutes per IP
- Stateless session management (no server-side storage)
- Google OAuth via Better Auth social provider
- CORS restricted to frontend origin only
- Minimal database schema (users table)

**Phase 1: Design & Contracts**
- Created data-model.md with User entity schema (SQLModel + Pydantic)
- Generated OpenAPI 3.1 specification (5 authentication endpoints)
- Documented API contracts with request/response examples
- Created quickstart.md with complete local development setup
- Updated CLAUDE.md agent context with database information

**Constitution Check Results**:
- ✅ I. Locked Tech Stack: All versions match (Next.js 16.1.6, FastAPI 0.128.5, Better Auth 1.4.18, SQLModel 0.0.32)
- ✅ II. Feature Scope Discipline: Authentication is foundational infrastructure, no scope creep
- ✅ III. User-Scoped Security: JWT with user_id claim, httpOnly cookies, CORS configured
- ✅ IV. UI/UX Standards: Login/signup page matches constitution specs exactly
- ✅ V. Clean Architecture: Monorepo structure, layered backend, Server Components
- ✅ VI. Test-First Development: TDD strategy with 80% coverage target

**Project Structure Defined**:
- Backend: FastAPI with routes → services → models architecture
- Frontend: Next.js App Router with (auth) and (protected) route groups
- Middleware: JWT validation and rate limiting
- Database: Alembic migrations for schema management
- Testing: pytest (backend), Vitest + Playwright (frontend)

**Performance Targets**:
- Registration: <60s end-to-end
- Login: <30s end-to-end
- Token validation: <50ms per request
- Concurrent users: 100

**Security Measures**:
- bcrypt password hashing (12 rounds)
- httpOnly cookies (XSS prevention)
- SameSite=Lax (CSRF prevention)
- Rate limiting (brute force prevention)
- SQLModel parameterized queries (SQL injection prevention)
- Secrets in environment variables

## Outcome

- ✅ Impact: Complete architecture plan ready for task generation and implementation
- 🧪 Tests: No tests (planning phase)
- 📁 Files: plan.md, research.md, data-model.md, contracts/auth.openapi.yaml, contracts/README.md, quickstart.md, CLAUDE.md (7 files)
- 🔁 Next prompts: /sp.tasks (generate implementation tasks)
- 🧠 Reflection: Architecture balances security, performance, and simplicity. All constitution principles satisfied with zero violations. Stateless JWT approach reduces infrastructure complexity while maintaining security. Better Auth integration simplifies frontend auth management.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully
- Graders run and results (PASS/FAIL): Constitution Check - PASSED (6/6 principles)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Generate tasks with /sp.tasks and validate task organization by user story
