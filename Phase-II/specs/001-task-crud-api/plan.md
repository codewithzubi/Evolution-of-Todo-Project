# Implementation Plan: Task CRUD API

**Branch**: `001-task-crud-api` | **Date**: 2026-02-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-task-crud-api/spec.md`

---

## Summary

Implement a secure, multi-user Task CRUD API using FastAPI, SQLModel, and Neon Serverless PostgreSQL. The API will provide 7 RESTful endpoints for authenticated users to manage their tasks with full CRUD operations and task completion tracking. Authentication is enforced via JWT tokens (Better Auth integration), and authorization is enforced through query-level user scoping to prevent cross-user data access. All endpoints are stateless, horizontally scalable, and include comprehensive input validation and error handling.

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.104+, SQLModel 0.0.14+, Pydantic 2.x, python-jose 3.x (JWT), cryptography (for secret handling)
**Storage**: Neon Serverless PostgreSQL (async support via asyncpg)
**Testing**: pytest 7.x with pytest-asyncio for async tests, pytest-cov for coverage
**Target Platform**: Linux/Docker (Kubernetes-ready)
**Project Type**: Web application (backend API only; frontend is separate Next.js app)
**Performance Goals**: p95 latency < 500ms for all endpoints under normal load
**Constraints**:
- All queries must include `WHERE user_id = :user_id` filter (data isolation)
- No plain-text secrets in code or logs
- Minimum 70% test coverage
- Token expiration: 7 days

**Scale/Scope**: Support 10k+ concurrent users, 1M+ tasks, stateless horizontal scaling

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status |
|-----------|-------------|--------|
| **Spec-First Development** | All code must reference spec sections via Task comments | ✅ Will enforce |
| **Traceability** | Every line must have `# [Task]: T-XXX, [From]: specs/...` | ✅ Will enforce |
| **JWT Authentication** | Better Auth secret via `.env`, stateless verification | ✅ Aligned |
| **Data Isolation** | Query-level user scoping, 403 for ownership violations | ✅ Required by spec |
| **Test Coverage** | Minimum 70% coverage via pytest --cov | ✅ Required |
| **Stateless Services** | No in-memory session state, all state in database | ✅ Aligned |
| **Clean Architecture** | Models / Services / API layers clearly separated | ✅ Will design |
| **No Plain-Text Secrets** | JWT_SECRET and DB credentials from .env only | ✅ Will enforce |
| **Pydantic Validation** | All request bodies validated via Pydantic models | ✅ Required |
| **Linting** | Ruff (Python) passes on all code | ✅ Will enforce |

**Gate Status**: ✅ **PASS** — All principles are compatible with spec requirements. Proceed to Phase 0.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-task-crud-api/
├── spec.md                          # Feature specification (7 endpoints, 6 user stories)
├── plan.md                          # This file
├── checklists/
│   └── requirements.md              # Spec quality checklist (all items PASS)
├── research.md                      # Phase 0 output (to be created)
├── data-model.md                    # Phase 1 output (to be created)
├── quickstart.md                    # Phase 1 output (to be created)
├── contracts/
│   ├── openapi.yaml                 # OpenAPI spec (Phase 1)
│   └── error-codes.yaml             # Error taxonomy (Phase 1)
└── tasks.md                         # Phase 2 output (created by /sp.tasks)
```

### Source Code (backend only)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                  # User model (from Better Auth)
│   │   └── task.py                  # Task model with validation
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py          # Business logic for task CRUD
│   ├── api/
│   │   ├── __init__.py
│   │   ├── middleware.py            # JWT verification middleware
│   │   ├── schemas.py               # Pydantic request/response models
│   │   └── tasks.py                 # Task endpoints (all 7 routes)
│   ├── database.py                  # Database connection (async sqlalchemy)
│   ├── config.py                    # Configuration from .env
│   └── main.py                      # FastAPI app initialization
├── tests/
│   ├── conftest.py                  # pytest fixtures (test DB, auth fixtures)
│   ├── unit/
│   │   ├── test_task_service.py    # Service layer tests
│   │   └── test_schemas.py         # Validation tests
│   ├── integration/
│   │   ├── test_task_endpoints.py  # Full API tests (all 7 endpoints)
│   │   └── test_auth_middleware.py # JWT verification tests
│   └── contract/
│       └── test_api_contract.py    # OpenAPI spec validation
├── .env.example                     # Environment template (no secrets)
├── requirements.txt                 # Python dependencies
├── pyproject.toml                   # Project metadata
└── Dockerfile                       # Container image
```

