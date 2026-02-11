# Phase II: Full-Stack Todo Application Constitution

<!--
Sync Impact Report:
Version: NEW → 1.0.0 (Initial constitution)
Modified Principles: N/A (initial creation)
Added Sections: All sections (initial creation)
Removed Sections: None
Templates Requiring Updates:
  - ✅ .specify/templates/plan-template.md (to be validated)
  - ✅ .specify/templates/spec-template.md (to be validated)
  - ✅ .specify/templates/tasks-template.md (to be validated)
  - ✅ .specify/templates/commands/*.md (to be validated)
Follow-up TODOs: None
-->

## Core Principles

### I. Locked Tech Stack (NON-NEGOTIABLE)

All technology versions are fixed and MUST NOT be changed without constitutional amendment:

- **Frontend**: Next.js 16.1.6 (App Router + TypeScript), shadcn/ui, Tailwind CSS, Lucide Icons, TanStack Query v5
- **Backend**: FastAPI 0.128.5, SQLModel 0.0.32, UV package manager, Python 3.13+
- **Authentication**: Better Auth 1.4.18 with JWT tokens
- **Database**: Neon Serverless PostgreSQL
- **Deployment**: Docker Compose for local development

**Rationale**: Version locking prevents dependency conflicts, ensures reproducibility, and eliminates "works on my machine" issues during hackathon evaluation. Any version change requires full regression testing and constitutional amendment.

### II. Feature Scope Discipline (NON-NEGOTIABLE)

The application MUST implement exactly 5 core features—no more, no less:

1. **Add Task**: Create new task with title and description
2. **View Tasks**: Display all tasks with filtering (All/Pending/Completed)
3. **Update Task**: Edit existing task title and description
4. **Delete Task**: Remove task permanently
5. **Mark Complete/Incomplete**: Toggle task completion status

**Prohibited Actions**:
- Adding features not listed above (tags, priorities, due dates, attachments, etc.)
- Implementing "nice-to-have" enhancements
- Building admin panels, analytics, or reporting features

**Rationale**: Scope discipline ensures timely delivery, prevents feature creep, and maintains focus on core functionality. Every feature request MUST be rejected unless it directly supports one of the 5 core features.

### III. User-Scoped Security (NON-NEGOTIABLE)

Every authenticated user MUST see only their own tasks:

- **Authentication**: Better Auth handles email/password + optional Google OAuth
- **Authorization**: FastAPI backend validates JWT tokens on every request
- **Data Isolation**: Database queries MUST filter by `user_id` from JWT claims
- **Session Management**: JWT tokens stored securely (httpOnly cookies preferred)

**Security Requirements**:
- No task data leakage between users
- All API endpoints require valid JWT (except public landing page)
- SQL injection prevention via SQLModel parameterized queries
- CORS configured for frontend origin only

**Rationale**: User data privacy is non-negotiable. A single data leak violates user trust and hackathon evaluation criteria.

### IV. UI/UX Standards (NON-NEGOTIABLE)

The application MUST implement the exact UI specification:

**1. Public Landing Page (`/`)**:
- Dark modern hero section with large headline
- Phone mockup displaying dashboard preview
- Features section with 3-4 cards
- Final CTA button redirecting to `/login`
- Clean SaaS aesthetic (Opal/Linear inspired)

**2. Login & Signup Page (`/login`)**:
- Centered card with dark gradient background
- Toggle between login/signup forms
- Better Auth integration

**3. Dashboard (`/dashboard`)**:
- **Left Sidebar**: All Tasks | Pending | Completed filters
- **Top Navbar**: Logo + Search + "+ Add Task" button + User avatar + Logout
- **Main Area**: Responsive task grid

**4. Task Card (shadcn Card component)**:
- Left: Checkbox for completion toggle
- Title (bold) + truncated description
- Status badge (Pending = orange, Completed = green)
- Hover state: Edit & Delete icons appear

**Global Standards**:
- Dark mode default (no light mode toggle)
- shadcn/ui components exclusively
- Lucide Icons for all iconography
- Responsive design (mobile-first)

**Rationale**: Consistent UI/UX ensures professional appearance and meets hackathon design criteria. Deviations create visual inconsistency and waste development time.

### V. Clean Architecture

The codebase MUST follow separation of concerns:

**Monorepo Structure**:
```
hackathon-todo/
├── .spec-kit/config.yaml
├── specs/
│   ├── overview.md
│   ├── features/
│   ├── api/
│   ├── database/
│   └── ui/
├── frontend/ (Next.js app)
│   ├── app/ (App Router pages)
│   ├── components/ (shadcn/ui + custom)
│   ├── lib/ (utilities, API client)
│   └── hooks/ (TanStack Query hooks)
├── backend/ (FastAPI)
│   ├── app/
│   │   ├── api/ (route handlers)
│   │   ├── models/ (SQLModel schemas)
│   │   ├── services/ (business logic)
│   │   └── auth/ (JWT validation)
│   └── tests/
├── CLAUDE.md (root + frontend + backend)
├── docker-compose.yml
└── README.md
```

**Architectural Rules**:
- **Frontend**: React Server Components where possible, Client Components only when needed (interactivity, hooks)
- **Backend**: Layered architecture (routes → services → models)
- **API**: RESTful conventions, JSON responses, proper HTTP status codes
- **Database**: SQLModel for type-safe ORM, migrations via Alembic
- **State Management**: TanStack Query for server state, React Context for UI state only

**Rationale**: Clean architecture improves maintainability, testability, and onboarding speed. Mixing concerns creates technical debt.

### VI. Test-First Development (NON-NEGOTIABLE)

TDD cycle MUST be followed for all features:

1. **Red**: Write failing tests first (unit + integration)
2. **Green**: Implement minimum code to pass tests
3. **Refactor**: Improve code while keeping tests green

**Testing Requirements**:
- **Backend**: pytest for unit tests, TestClient for API integration tests
- **Frontend**: Vitest for unit tests, Playwright for E2E tests
- **Coverage**: Minimum 80% for business logic (services, API routes)
- **CI/CD**: All tests MUST pass before merge

**Test Categories**:
- Unit tests: Individual functions, components
- Integration tests: API endpoints with database
- E2E tests: Critical user flows (login → add task → mark complete → delete)

**Rationale**: Tests prevent regressions, document behavior, and enable confident refactoring. Skipping tests creates fragile code.

## Technology Constraints

### Locked Dependencies

**Frontend (`frontend/package.json`)**:
```json
{
  "dependencies": {
    "next": "16.1.6",
    "@tanstack/react-query": "^5.0.0",
    "better-auth": "1.4.18",
    "lucide-react": "latest",
    "tailwindcss": "latest"
  }
}
```

**Backend (`backend/pyproject.toml`)**:
```toml
[project]
dependencies = [
    "fastapi==0.128.5",
    "sqlmodel==0.0.32",
    "uvicorn[standard]>=0.30.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "psycopg[binary]>=3.1.0"
]
```

### Environment Variables

**Required `.env` variables**:
```
# Database
DATABASE_URL=postgresql://...

# Auth
BETTER_AUTH_SECRET=...
BETTER_AUTH_URL=http://localhost:3000

# Backend
BACKEND_URL=http://localhost:8000
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
```

**Prohibited**: Hardcoded secrets, API keys in source code, committed `.env` files.

## Development Workflow

### Spec-Driven Development

1. **Specification**: Write `specs/<feature>/spec.md` with requirements
2. **Planning**: Create `specs/<feature>/plan.md` with architecture decisions
3. **Tasks**: Generate `specs/<feature>/tasks.md` with testable acceptance criteria
4. **Implementation**: Follow Red-Green-Refactor cycle
5. **Review**: Verify against spec and constitution compliance

### Git Workflow

- **Branch Naming**: `feature/<feature-name>`, `fix/<bug-name>`
- **Commits**: Conventional Commits format (`feat:`, `fix:`, `docs:`, `test:`)
- **PRs**: Must reference spec, include tests, pass CI checks
- **Main Branch**: Protected, requires PR approval

### Quality Gates

Before merging, ALL must pass:
- ✅ All tests passing (unit + integration + E2E)
- ✅ No TypeScript/Python type errors
- ✅ Linting passes (ESLint, Ruff)
- ✅ Constitution compliance verified
- ✅ Spec requirements met

## Governance

### Amendment Process

1. **Proposal**: Document proposed change with rationale
2. **Impact Analysis**: Identify affected code, specs, templates
3. **Approval**: Team consensus required
4. **Migration**: Update all dependent artifacts
5. **Version Bump**: Increment constitution version (semantic versioning)

### Version Semantics

- **MAJOR (X.0.0)**: Breaking changes (principle removal, tech stack change)
- **MINOR (0.X.0)**: New principles, expanded guidance
- **PATCH (0.0.X)**: Clarifications, typo fixes, non-semantic changes

### Compliance

- All PRs MUST verify constitution compliance
- Complexity MUST be justified against principles
- Violations MUST be rejected or amended via governance process
- Use `CLAUDE.md` files for runtime development guidance

### Enforcement

Constitution supersedes all other practices. When conflicts arise:
1. Constitution principles take precedence
2. Spec requirements must align with constitution
3. Implementation must satisfy both constitution and spec
4. Deviations require constitutional amendment

**Version**: 1.0.0 | **Ratified**: 2026-02-09 | **Last Amended**: 2026-02-09
