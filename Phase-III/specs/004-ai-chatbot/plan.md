# Implementation Plan: Phase-III AI Todo Chatbot

**Branch**: `004-ai-chatbot` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/004-ai-chatbot/spec.md`
**Status**: Complete Architecture Design | **Architecture Documents**: See `ARCHITECTURE.md`, `IMPLEMENTATION_SUMMARY.md`

## Summary

Phase-III AI Chatbot integrates OpenAI Agents SDK with MCP-first tool architecture into the existing Phase-II Full-Stack Todo Application. The chatbot provides natural language task management (create, list, update, complete, delete) through a floating UI widget, with full conversation persistence in Neon PostgreSQL. Core design: **Stateless backend + database-backed conversations + MCP tools + JWT-scoped user isolation**. Zero Phase-II modifications. 5 implementation phases across 7-8 days (optimized parallel execution).

## Technical Context

**Backend Language/Version**: Python 3.13+ (FastAPI)
**Frontend Language/Version**: TypeScript (Next.js 16+ with App Router)
**Primary Dependencies**:
  - Backend: FastAPI, SQLModel, Pydantic, openai (Agents SDK), alembic
  - Frontend: React, TypeScript, Tailwind CSS, ChatKit or custom chat component
  - Database: Neon PostgreSQL (serverless)
  - Authentication: JWT tokens, Better Auth (shared with Phase-II)

**Storage**: Neon PostgreSQL
  - Existing tables: users, tasks (Phase-II)
  - New tables: conversations, messages (Phase-III)
  - Indexes: (user_id, created_at), (conversation_id, created_at)

**Testing**: pytest (backend), vitest (frontend), integration tests for end-to-end flows

**Target Platform**: Web (browser + FastAPI backend)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
  - Chat response time: < 3 seconds (p95)
  - Task appearance in UI: < 1 second
  - Page load impact: < 500ms
  - Concurrent users supported: 100+

**Constraints**:
  - Stateless backend (no in-memory conversation state)
  - Database persistence for all messages (100% recovery on server restart)
  - JWT validation on every request
  - User isolation: all queries filtered by user_id
  - Confirmation required for write operations (add, update, complete, delete)
  - Zero Phase-II API modifications or code duplication

**Scale/Scope**:
  - 7 user stories (P1: Create, List, Persistence, Isolation; P2: Update, Complete, Delete)
  - 22 functional requirements
  - 2 new database tables
  - 1 new FastAPI endpoint (chat messages)
  - 5 MCP tools (add_task, list_tasks, update_task, complete_task, delete_task)
  - 1 new frontend component (floating chat widget)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Phase-III Constitution Alignment** (v3.0.0):

- ✅ **P3.1: Full-Stack Integration Only**
  - Design reuses Phase-II backend, database, authentication
  - No parallel backend, no duplicate task CRUD logic
  - MCP tools call existing `/api/users/{user_id}/tasks/*` endpoints
  - No modifications to Phase-II APIs

- ✅ **P3.2: OpenAI-Only AI Stack**
  - OpenAI API key as sole credential
  - OpenAI Agents SDK for orchestration
  - GPT-4-turbo model (or later)
  - No Gemini, Claude, Grok alternatives

- ✅ **P3.3: MCP-First Tool Architecture**
  - Stateless MCP server (FastAPI-based)
  - 5 tools: add_task, list_tasks, update_task, complete_task, delete_task
  - All tool calls user_id scoped
  - Tool invocation only after confirmation (except read-only list)

- ✅ **P3.4: Conversational Safety Rules**
  - Intent detection ≠ execution
  - Step-by-step data collection before tool invocation
  - Confirmation required: FR-003, FR-007, FR-016
  - No auto-execution of writes without "yes"

- ✅ **P3.5: Stateless Backend, Persistent Memory**
  - Backend endpoints stateless (no session store)
  - Conversation history in database (100% recovery on restart)
  - Messages linked to user_id
  - Full history loaded on each request

- ✅ **P3.6: Secure User Context**
  - JWT required on every chat request (FR-011)
  - user_id extracted and passed to tools (FR-017)
  - All queries filtered by user_id (FR-018)
  - 403 Forbidden on cross-user access (FR-019, not 404)

- ✅ **P3.7: Embedded Chat UI (No New Routes)**
  - Floating widget, bottom-right corner (FR-013)
  - No new pages or routes (embedded in layout)
  - Authenticated users only (FR-012)
  - Smooth animations (FR-014)

- ✅ **P3.8: Database Extensions Only**
  - conversations table (new)
  - messages table (new)
  - No modifications to users or tasks tables

- ✅ **P3.9: OpenAI Agents Integration**
  - Agents SDK handles multi-turn reasoning
  - Tool calls parsed and executed
  - Message array built from database history
  - Response stored in database

- ✅ **P3.10: Forbidden Actions**
  - ✅ No Phase-II API modifications
  - ✅ No direct DB writes by AI (MCP tools only)
  - ✅ No in-memory chat state
  - ✅ No auto task creation without confirmation

- ✅ **P3.11: Success Metrics**
  - All 12 success criteria (SC-001 to SC-012) addressed in design
  - 7 user stories mapped to implementation phases
  - Zero Phase-II regression guaranteed

**GATE STATUS**: ✅ **PASS** - Design fully compliant with Phase-III constitution. All 11 principles honored.

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

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

## Project Structure

### Documentation (this feature)

```text
specs/004-ai-chatbot/
├── spec.md                              # Feature specification (7 stories, 22 requirements, 12 success criteria)
├── plan.md                              # This file (implementation architecture)
├── ARCHITECTURE.md                      # Deep-dive architectural design (50+ pages)
├── IMPLEMENTATION_SUMMARY.md            # Quick reference guide
├── checklists/
│   └── requirements.md                  # Quality assurance checklist (PASS ✅)
└── contracts/                           # API contracts (generated in Phase 1)
    ├── chat-endpoint.md                 # POST /api/v1/chat/conversations/{id}/messages
    └── mcp-tools.md                     # MCP tool schemas (input/output)
```

### Source Code Structure

**Backend** (Python FastAPI - existing structure):
```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py                      # Existing (Phase-II)
│   │   ├── user.py                      # Existing (Phase-II)
│   │   ├── conversation.py              # NEW: Conversation model
│   │   └── message.py                   # NEW: Message model
│   ├── services/
│   │   ├── task_service.py              # Existing (Phase-II) - REUSED
│   │   ├── conversation_service.py      # NEW: Conversation CRUD
│   │   └── message_service.py           # NEW: Message persistence
│   ├── api/
│   │   ├── users/tasks.py               # Existing (Phase-II) - REUSED
│   │   └── chat.py                      # NEW: POST /api/v1/chat/...
│   ├── mcp/                             # NEW: MCP Server
│   │   ├── server.py                    # MCP SDK server
│   │   ├── tools.py                     # 5 task tools
│   │   └── schemas.py                   # Tool input/output schemas
│   └── agents/                          # NEW: OpenAI Integration
│       ├── factory.py                   # Agent initialization
│       ├── tools.py                     # Tool binding to MCP
│       └── prompts.py                   # System prompts
├── alembic/
│   └── versions/
│       ├── 001_create_conversations.py  # NEW: Database migration
│       └── 002_create_messages.py       # NEW: Database migration
└── tests/
    ├── integration/
    │   ├── test_chat_flow.py            # NEW: End-to-end chat tests
    │   └── test_user_isolation.py       # NEW: Multi-user isolation tests
    └── unit/
        ├── test_mcp_tools.py            # NEW: MCP tool unit tests
        └── test_agent_reasoning.py      # NEW: Agent response tests
```

**Frontend** (Next.js - existing structure):
```text
frontend/
├── src/
│   ├── components/
│   │   ├── ChatWidget.tsx               # NEW: Floating chat widget
│   │   └── ChatWindow.tsx               # NEW: Chat message display
│   ├── hooks/
│   │   └── useChat.ts                   # NEW: Chat state management hook
│   ├── services/
│   │   └── chatApi.ts                   # NEW: Chat API client
│   └── app/
│       └── [locale]/
│           └── layout.tsx               # Modified: Import ChatWidget
└── tests/
    ├── integration/
    │   └── test_chat_widget.test.tsx    # NEW: Widget integration tests
    └── unit/
        └── test_useChat.test.ts         # NEW: Hook unit tests
```

**Structure Decision**: Web application with separate frontend (Next.js) and backend (FastAPI). Existing directory structure preserved; new feature code added without modifying Phase-II files.

---

## Implementation Phases

### Phase 1: Database Schema & Migrations (Days 1-2)

**Deliverables**:
- Conversations table with indexes
- Messages table with indexes
- Alembic migrations (reversible)
- SQLModel ORM models

**Key Files**:
- `backend/src/models/conversation.py`
- `backend/src/models/message.py`
- `backend/alembic/versions/001_create_conversations.py`
- `backend/alembic/versions/002_create_messages.py`

**Tasks**:
- Design conversation schema (id, user_id, title, created_at, updated_at, deleted_at)
- Design message schema (id, conversation_id, user_id, role, content, created_at, metadata)
- Create indexes: (user_id, created_at), (conversation_id, created_at)
- Write SQLModel models with validation
- Test migrations: create, rollback, re-create

**Success Criteria**: Schema matches spec, indexes optimize queries, migrations reversible, zero Phase-II impact

---

### Phase 2: MCP Server & Tool Implementation (Days 2-4)

**Deliverables**:
- Stateless MCP server (FastAPI-based)
- 5 task tools (add, list, update, complete, delete)
- Tool validation and error handling
- Tool contracts (schemas)

**Key Files**:
- `backend/src/mcp/server.py`
- `backend/src/mcp/tools.py`
- `backend/src/mcp/schemas.py`
- `specs/004-ai-chatbot/contracts/mcp-tools.md`

**Tasks**:
- Initialize MCP SDK in FastAPI
- Implement add_task tool (calls POST /api/users/{user_id}/tasks)
- Implement list_tasks tool (calls GET /api/users/{user_id}/tasks with filters)
- Implement update_task tool (calls PUT /api/users/{user_id}/tasks/{task_id})
- Implement complete_task tool (calls PATCH /api/users/{user_id}/tasks/{task_id}/complete)
- Implement delete_task tool (calls DELETE /api/users/{user_id}/tasks/{task_id})
- Add parameter validation (required fields, user_id scoping)
- Add error handling (tool errors return user-friendly messages)
- Write unit tests for each tool
- Document tool schemas (input/output)

**Success Criteria**: All 5 tools callable, parameters validated, user_id scoped, Phase-II endpoints reused, 70%+ coverage

---

### Phase 3: Chat Endpoint & Agent Integration (Days 3-5)

**Deliverables**:
- FastAPI chat endpoint (POST /api/v1/chat/conversations/{id}/messages)
- OpenAI Agents SDK integration
- Message array builder from database
- Tool execution and response handling

**Key Files**:
- `backend/src/api/chat.py`
- `backend/src/agents/factory.py`
- `backend/src/agents/tools.py`
- `backend/src/services/conversation_service.py`
- `backend/src/services/message_service.py`
- `specs/004-ai-chatbot/contracts/chat-endpoint.md`

**Tasks**:
- Create FastAPI endpoint: `POST /api/v1/chat/conversations/{conversation_id}/messages`
- Implement JWT validation (extract user_id from token)
- Implement message array builder (fetch history from DB, ordered by created_at)
- Initialize OpenAI Agents SDK with system prompt
- Bind MCP tools to agent
- Implement agent execution loop (message → agent → tool call → store → response)
- Implement tool call parsing (extract tool name, parameters)
- Implement tool execution (call MCP tool with user_id)
- Implement error handling (tool errors, agent errors, network errors)
- Store user message and assistant response in database
- Return response to client with 200 status
- Write integration tests (end-to-end chat flows)
- Write security tests (JWT validation, user isolation)

**Success Criteria**: Endpoint works end-to-end, agent reasoning sound, tool calls execute correctly, messages persist, 70%+ coverage

---

### Phase 4: Frontend Chat Widget (Days 4-6)

**Deliverables**:
- Floating chat widget (bottom-right corner)
- Chat message display and input
- OpenAI ChatKit or custom React component
- Client-side chat state management
- Integration with chat endpoint

**Key Files**:
- `frontend/src/components/ChatWidget.tsx`
- `frontend/src/components/ChatWindow.tsx`
- `frontend/src/hooks/useChat.ts`
- `frontend/src/services/chatApi.ts`
- `frontend/src/app/[locale]/layout.tsx` (modified)

**Tasks**:
- Create ChatWidget component (Client Component with 'use client')
- Implement floating position (bottom-right, fixed)
- Implement open/close animation (CSS transitions)
- Create ChatWindow component (message list + input)
- Implement message rendering (user vs assistant styling)
- Create useChat hook (manage conversation state, message sending)
- Implement chat API client (POST to /api/v1/chat/conversations/{id}/messages)
- Implement JWT token passing (Authorization header)
- Implement conversation persistence (load history on mount)
- Implement auto-scroll to latest message
- Add loading states and error messages
- Integrate into root layout (lazy load ChatWidget)
- Write component unit tests
- Write integration tests (widget interaction with backend)

**Success Criteria**: Widget loads correctly, smooth animations, messages display, backend integration works, <500ms page load impact, 70%+ coverage

---

### Phase 5: Testing, Security & Validation (Days 5-8)

**Deliverables**:
- Comprehensive test suite (70%+ coverage)
- Security validation (user isolation, JWT, 403 errors)
- Performance testing (< 3 second response time)
- Integration tests (Phase-II compatibility)
- Documentation and deployment guide

**Key Files**:
- `backend/tests/integration/test_chat_flow.py`
- `backend/tests/integration/test_user_isolation.py`
- `backend/tests/unit/test_mcp_tools.py`
- `frontend/tests/integration/test_chat_widget.test.tsx`
- `specs/004-ai-chatbot/IMPLEMENTATION_SUMMARY.md` (updated)

**Tasks**:
- Write integration tests for all 7 user stories (Create, List, Update, Complete, Delete, Persistence, Isolation)
- Write security tests: JWT validation, user isolation (User A cannot see User B's data), 403 errors
- Write performance tests: response time < 3 seconds, task appearance < 1 second
- Run Phase-II regression tests (verify no API changes, zero breaking changes)
- Test conversation resumption (create → close → reopen → messages present)
- Test error handling (network errors, invalid input, tool errors)
- Test concurrent users (horizontal scaling, no session affinity needed)
- Generate coverage report (target ≥ 70%)
- Create deployment guide
- Document known issues and workarounds
- Finalize implementation summary

**Success Criteria**: All tests pass, 70%+ coverage, zero Phase-II regression, security validated, performance targets met

---

## Technical Decisions & Tradeoffs

### Decision 1: Database-Backed Conversations vs. In-Memory State
- **Chosen**: Database-backed (Neon PostgreSQL)
- **Rationale**: Enables stateless backend, 100% recovery on restart, horizontal scaling
- **Alternative Considered**: Redis for message caching
- **Tradeoff**: Slightly higher latency vs. guaranteed persistence

### Decision 2: OpenAI Agents SDK vs. Custom Agent Loop
- **Chosen**: OpenAI Agents SDK
- **Rationale**: Native tool support, multi-turn reasoning, maintained by OpenAI
- **Alternative Considered**: Custom agent loop with OpenAI API
- **Tradeoff**: Vendor lock-in vs. simplified development

### Decision 3: MCP-First Tools vs. Direct API Calls
- **Chosen**: MCP-first (AI calls MCP tools)
- **Rationale**: Enforces user isolation, no bypass of security, decouples AI from business logic
- **Alternative Considered**: AI directly calls FastAPI endpoints
- **Tradeoff**: Extra abstraction layer vs. security & flexibility

### Decision 4: Token Window of 20 Messages
- **Chosen**: Last 20 messages in agent context
- **Rationale**: Balances context quality vs. token cost (20 messages ≈ 2-3K tokens)
- **Alternative Considered**: Full conversation history or sliding window
- **Tradeoff**: Limited long-term context vs. cost control

### Decision 5: Confirmation Gates (Yes/No Before Execution)
- **Chosen**: Mandatory confirmation for write operations
- **Rationale**: Prevents accidental task deletion, builds user trust, aligns with P3.4 constitution
- **Alternative Considered**: AI auto-executes after high confidence
- **Tradeoff**: Extra step in conversation vs. safety

---

## Success Criteria Mapping

| Success Criterion | How Achieved | Test Case |
|-------------------|-------------|-----------|
| SC-001: Task creation < 90 seconds | 5-6 turn conversation + API call | Measure time from "create task" to confirmation |
| SC-002: 95% of tasks appear in UI within 1 second | Messages stored immediately, UI fetches fresh list | Create task, check UI without refresh |
| SC-003: Conversation persists across refresh | Messages in DB, loaded on each request | Create conversation, refresh, verify history |
| SC-004: Filters match Phase-II API results | MCP tool calls existing `/api/.../tasks` | Compare filtered results in chatbot vs. UI |
| SC-005: Updates visible in UI within 1 second | Messages stored, UI queries fresh data | Update priority, check UI without refresh |
| SC-006: 100% prevention of accidental deletes | Mandatory confirmation ("yes") required | Refuse delete, verify task remains |
| SC-007: Zero cross-user data leaks | user_id scoping on all queries, 403 errors | User A cannot list User B's tasks or conversations |
| SC-008: Response time < 3 seconds | Agent + tool execution + DB store | Measure end-to-end time with load testing |
| SC-009: Widget adds < 500ms to page load | Lazy load ChatKit, async initialization | Measure page load time with/without widget |
| SC-010: 90% user intuitiveness | Intuitive UI, clear conversations, helpful error messages | User testing, feedback collection |
| SC-011: 70%+ test coverage | Comprehensive unit + integration tests | Coverage report from pytest/vitest |
| SC-012: Zero Phase-II regression | All Phase-II tests pass, no API changes | Run full Phase-II test suite |

---

## Risk Analysis & Mitigation

### Risk 1: Token Window Overflow (Conversation Exceeds Context)
**Severity**: Medium | **Probability**: Medium | **Blast Radius**: Agent loses context, poor responses

**Mitigation**:
- Limit agent context to last 20 messages (CLARIFICATION-002 from spec)
- Implement message summarization (optional Phase-IV)
- Log warnings when conversation exceeds threshold
- Graceful degradation: older messages available from DB, not in agent context

**Kill Switch**: If agent becomes incoherent, truncate to last 10 messages; user can refresh to reset

---

### Risk 2: Cross-User Data Leakage via Tool Call
**Severity**: Critical | **Probability**: Low | **Blast Radius**: Major security breach, data exposure

**Mitigation**:
- Enforce user_id scoping on EVERY tool call (not just in database query)
- Tool parameter validation: verify user_id from JWT matches request
- Unit test: each tool with User A's token cannot access User B's tasks
- Return 403 Forbidden (not 404) to avoid leaking existence of other users' resources
- Log all cross-user access attempts for audit trail

**Kill Switch**: If data leakage detected, immediately disable chat endpoint, notify security team

---

### Risk 3: Tool Timeout (Agent Waits Indefinitely for Tool Response)
**Severity**: Medium | **Probability**: Low | **Blast Radius**: Chat hangs, poor user experience

**Mitigation**:
- Set 5-10 second timeout on MCP tool execution (CLARIFICATION-001 from spec)
- Return user-friendly error after timeout: "I'm having trouble completing that action. Please try again."
- Log timeout events for debugging
- Implement retry mechanism (agent can retry tool call)

**Kill Switch**: If timeouts exceed threshold, disable problematic tool, notify team

---

### Risk 4: Database Connection Pool Exhaustion
**Severity**: Medium | **Probability**: Low | **Blast Radius**: Chat endpoint unavailable under load

**Mitigation**:
- Configure connection pooling (e.g., pgbouncer for Neon)
- Monitor connection pool usage
- Implement backpressure: queue requests if pool exhausted
- Use async queries (FastAPI async drivers)
- Test with 100+ concurrent users

**Kill Switch**: If pool exhausted, fallback to read-only mode; drain queue before resuming writes

---

### Risk 5: AI Hallucination (Agent Invokes Non-Existent Task)
**Severity**: Low | **Probability**: Medium | **Blast Radius**: Error message returned, no data corruption

**Mitigation**:
- Agent system prompt: "Only reference tasks from the list_tasks result"
- Tool validation: delete_task and update_task verify task exists before execution
- Return user-friendly error: "I couldn't find that task. Did you mean: [list options]?"
- Agent can recover: ask user for clarification, retry with correct task ID

**Kill Switch**: None needed; errors are handled gracefully, no data corruption

---

## Effort Estimation & Timeline

**Optimized Parallel Execution** (2-3 engineers):

| Phase | Duration | Effort | Team |
|-------|----------|--------|------|
| Phase 1: Database Schema | 2 days | 16 hours | Backend Lead |
| Phase 2: MCP Server & Tools | 2 days (parallel with Phase 1 after day 1) | 16 hours | Backend Engineer |
| Phase 3: Chat Endpoint & Agent | 2 days (parallel with Phase 2 after day 2) | 16 hours | Backend Senior + AI/Agents Specialist |
| Phase 4: Frontend Widget | 2 days (parallel with Phase 3 after day 3) | 16 hours | Frontend Engineer |
| Phase 5: Testing & Validation | 2 days (parallel with Phase 4 after day 4) | 16 hours | QA Engineer |
| **Total** | **7-8 days** | **64 hours** | **2-3 engineers** |

**Critical Path**: Phase 1 → Phase 2 → Phase 3 (database → tools → endpoint)

**Parallelizable Work**:
- Phase 2 MCP Server (after Phase 1 database schema complete)
- Phase 4 Frontend Widget (after Phase 3 endpoint contract defined)
- Phase 5 Testing (starts after Phase 3, runs in parallel)

**Sequential Approach** (1 engineer): 18 days

---

## Next Steps

1. **Approval**: Review this plan and ARCHITECTURE.md
2. **Task Breakdown**: Run `/sp.tasks` to generate atomic tasks with dependencies
3. **Implementation**: Begin Phase 1 (Database Schema) immediately
4. **Architecture Review**: Consider ADRs for 5 major decisions (optional)

See `ARCHITECTURE.md` for deep-dive design, pseudocode examples, system diagrams, and detailed component specifications.

---

**Plan Status**: ✅ **COMPLETE** | **Ready for**: `/sp.tasks` (task breakdown) or implementation

