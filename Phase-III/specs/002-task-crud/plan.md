# Implementation Plan: Task CRUD Operations

**Branch**: `002-task-crud` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-task-crud/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement complete CRUD operations for task management with 5 core features: view tasks with filtering (All/Pending/Completed), add new tasks, toggle completion status, update existing tasks, and delete tasks. Full-stack implementation with FastAPI backend (SQLModel ORM, JWT validation, user-scoped queries) and Next.js frontend (TanStack Query for state management, shadcn/ui components, optimistic UI updates). Strong emphasis on user data isolation (all queries filtered by user_id from JWT claims) and performance (supports 1000+ tasks without degradation).

## Technical Context

**Language/Version**: TypeScript (Next.js 16.1.6) + Python 3.13+ (FastAPI 0.128.5)
**Primary Dependencies**: Frontend: Next.js 16.1.6, TanStack Query v5, shadcn/ui, Lucide Icons | Backend: FastAPI 0.128.5, SQLModel 0.0.32, python-jose (JWT), psycopg (PostgreSQL driver)
**Storage**: Neon Serverless PostgreSQL with SQLModel ORM
**Testing**: Frontend: Vitest (unit), Playwright (E2E) | Backend: pytest (unit + integration with TestClient)
**Target Platform**: Web (modern browsers: Chrome, Firefox, Safari, Edge) + FastAPI server
**Project Type**: Web (full-stack: frontend + backend)
**Performance Goals**: View tasks <1s, create task <10s, toggle completion instant (<100ms), support 1000+ tasks without degradation, 60fps scrolling on mobile
**Constraints**: User-scoped security (all queries filtered by user_id from JWT), JWT validation required on all endpoints, optimistic UI updates, 95% operation success rate
**Scale/Scope**: 5 CRUD operations (view/filter, add, toggle complete, update, delete), 2 entities (Task, User), 5 API endpoints, responsive grid UI, modal forms

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Locked Tech Stack (NON-NEGOTIABLE)
**Status**: ✅ PASS
- Frontend: Next.js 16.1.6, TanStack Query v5, shadcn/ui, Lucide Icons: Aligned
- Backend: FastAPI 0.128.5, SQLModel 0.0.32, Python 3.13+: Aligned
- Database: Neon Serverless PostgreSQL: Aligned
- No version deviations

### II. Feature Scope Discipline (NON-NEGOTIABLE)
**Status**: ✅ PASS
- Implements exactly 5 core task operations per constitution:
  1. Add Task (US2) ✓
  2. View Tasks (US1) ✓
  3. Update Task (US4) ✓
  4. Delete Task (US5) ✓
  5. Mark Complete/Incomplete (US3) ✓
- No additional features beyond the 5 core operations
- Filtering (All/Pending/Completed) is part of "View Tasks" operation
- No tags, priorities, due dates, attachments, or other prohibited features

### III. User-Scoped Security (NON-NEGOTIABLE)
**Status**: ✅ PASS
- All API endpoints require JWT validation (FR-025)
- All database queries filter by user_id from JWT claims (FR-019)
- Task entity has user_id foreign key (FR-009)
- Zero data leakage between users (SC-007: 100% data isolation)
- SQLModel parameterized queries prevent SQL injection
- Strong dependency on authentication system (001-user-auth)

### IV. UI/UX Standards (NON-NEGOTIABLE)
**Status**: ✅ PASS
- Dashboard layout matches constitution specification:
  - Left sidebar: All Tasks | Pending | Completed filters (FR-002)
  - Top navbar: Logo + "+ Add Task" button + User avatar + Logout
  - Main area: Responsive task grid (FR-003)
- Task cards use shadcn Card component with:
  - Checkbox for completion toggle (left side)
  - Title (bold) + truncated description (FR-021)
  - Status badge: orange (Pending), green (Completed) (FR-011)
  - Hover state: Edit & Delete icons appear (FR-022)
- Dark mode default, shadcn/ui components, Lucide Icons, responsive design

### V. Clean Architecture
**Status**: ✅ PASS
- Backend: Layered architecture (routes → services → models)
  - Models: SQLModel schemas in backend/app/models/
  - Services: Business logic in backend/app/services/
  - API: Route handlers in backend/app/api/
- Frontend: Server Components + Client Components pattern
  - Components: Task cards, modals in frontend/components/
  - State: TanStack Query for server state
  - Pages: Dashboard at frontend/app/dashboard/
- Follows monorepo structure (frontend/ and backend/ separation)

### VI. Test-First Development (NON-NEGOTIABLE)
**Status**: ✅ PASS
- TDD cycle planned for all user stories
- Backend: pytest for unit tests, TestClient for API integration tests
- Frontend: Vitest for component tests, Playwright for E2E tests
- Coverage target: 80% for business logic (services, API routes)
- Tests for all 5 CRUD operations

**Overall Gate Status**: ✅ ALL GATES PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

## Project Structure

### Documentation (this feature)