**Structure Decision**: Web application backend structure (Option 2). FastAPI monolith with layered architecture (Models → Services → API). Tests use real PostgreSQL test instance for integration tests. Deployment-ready with Docker support.

---

## Phase 0: Research & Unknowns

**Status**: To be completed by `/sp.plan` command
**Deliverable**: `research.md`

### Research Tasks

1. **JWT Integration with Better Auth**
   - Question: How does Better Auth issue JWT tokens to FastAPI backend?
   - Research: Token format, claims structure, secret key exchange mechanism
   - Agent: `auth-security` to verify OAuth2/JWT patterns
   - Output: JWT claims schema and verification code pattern

2. **SQLModel Async Patterns**
   - Question: How to use SQLModel with async SQLAlchemy and asyncpg?
   - Research: Best practices for async session management, query composition
   - Agent: `db-neon-sqlmodel` to explore async session management
   - Output: SQLModel async pattern guide

3. **Neon Serverless Connection Management**
   - Question: How to handle Neon's connection pooling in serverless context?
   - Research: PgBouncer configuration, connection limits, retry strategies
   - Agent: `db-neon-sqlmodel` to investigate Neon best practices
   - Output: Connection pooling configuration

4. **Pydantic v2 Request/Response Validation**
   - Question: How to validate nested schemas and handle partial updates (PATCH)?
   - Research: Pydantic field validation, Optional fields, update strategies
   - Agent: `fastapi-backend` to explore Pydantic v2 patterns
   - Output: Pydantic schema patterns for all endpoint types

5. **Error Response Standardization**
   - Question: How to return consistent error responses (data + error structure)?
   - Research: FastAPI exception handlers, custom response models
   - Agent: `fastapi-backend` to establish error handling patterns
   - Output: FastAPI exception handler templates

---

## Phase 1: Design & Contracts

**Prerequisite**: Phase 0 research complete
**Deliverables**: `data-model.md`, `contracts/openapi.yaml`, `contracts/error-codes.yaml`, `quickstart.md`

### 1.1 Data Model Design

**Entities from Specification**:

#### User Entity
```
- id: UUID (primary key, from Better Auth)
- email: string (unique, from Better Auth)
- name: string (from Better Auth)
- created_at: datetime (from Better Auth)
```

#### Task Entity
```
- id: UUID (primary key)
- user_id: UUID (foreign key → User, required for row-level security)
- title: string (required, 1-255 chars)
- description: string (optional, max 2000 chars)
- due_date: datetime (optional, ISO 8601)
- completed: boolean (default: false)
- completed_at: datetime (nullable, set when completed=true)
- created_at: datetime (auto-set on creation)
- updated_at: datetime (auto-set on update)

Indexes:
- PRIMARY KEY (id)
- UNIQUE (id, user_id) [composite for fast lookups]
- INDEX (user_id, created_at) [for list queries]
- INDEX (user_id, completed) [for filtering completed tasks]
```

**Validation Rules** (from spec):
- title: required, 1-255 chars, non-empty string
- description: optional, max 2000 chars
- due_date: optional, valid ISO 8601 datetime
- completed: boolean (true/false)
- User ownership: every task must have valid user_id reference

### 1.2 API Contracts

**Endpoint Summary** (from spec):

