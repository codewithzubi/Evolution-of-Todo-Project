---
id: 002
title: Create Task CRUD Architecture Plan
stage: plan
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-task-crud
branch: 002-task-crud
user: user
command: /sp.plan
labels: ["architecture", "planning", "task-crud", "full-stack", "crud"]
links:
  spec: specs/002-task-crud/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-task-crud/plan.md
  - specs/002-task-crud/research.md
  - specs/002-task-crud/data-model.md
  - specs/002-task-crud/contracts/tasks.openapi.yaml
  - specs/002-task-crud/quickstart.md
tests:
  - none
---

## Prompt

(empty - continuation from /sp.plan skill invocation)

## Response snapshot

Created comprehensive architecture plan for task CRUD feature with complete technical context, design decisions, data model, API contracts, and test scenarios.

**Technical Context**:
- Language: TypeScript (Next.js 16.1.6) + Python 3.13+ (FastAPI 0.128.5)
- Full-stack implementation with RESTful API
- Database: Neon PostgreSQL with SQLModel ORM
- State management: TanStack Query v5 with optimistic updates
- Performance targets: view <1s, create <10s, toggle <100ms, support 1000+ tasks

**Constitution Check**: ✅ ALL GATES PASS
- Locked tech stack: Aligned (Next.js, FastAPI, SQLModel, TanStack Query)
- Feature scope: Aligned (exactly 5 core operations: add, view, update, delete, toggle)
- User-scoped security: Enforced (JWT validation, user_id filtering on all queries)
- UI/UX standards: Aligned (dashboard layout, task cards, sidebar filters, shadcn/ui)
- Clean architecture: Aligned (backend: models → services → API, frontend: components → hooks → pages)
- Test-First Development: Planned (pytest + Vitest + Playwright)

**Project Structure**:
- Backend: models/task.py, services/task_service.py, api/tasks.py
- Frontend: dashboard/page.tsx, components/dashboard/ (task-card, task-grid, sidebar, modals)
- Tests: backend/tests/ (unit + integration), frontend/tests/ (unit + E2E)

**Phase 0: Research (research.md)**:
8 architectural decisions documented with rationale and alternatives:
1. Database schema: Task entity with user_id FK, indexed for performance
2. API endpoints: 5 RESTful endpoints (GET, POST, PATCH, PUT, DELETE)
3. State management: TanStack Query v5 with optimistic updates
4. UI approach: Modals for create/edit, inline checkbox for toggle, confirmation for delete
5. Filtering: Client-side for instant switching (no API round-trip)
6. Performance: Database indexes, virtual scrolling if needed for 1000+ tasks
7. JWT validation: FastAPI dependency injection (reuse from 001-user-auth)
8. Error handling: Layered with user-friendly messages

**Phase 1: Design**:

1. **data-model.md** - 2 entities with relationships
   - Task entity: id, user_id (FK), title (200 chars), description (1000 chars), is_completed, timestamps
   - User entity: Reference from 001-user-auth
   - One-to-many: User → Tasks (CASCADE on delete)
   - Validation rules for all CRUD operations
   - State transitions: Pending ↔ Completed → Deleted

2. **contracts/tasks.openapi.yaml** - 5 API endpoints
   - GET /api/tasks?status={all|pending|completed} - List with filter
   - POST /api/tasks - Create (body: title, description?)
   - PATCH /api/tasks/{id}/toggle - Toggle completion
   - PUT /api/tasks/{id} - Update (body: title, description?)
   - DELETE /api/tasks/{id} - Delete permanently
   - Complete schemas with examples and error responses

3. **quickstart.md** - 18 test scenarios
   - View/filter tasks (all, pending, completed)
   - Add task (with/without description, validation errors)
   - Toggle completion (pending ↔ completed, optimistic updates)
   - Edit task (pre-filled form, validation)
   - Delete task (confirmation dialog, permanent removal)
   - Responsive design, performance (1000+ tasks), security (data isolation)
   - Error handling (network failures, concurrent edits)

**Key Characteristics**:
- Full-stack CRUD implementation (backend + frontend)
- User-scoped security (100% data isolation via user_id filtering)
- Optimistic UI updates (instant feedback, rollback on error)
- Performance-optimized (supports 1000+ tasks, 60fps scrolling)
- 5 core operations per constitution (no scope creep)
- Strong dependency on authentication system (001-user-auth)

**Agent Context Updated**: CLAUDE.md updated with task-crud technology stack

## Outcome

- ✅ Impact: Complete architecture plan ready for task generation
- 🧪 Tests: No tests (planning phase) - test scenarios documented in quickstart.md
- 📁 Files: specs/002-task-crud/plan.md (250+ lines), research.md (400+ lines), data-model.md (400+ lines), contracts/tasks.openapi.yaml (400+ lines), quickstart.md (500+ lines)
- 🔁 Next prompts: /sp.tasks (task generation for task-crud)
- 🧠 Reflection: Task CRUD is the core feature of the todo application - implements all 5 constitutional operations. Full-stack complexity requires careful coordination between backend (FastAPI + SQLModel) and frontend (Next.js + TanStack Query). User-scoped security is critical and enforced at multiple layers (JWT validation, database queries, API authorization). Optimistic updates provide instant feedback while maintaining data consistency. Performance targets are aggressive (1000+ tasks) but achievable with proper indexing and virtual scrolling.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully
- Graders run and results (PASS/FAIL): Constitution check validation - PASSED (all 6 gates)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Complete task generation for task-crud to have full implementation roadmap for all three features
