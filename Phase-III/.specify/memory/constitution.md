# Phase II & III: Full-Stack Todo Application Constitution

<!--
Sync Impact Report:
Version: 1.0.0 → 1.1.0 (Phase-III additions)
Modified Principles: None (Phase-II principles unchanged)
Added Sections: Phase-III Additions (AI Chatbot Integration)
Removed Sections: None
Templates Requiring Updates:
  - ⚠ .specify/templates/plan-template.md (validate Phase-III architecture patterns)
  - ⚠ .specify/templates/spec-template.md (validate Phase-III feature requirements)
  - ⚠ .specify/templates/tasks-template.md (validate Phase-III task categories)
  - ⚠ .specify/templates/commands/*.md (validate Phase-III workflow)
Follow-up TODOs:
  - Validate MCP server configuration in deployment specs
  - Update API documentation to include chat endpoint
  - Add ChatKit domain allowlist to environment configuration
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

---

# Phase-III Additions

## VII. AI Chatbot Integration (NON-NEGOTIABLE)

Phase-III extends the application with natural language todo management via AI chatbot:

### Objective

Build an AI-powered chatbot interface that allows users to manage todos through natural language conversations while maintaining all Phase-II security and architecture principles.

### Technology Stack Extensions

**Frontend AI Components**:
- **OpenAI ChatKit**: Pre-built chat UI components for conversational interface
- **Integration**: Embedded within existing dashboard, accessible via chat icon/button
- **Styling**: Dark mode default, shadcn/ui styling for consistency

**Backend AI Components**:
- **OpenAI Agents SDK**: Agent orchestration and tool execution
- **Official MCP SDK**: Model Context Protocol server implementation
- **Architecture**: Stateless chat endpoint with database-persisted conversation state

### MCP Server Requirements (NON-NEGOTIABLE)

The backend MUST expose an MCP server with exactly 5 tools matching core todo operations:

1. **add_task**: Create new task (title, description)
2. **list_tasks**: Retrieve tasks with optional filtering (all/pending/completed)
3. **complete_task**: Mark task as complete/incomplete
4. **delete_task**: Remove task permanently
5. **update_task**: Edit task title and/or description

**Security Constraints**:
- ALL tools MUST filter by `user_id` extracted from JWT token
- NO cross-user data access permitted
- Tool execution MUST validate user ownership before any operation
- Failed authorization MUST return clear error messages

**Rationale**: MCP tools provide structured, type-safe interfaces for AI agents to interact with todo operations while enforcing user-scoped security at the tool level.

### Chat Endpoint Architecture (NON-NEGOTIABLE)

**Endpoint**: `POST /api/chat`

**Design Principles**:
- **Stateless**: No server-side session storage; all state in database
- **Conversation Persistence**: Store full conversation history in database
- **User Isolation**: Conversations scoped to authenticated user via JWT

**Request Flow**:
1. Frontend sends user message + conversation_id (optional for new conversations)
2. Backend validates JWT and extracts user_id
3. Load conversation history from database (if existing conversation)
4. OpenAI Agents SDK processes message with MCP tools available
5. Agent executes tools (filtered by user_id) and generates response
6. Save user message + assistant response to database
7. Return assistant response to frontend

**Database Models** (MUST be added):

```python
class Conversation(SQLModel, table=True):
    id: int (primary key)
    user_id: int (foreign key to users)
    title: str (auto-generated from first message)
    created_at: datetime
    updated_at: datetime

class Message(SQLModel, table=True):
    id: int (primary key)
    conversation_id: int (foreign key to conversations)
    role: str (enum: "user" | "assistant")
    content: str (message text)
    tool_calls: Optional[str] (JSON array of tool executions)
    created_at: datetime
```

**Rationale**: Database-persisted conversations enable multi-turn context, conversation history viewing, and audit trails while maintaining stateless backend architecture.

### ChatKit Configuration (NON-NEGOTIABLE)

**Domain Allowlist**:
- ChatKit MUST be configured with allowed domains for hosted UI
- Local development: `http://localhost:3000`
- Production: Actual deployment domain (e.g., `https://app.example.com`)

**UI Integration**:
- Chat interface accessible via floating button or sidebar tab in dashboard
- Full-screen chat view option for extended conversations
- Message history scrollable with timestamps
- Loading states during tool execution
- Error handling for failed tool calls

**Styling Requirements**:
- Dark mode default (matching Phase-II standards)
- shadcn/ui components for buttons, inputs, cards
- Lucide Icons for chat-related icons (send, history, etc.)
- Responsive design (mobile-first)

**Rationale**: ChatKit provides production-ready chat UI with minimal custom code, but requires proper domain configuration for security and CORS compliance.

### Development Workflow Extensions

**Spec-Driven Development for Phase-III**:
1. All Phase-III features MUST have specs in `specs/features/phase3-*`
2. MCP tool definitions MUST be documented in `specs/api/mcp-tools.md`
3. Chat endpoint specification MUST be in `specs/api/chat-endpoint.md`
4. Database schema changes MUST be in `specs/database/phase3-schema.md`

**Testing Requirements**:
- **MCP Tools**: Unit tests for each tool with user_id filtering validation
- **Chat Endpoint**: Integration tests with mock OpenAI responses
- **Security**: Tests verifying cross-user data isolation
- **E2E**: Playwright tests for chat UI interactions

**Prohibited Actions**:
- Implementing chat features beyond natural language todo management
- Adding AI capabilities not related to the 5 core todo operations
- Storing conversation state in memory/cache (MUST use database)
- Bypassing user_id filtering in any tool

### Quality Gates (Phase-III Additions)

Before merging Phase-III features, ALL must pass:
- ✅ All Phase-II quality gates (tests, types, linting, constitution, spec)
- ✅ MCP server tools validated with user_id filtering
- ✅ Chat endpoint returns responses within 5 seconds (p95)
- ✅ Conversation persistence verified in database
- ✅ ChatKit domain allowlist configured correctly
- ✅ No AI hallucinations causing incorrect todo operations

### Governance (Phase-III)

**Amendment Process**:
- Phase-III additions follow same governance as Phase-II
- AI model changes (e.g., switching from OpenAI to Anthropic) require MAJOR version bump
- MCP tool additions/removals require MINOR version bump
- ChatKit configuration changes require PATCH version bump

**Compliance**:
- Phase-III features MUST NOT violate Phase-II principles
- All Phase-II security, architecture, and testing standards apply
- Spec-Driven Development with Claude Code + Spec-Kit Plus is mandatory

---

**Version**: 1.1.0 | **Ratified**: 2026-02-09 | **Last Amended**: 2026-02-11