| Endpoint | Method | Purpose | Auth | Ownership Check |
|----------|--------|---------|------|-----------------|
| `/api/{user_id}/tasks` | POST | Create task | JWT | user_id match |
| `/api/{user_id}/tasks` | GET | List user tasks | JWT | user_id match |
| `/api/{user_id}/tasks/{task_id}` | GET | Get task details | JWT | task owner |
| `/api/{user_id}/tasks/{task_id}` | PUT | Update entire task | JWT | task owner |
| `/api/{user_id}/tasks/{task_id}` | PATCH | Partial update | JWT | task owner |
| `/api/{user_id}/tasks/{task_id}/complete` | PATCH | Toggle complete | JWT | task owner |
| `/api/{user_id}/tasks/{task_id}` | DELETE | Delete task | JWT | task owner |

**Request/Response Schemas** (to be detailed in `contracts/openapi.yaml`):

- **POST /api/{user_id}/tasks** (Create):
  - Request: `{ title, description?, due_date? }`
  - Response: `{ data: { id, user_id, title, description, due_date, completed, completed_at, created_at, updated_at }, error: null }`
  - Status: 201 Created

- **GET /api/{user_id}/tasks** (List):
  - Query: `?limit=10&offset=0`
  - Response: `{ data: { items: [...], pagination: { limit, offset, total, has_more } }, error: null }`
  - Status: 200 OK

- **GET /api/{user_id}/tasks/{task_id}** (Detail):
  - Response: `{ data: { id, user_id, ... }, error: null }`
  - Status: 200 OK or 404 Not Found

- **PUT /api/{user_id}/tasks/{task_id}** (Full Update):
  - Request: `{ title, description?, due_date?, completed? }`
  - Response: `{ data: { ... }, error: null }`
  - Status: 200 OK

- **PATCH /api/{user_id}/tasks/{task_id}** (Partial Update):
  - Request: Any subset of fields
  - Response: `{ data: { ... }, error: null }`
  - Status: 200 OK

- **PATCH /api/{user_id}/tasks/{task_id}/complete** (Toggle):
  - Request: `{ completed: true/false }`
  - Response: `{ data: { ..., completed, completed_at }, error: null }`
  - Status: 200 OK

- **DELETE /api/{user_id}/tasks/{task_id}** (Delete):
  - Response: No body
  - Status: 204 No Content

**Error Responses** (to be detailed in `contracts/error-codes.yaml`):
- 400 Bad Request: Invalid request format
- 401 Unauthorized: Missing/expired JWT token
- 403 Forbidden: User ID mismatch or task not owned by user
- 404 Not Found: Task doesn't exist
- 422 Unprocessable Entity: Validation error (field-level details)
- 500 Internal Server Error: Unexpected error (with correlation ID)

### 1.3 Agent Context Update

Run the agent context update script to add Task CRUD API context to FastAPI and DB agents:

```bash
.specify/scripts/bash/update-agent-context.sh claude
```

This will:
- Detect current AI agent
- Update agent-specific context with Task CRUD API requirements
- Add FastAPI endpoint patterns
- Add SQLModel async patterns
- Add Better Auth JWT verification patterns

---

## Phase 2: Task Breakdown (Managed by `/sp.tasks`)

**Prerequisite**: Phase 1 complete (data-model.md, contracts/)
**Output**: `tasks.md` (created by `/sp.tasks` command, not by `/sp.plan`)

**Anticipated Task Structure** (for planning):

### T-001: Setup FastAPI Project & Environment
- Create `backend/` directory structure
- Initialize `requirements.txt` with dependencies (FastAPI, SQLModel, pytest, etc.)
- Create `.env.example` with placeholders
- Setup `pyproject.toml` and `Dockerfile`
- Agent: `fastapi-backend`