```text
specs/002-task-crud/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── tasks.openapi.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── task.py              # Task SQLModel schema
│   │   └── user.py              # User SQLModel schema (from 001-user-auth)
│   ├── services/
│   │   └── task_service.py      # Task business logic (CRUD operations)
│   ├── api/
│   │   ├── deps.py              # JWT validation dependency (from 001-user-auth)
│   │   └── tasks.py             # Task API routes (5 endpoints)
│   └── main.py                  # FastAPI app (existing)
└── tests/
    ├── unit/
    │   └── test_task_service.py # Unit tests for task service
    └── integration/
        └── test_tasks_api.py    # Integration tests for task endpoints

frontend/
├── app/
│   └── dashboard/
│       └── page.tsx             # Dashboard page with task grid and filters
├── components/
│   ├── dashboard/
│   │   ├── task-card.tsx        # Task card component (checkbox, title, description, badges, icons)
│   │   ├── task-grid.tsx        # Responsive grid container for tasks
│   │   ├── sidebar.tsx          # Filter sidebar (All/Pending/Completed)
│   │   ├── add-task-modal.tsx   # Modal for creating new tasks
│   │   ├── edit-task-modal.tsx  # Modal for editing existing tasks
│   │   └── delete-confirm-dialog.tsx # Confirmation dialog for deletion
│   └── ui/                      # shadcn/ui components (Button, Card, Dialog, Input - existing)
├── lib/
│   ├── api/
│   │   └── tasks.ts             # API client functions for task operations
│   └── hooks/
│       └── use-tasks.ts         # TanStack Query hooks for task state management
└── tests/
    ├── unit/
    │   └── dashboard/
    │       ├── task-card.test.tsx
    │       └── task-grid.test.tsx
    └── e2e/
        └── task-crud.spec.ts    # E2E tests for all CRUD operations
```

**Structure Decision**: Web application structure (Option 2) with full-stack implementation. Backend uses layered architecture (models → services → API routes) with SQLModel for database access. Frontend uses Next.js App Router with dashboard page, modular components for task UI, and TanStack Query for server state management. Strong separation between backend (FastAPI) and frontend (Next.js) with RESTful API communication.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. All constitution gates passed.

This feature implements exactly the 5 core task operations specified in the constitution with no additional complexity. Full-stack implementation follows clean architecture principles with proper separation of concerns (backend: models → services → API, frontend: components → hooks → pages). User-scoped security enforced at all layers. No architectural deviations or complexity beyond constitutional requirements.

---

## Phase 1 Artifacts

### Generated Documents

1. ✅ **research.md** - 8 architectural decisions documented
   - Database schema design with user-scoped security (SQLModel, foreign keys, indexes)
   - API endpoint design (5 RESTful endpoints)
   - State management strategy (TanStack Query v5 with optimistic updates)
   - Modal vs inline editing approach (modals for create/edit, inline for toggle)
   - Filtering implementation (client-side for instant switching)
   - Performance optimization for 1000+ tasks (indexes, virtual scrolling if needed)
   - JWT validation approach (FastAPI dependency injection)
   - Error handling strategy (layered with user-friendly messages)

2. ✅ **data-model.md** - 2 entities with relationships
   - Task entity: id, user_id (FK), title, description, is_completed, created_at, updated_at
   - User entity: Reference from 001-user-auth
   - One-to-many relationship: User → Tasks
   - Validation rules for all CRUD operations
   - State transitions: Pending ↔ Completed → Deleted
   - Query patterns for all 5 operations

3. ✅ **contracts/tasks.openapi.yaml** - 5 API endpoints
   - GET /api/tasks?status={all|pending|completed} - List tasks with filter
   - POST /api/tasks - Create new task
   - PATCH /api/tasks/{task_id}/toggle - Toggle completion status
   - PUT /api/tasks/{task_id} - Update task
   - DELETE /api/tasks/{task_id} - Delete task permanently
   - Complete request/response schemas with examples
   - Error responses for all failure scenarios

4. ✅ **quickstart.md** - 18 test scenarios with acceptance criteria
   - View tasks with filtering (all, pending, completed)
   - Add task (with/without description, validation)
   - Toggle completion status (pending ↔ completed)
   - Edit task (pre-filled form, validation)
   - Delete task (confirmation dialog)
   - Responsive design testing
   - Performance testing (1000+ tasks)
   - Security testing (user data isolation)
   - Error handling (network failures, concurrent edits)

5. ✅ **Agent context updated** - CLAUDE.md updated with task-crud technology

### Post-Design Constitution Re-Check

**Status**: ✅ ALL GATES STILL PASS

No changes to constitution compliance after design phase. Task CRUD remains:
- Aligned with locked tech stack (Next.js 16.1.6, FastAPI 0.128.5, SQLModel 0.0.32, TanStack Query v5)
- Implements exactly 5 core operations per constitution (add, view, update, delete, mark complete)
- Enforces user-scoped security (JWT validation, user_id filtering on all queries)
- Matches UI/UX standards (dashboard layout, task cards, sidebar filters, shadcn/ui components)
- Follows clean architecture (backend: models → services → API, frontend: components → hooks → pages)
- Test-First Development planned (pytest + Vitest + Playwright)

---

## Next Steps

1. ✅ Planning phase complete - proceed to `/sp.tasks` command
2. Generate tasks.md with implementation tasks organized by user story
3. Begin implementation following Red-Green-Refactor TDD cycle
4. Validate against quickstart.md test scenarios
5. Verify performance targets and security requirements

---

## Summary

Task CRUD architecture planning complete. All design decisions documented in research.md with clear rationale and alternatives considered. Data model defines Task entity with user-scoped foreign key relationship. API contracts specify 5 RESTful endpoints with complete request/response schemas. Test scenarios cover all CRUD operations, filtering, validation, performance, security, and error handling. Constitution compliance verified pre- and post-design. Ready for task generation phase.
