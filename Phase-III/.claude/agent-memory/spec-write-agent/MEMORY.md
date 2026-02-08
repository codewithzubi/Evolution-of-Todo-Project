# Spec Writer Agent Memory

## Phase-III Task Generation Patterns

### Task List Structure
- Task IDs follow pattern: T[3-digit range] starting at T300 (Phase-III features)
- Format: `- [ ] [ID] [P?] [Story] Description with exact file path`
  - [P] = Parallelizable (different files, no dependencies)
  - [Story] = User story tag (US1-US7)
  - File paths = Absolute paths from codebase root
- Each task includes acceptance criteria (testable, measurable)

### Phase Organization for 7-Story Features
1. **Phase 1**: Database & Migrations (foundational)
2. **Phase 2**: Service/Infrastructure Layer (shared by all stories)
3. **Phases 3-9**: Feature implementation (one phase per user story, P1 stories first)
4. **Phase 10**: Testing, security, documentation (comprehensive coverage)

### Task Ranges & Task Counts
- Phase 1 Setup: 7 tasks (database schema, migrations, models)
- Phase 2 Foundation: 9 tasks (services, API skeleton, error handling)
- Phases 3-7 (Feature Stories): 6-12 tasks each (implement + test)
- Phase 8-9 (Cross-Cutting): 7-9 tasks each (persistence, isolation)
- Phase 10 Testing: 15+ tasks (integration, security, performance, docs)
- **Total Range**: 60-90 tasks for complex feature with 7 stories

### Critical Path Analysis
- Database schema blocks all tool implementation (must be first)
- MCP server initialization blocks tool implementation
- Chat endpoint contract blocks frontend implementation
- User isolation testing cannot run until all CRUD operations exist
- Dependency: T300→T307→T316→T328→T334→T340→T345→T350→T359→T366

### Parallelization Patterns
- **After Phase 1**: Multiple engineers can work on Phase 2 components in parallel
- **After Phase 2**: Backend tools (add_task, list_tasks) and frontend widget can develop in parallel
- **After Each Story**: Next story can start while previous story completes testing
- **Testing Phase**: Security, performance, and documentation testing can run in parallel

### MVP Scope Strategy
- MVP = Phases 1-3 (core functionality) + Phase 8 (persistence)
- MVP tasks ≈ 40-50 tasks
- MVP delivery timeline: 4-5 days with 2 engineers
- Post-MVP features clearly separated (List, Update, Complete, Delete in later phases)

### Phase-II Integration Notes
- All new code is additive (no modifications to Phase-II)
- MCP tools call existing Phase-II endpoints (reuse, don't duplicate)
- User and task models used as-is (no schema changes)
- JWT validation uses existing Better Auth infrastructure
- Specify exact endpoint calls in task descriptions (e.g., "Call POST /api/users/{user_id}/tasks")

### Security Testing Integration
- Dedicate full phase (Phase 9) to user isolation validation
- Multi-user test setup: create User A and User B with separate tokens
- 403 Forbidden tests (not 404) to avoid leaking resource existence
- Test user_id scoping at: database query, service layer, API layer, MCP tool layer
- Include cross-user access attempt logging/audit trail tests

### Test Coverage Requirements
- Phase checkpoints: 80-90% coverage minimum for features
- Final checkpoint (Phase 10): 70% overall, 80%+ for critical paths
- Critical paths: authentication, tool execution, user isolation
- Coverage reports generated with tools: pytest --cov, vitest --coverage

### File Path Conventions
- Backend: `backend/src/models/`, `backend/src/services/`, `backend/src/api/`, `backend/src/mcp/`, `backend/src/agents/`
- Frontend: `frontend/src/components/`, `frontend/src/hooks/`, `frontend/src/services/`
- Tests: `backend/tests/unit/`, `backend/tests/integration/`, `backend/tests/security/`, `backend/tests/performance/`
- Migrations: `backend/alembic/versions/`
- Specs: `specs/[feature]/tasks.md`, documentation files in same directory

### Task Dependencies Documentation
- Critical Path: Marked as sequential requirements
- Parallelizable Tasks: Grouped by file/module to enable concurrent development
- Example provided: "After Phase 1 Complete: T307-T309 (MCP Server) + T310-T313 (API skeleton) can run in parallel"

### Team Guidance Sections
- Always include role-specific notes: Backend engineer, Frontend engineer, QA engineer
- Specify focus areas: what each role should prioritize
- Include general notes on: branching strategy, PR reviews, ADR documentation

### Success Criteria Mapping
- Link each task to success criteria (SC-001 to SC-012)
- Phase checkpoints should verify subset of success criteria
- Final checkpoint (Phase 10) verifies ALL success criteria
- Include acceptance checklist at end of task list for sign-off

## Convention Reminders
- Use absolute paths ONLY (start with `/mnt/c/Users/...`)
- Task descriptions include exact file paths for clarity
- Each task is independently testable
- Acceptance criteria are specific and measurable
- No implementation details in task descriptions (focus on "what", not "how")