### T-002: Database Setup & SQLModel Models
- Create `models/task.py` with SQLModel Task class
- Create `models/user.py` with SQLModel User class (references Better Auth)
- Setup `database.py` for async SQLAlchemy connection (Neon)
- Create migration files for schema initialization
- Agent: `db-neon-sqlmodel`

### T-003: JWT Middleware & Authentication
- Create `api/middleware.py` with JWT verification logic
- Extract and validate user_id from JWT claims
- Setup FastAPI dependency injection for authenticated user_id
- Agent: `auth-security`

### T-004: Request/Response Schemas
- Create `api/schemas.py` with Pydantic models
- TaskCreate, TaskUpdate, TaskResponse, PaginatedResponse, ErrorResponse
- Validation rules for title, description, due_date, completed
- Agent: `fastapi-backend`

### T-005: Task Service Layer
- Create `services/task_service.py`
- Implement CRUD methods: create_task, get_task, list_tasks, update_task, delete_task, mark_complete
- All methods include user_id parameter for query scoping
- Agent: `fastapi-backend`

### T-006: API Endpoints (POST, GET List, GET Detail)
- Create endpoints for POST /api/{user_id}/tasks, GET /api/{user_id}/tasks, GET /api/{user_id}/tasks/{task_id}
- Implement 201 Created, 200 OK, 404 Not Found, 403 Forbidden responses
- Agent: `fastapi-backend`

### T-007: API Endpoints (PUT, PATCH, PATCH Complete, DELETE)
- Create endpoints for PUT, PATCH, PATCH complete, DELETE operations
- Implement partial update logic (PATCH) with Pydantic Optional fields
- Implement task completion toggle (PATCH /complete)
- Agent: `fastapi-backend`

### T-008: Error Handling & Validation
- Setup global FastAPI exception handlers
- Implement 400 Bad Request for invalid input
- Implement 401 Unauthorized for missing JWT
- Implement 403 Forbidden for ownership violations
- Implement 422 Unprocessable Entity with field-level error details
- Implement 500 Internal Server Error with correlation ID logging
- Agent: `fastapi-backend`

### T-009: Unit Tests - Service Layer
- Write tests for `TaskService` methods
- Mock database, test CRUD logic in isolation
- Test user_id filtering, validation, state transitions
- Target: >90% coverage of service layer
- Agent: `fastapi-backend`

### T-010: Integration Tests - API Endpoints
- Write tests for all 7 API endpoints
- Use test database (PostgreSQL test instance)
- Test success paths, error paths, ownership validation
- Test pagination, filtering, timestamp management
- Test concurrent requests, edge cases
- Target: >80% coverage of API layer
- Agent: `fastapi-backend`

### T-011: Contract Tests
- Validate OpenAPI spec matches implementation
- Validate error codes and status codes match spec
- Validate request/response schemas match spec
- Agent: `fastapi-backend`

### T-012: Documentation & Quickstart
- Generate OpenAPI spec (auto-generated by FastAPI)
- Write `quickstart.md` with curl examples for all 7 endpoints
- Document JWT token setup and test user creation
- Document error scenarios and debugging
- Agent: `fastapi-backend`

---

## Implementation Approach

### Agents & Skills Mapping

| Task | Primary Agent | Skills | Rationale |
|------|---------------|--------|-----------|
| T-001 | `fastapi-backend` | `backend-api` | FastAPI project setup |
| T-002 | `db-neon-sqlmodel` | `database-skill` | Database schema & models |
| T-003 | `auth-security` | `auth-skill` | JWT verification middleware |
| T-004 | `fastapi-backend` | `backend-api` | Pydantic validation |
| T-005 | `fastapi-backend` | `backend-api` | Service layer CRUD logic |
| T-006-007 | `fastapi-backend` | `backend-api` | Endpoint implementation |
| T-008 | `fastapi-backend` | `backend-api` | Error handling patterns |
| T-009-011 | `fastapi-backend` | `backend-api` | Test implementation |
| T-012 | `fastapi-backend` | `backend-api` | Documentation |

### Task Dependencies

```
T-001 (Setup)
  ↓
T-002 (DB Models) ← Must complete before T-005, T-006, T-007
  ↓
T-003 (JWT Middleware) ← Must complete before T-006, T-007
  ↓
T-004 (Schemas) ← Can run parallel with T-003, must complete before T-006, T-007
  ↓
T-005 (Service) ← Depends on T-002, can run parallel with T-006, T-007
  ↓
T-006, T-007 (Endpoints) ← Depends on T-002, T-003, T-004, T-005
  ↓
T-008 (Error Handling) ← Depends on T-006, T-007
  ↓
T-009, T-010, T-011 (Tests) ← Depends on T-006, T-007, T-008
  ↓
T-012 (Docs) ← Final task, depends on all above
```

### Optimal Implementation Sequence

1. **T-001**: Setup FastAPI project structure and environment
2. **T-002**: Create database models (SQLModel Task & User)
3. **T-003**: Implement JWT middleware (parallel with T-004 possible)
4. **T-004**: Define request/response schemas (Pydantic)
5. **T-005**: Implement TaskService with CRUD logic
6. **T-006**: Implement POST, GET list, GET detail endpoints
7. **T-007**: Implement PUT, PATCH, DELETE endpoints
8. **T-008**: Add error handling and validation
9. **T-009**: Write service layer unit tests
10. **T-010**: Write API integration tests
11. **T-011**: Validate API contract (OpenAPI)
12. **T-012**: Generate documentation and quickstart

---

## Acceptance Criteria

### All Tasks
- ✅ Code includes task comment references: `# [Task]: T-XXX, [From]: specs/001-task-crud-api/spec.md#FR-XXX`
- ✅ Code passes `ruff check` (Python linting) with no errors
- ✅ All dependencies properly declared in `requirements.txt`
- ✅ No secrets hardcoded; all config from `.env` or environment variables

### T-001-T-005 (Setup & Models)
- ✅ FastAPI app initializes without errors
- ✅ Database connection established to Neon
- ✅ SQLModel Task model has all required fields with validation
- ✅ JWT middleware correctly extracts and validates user_id
- ✅ Pydantic schemas enforce validation rules from spec

### T-006-T-007 (Endpoints)
- ✅ All 7 endpoints respond with correct HTTP status codes
- ✅ All endpoints require JWT token (401 without token)
- ✅ All endpoints check task ownership (403 if not owner)
- ✅ Request bodies validated (422 on invalid input)
- ✅ Response format matches spec exactly: `{ data: {...}, error: null }`
- ✅ Pagination works correctly (limit, offset, has_more, total)
- ✅ Timestamps (created_at, updated_at, completed_at) managed automatically

### T-008 (Error Handling)
- ✅ 400 Bad Request for malformed requests
- ✅ 401 Unauthorized for missing/expired JWT
- ✅ 403 Forbidden for ownership violations (not 404 to avoid leaking info)
- ✅ 404 Not Found for non-existent tasks
- ✅ 422 Unprocessable Entity with field-level error details
- ✅ 500 Internal Server Error with correlation ID

### T-009-T-011 (Testing & Quality)
- ✅ Minimum 70% code coverage (pytest --cov)
- ✅ All critical paths tested (happy path + error paths)
- ✅ Concurrent request handling tested
- ✅ Edge cases covered (empty lists, large datasets, etc.)
- ✅ OpenAPI spec validates against implementation
- ✅ All test imports working, no missing fixtures

### T-012 (Documentation)
- ✅ OpenAPI spec auto-generated and accessible at `/docs`
- ✅ `quickstart.md` has working curl examples for all 7 endpoints
- ✅ Documentation includes token setup and test user creation
- ✅ Error scenarios documented with expected responses

---

## Key Architectural Decisions

### 1. Async SQLAlchemy with SQLModel
**Decision**: Use SQLModel with async SQLAlchemy and asyncpg for Neon connections
**Rationale**: Enables non-blocking database queries, supports horizontal scaling, native to FastAPI
**Tradeoff**: Slightly more complex session management vs. simpler sync approach

### 2. Query-Level User Scoping
**Decision**: Every database query includes `WHERE user_id = :user_id` filter
**Rationale**: Enforces user data isolation at database layer (defense-in-depth), prevents authorization bypass
**Tradeoff**: Slightly more verbose query composition vs. simpler filter-free queries

### 3. Middleware-Based JWT Verification
**Decision**: JWT validation happens in middleware before reaching route handlers
**Rationale**: Centralized, ensures all endpoints protected, easy to test independently
**Tradeoff**: Cannot customize behavior per endpoint (acceptable for this use case)

### 4. Pydantic v2 Validation
**Decision**: Use Pydantic v2 with field validation, Optional fields for PATCH, custom validators
**Rationale**: Built-in to FastAPI, type-safe, automatic documentation, field-level error details
**Tradeoff**: Requires Pydantic v2 (not v1), more boilerplate than simple dicts

### 5. Standard Error Response Format
**Decision**: All responses follow `{ data: {...} | null, error: {...} | null }` structure
**Rationale**: Consistent client expectations, clear error vs. success distinction
**Tradeoff**: Slightly more verbose than bare error codes

### 6. Soft vs. Hard Deletes
**Decision**: Hard delete (permanent removal) in MVP, audit logging optional
**Rationale**: Simpler implementation, meets MVP requirements, can add soft deletes later
**Tradeoff**: No audit trail without separate logging layer

---

## Open Questions / Clarifications

1. **Better Auth Token Exchange**: How exactly does Better Auth frontend pass JWT to FastAPI backend? (Resolved in Phase 0 research)
2. **Neon Connection Pooling**: Should we use PgBouncer or rely on Neon's built-in connection pooling? (Resolved in Phase 0 research)
3. **Async Session Management**: Best practices for handling SQLModel async sessions in request-scoped dependency injection? (Resolved in Phase 0 research)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| JWT token expiration not handled | Users locked out | Frontend handles token refresh; backend returns 401 consistently |
| Cross-user data leakage | Security vulnerability | Query-level filtering + 403 (not 404) for ownership violations |
| Neon connection exhaustion | API outages | Connection pooling config + circuit breaker pattern in service layer |
| Concurrent updates to same task | Data inconsistency | Last-write-wins strategy (documented in assumption); consider optimistic locking in Phase 3 |
| Slow list queries on large datasets | Performance degradation | Index on (user_id, created_at); pagination enforced; cache optimization in Phase 3 |

---

## Next Steps

1. **Phase 0 Complete**: Run research on JWT patterns, async SQLModel, Neon pooling, Pydantic v2, error handling
2. **Phase 1 Complete**: Generate `data-model.md`, `contracts/openapi.yaml`, `quickstart.md`
3. **Run `/sp.tasks`**: Break Phase 2 tasks into granular, testable units with full dependencies
4. **Implementation**: Execute tasks via Claude Code agents in order, respecting dependencies
5. **Quality Gate**: Achieve 70%+ test coverage, pass linting, validate against spec

---

## Appendix: Constitution Alignment

**All design decisions above are aligned with the project constitution**:
- ✅ Spec-first: This plan references spec sections (e.g., FR-001, FR-017)
- ✅ Spec-driven code: All generated code will include `[Task]: T-XXX, [From]: specs/...` comments
- ✅ JWT + Better Auth: Middleware validates tokens, no plain-text secrets
- ✅ Data isolation: Query-level user_id filtering enforced
- ✅ Stateless services: No in-memory sessions, all state in Neon
- ✅ Clean architecture: Models / Services / API layers separated
- ✅ Test-driven: 70%+ coverage required
- ✅ Type-safe: Pydantic v2 validation, strict types
