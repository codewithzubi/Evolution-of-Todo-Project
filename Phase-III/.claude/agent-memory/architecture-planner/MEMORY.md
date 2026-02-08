# Phase-III Architecture Planner - Persistent Memory

**Last Updated**: 2026-02-07

## Key Architectural Decisions

### 1. Stateless Backend with Database Persistence (ADR-001)
- **Decision**: No in-memory conversation state; all messages persisted to Neon PostgreSQL immediately
- **Why**: Enables horizontal scaling, survives server restarts, provides audit trail, supports real-time persistence requirements
- **Implementation**:
  - Conversations table: `id, user_id, title, created_at, updated_at, deleted_at`
  - Messages table: `id, conversation_id, user_id, role, content, metadata, created_at`
  - Both tables indexed on `(user_id, created_at)` for efficient filtering

### 2. OpenAI Agents SDK (ADR-002)
- **Decision**: Use OpenAI Agents SDK (not LangChain, Anthropic, or custom loop)
- **Why**: Native tool support, minimal wrapper code, built-in multi-turn reasoning, error handling
- **Key Pattern**: Agent receives conversation history (last 20 messages) + tool definitions; handles tool loop internally
- **Token Window**: Load only last 20 messages to agent to save tokens; full history available from DB

### 3. MCP-First Tool Architecture (ADR-003)
- **Critical Design Rule**: AI NEVER has direct database access; all task operations flow through MCP tools
- **Tool Pattern**: MCP tools call Phase-II endpoints via HTTP; user_id injected from JWT (cannot be forged by user input)
- **Tools Implemented**: add_task, list_tasks, update_task, complete_task, delete_task
- **Error Handling**: Tools return JSON with success/error fields; agent converts to natural language

### 4. User Isolation via JWT (ADR-004)
- **Rule**: Every query includes `WHERE user_id = :user_id` extracted from JWT
- **Security Pattern**:
  - JWT middleware validates token before any endpoint processing
  - User ID extracted from JWT, stored in `request.state.user_id`
  - Tools receive scoped user_id; cannot be overridden by user input
  - Cross-user access returns 403 Forbidden (NOT 404, to avoid leaking resource existence)
- **Testing**: Must verify User A cannot see/access User B's conversations or tasks

### 5. Confirmation Gates for Destructive Operations (ADR-005)
- **Rule**: All write operations require explicit user confirmation via natural conversation
- **Implementation**:
  - Agent asks clarifying questions (title, description, priority, due_date)
  - Summarizes collected details
  - Requests confirmation: "yes" or "confirm"
  - Only invokes tool after confirmation
- **Exception**: list_tasks (read-only) does not require confirmation if intent is clear
- **Delete Safety**: Mandatory explicit confirmation ("Are you sure you want to delete [task name]?")

## Phase-II Integration Patterns

### API Reuse Without Duplication
- Phase-III MCP tools call Phase-II endpoints directly
- No reimplementation of CRUD logic
- Tool ↔ Phase-II Endpoint Mapping:
  - `add_task` → POST `/{user_id}/tasks` (201)
  - `list_tasks` → GET `/{user_id}/tasks?limit=10&offset=0` (200)
  - `update_task` → PATCH `/{user_id}/tasks/{id}` (200)
  - `complete_task` → PATCH `/{user_id}/tasks/{id}/complete` (200)
  - `delete_task` → DELETE `/{user_id}/tasks/{id}` (204)

### Data Model Separation
- **Phase-II Tables (UNCHANGED)**:
  - `users`: authentication, Better Auth integration
  - `tasks`: title, description, due_date, completed, priority, tags, user_id
- **Phase-III Tables (NEW)**:
  - `conversations`: user-scoped chat sessions
  - `messages`: conversation history (user/assistant/system messages)
- **NO Schema Coupling**: Phase-III doesn't modify Phase-II tables; can be deployed independently

## Success Criteria Implementation

| SC-ID | Implementation Strategy | Test Validation |
|-------|------------------------|-----------------|
| SC-001 | 5-6 turn dialogue with agent asking clarifying questions sequentially | Integration test with timing assertion (<90s) |
| SC-002 | Immediate Phase-II API call on confirmation; no DB polling | Performance test with task list refresh |
| SC-003 | Messages persisted immediately; load last 50 on conversation open | Persistence test (close browser, reopen) |
| SC-004 | list_tasks filters on client (agent understands intent); zero false positives | Verify against Phase-II API results |
| SC-005 | Immediate PATCH call to Phase-II; <1s database write | Performance test with UI verification |
| SC-006 | Confirmation flow stored in database; agent asks before delete | Test refusing/confirming deletion |
| SC-007 | User_id scoping on all queries; cross-user test returns 403 | Security test (User B accesses User A's data) |
| SC-008 | Agent response time (inference + tool call): 2-3 seconds p95 | Load test with 100 concurrent users |
| SC-009 | ChatWidget lazy loaded; doesn't block page render | Lighthouse performance audit |
| SC-010 | Clear UI + agent guidance in system prompt | Usability review |
| SC-011 | Unit tests (MCP tools): 90%+; Integration tests (endpoints): 70%+ | pytest-cov coverage report |
| SC-012 | Run all Phase-II tests; verify zero failures | Regression test suite |

## Common Pitfalls & Solutions

### Pitfall 1: Forgetting User_ID Scoping in Queries
- **Problem**: Agent could see/modify other users' tasks if WHERE clause missing
- **Solution**: Template helper functions that auto-inject user_id
```python
def scoped_query(user_id: UUID, base_query):
    return base_query.where(Model.user_id == user_id)
```

### Pitfall 2: Passing Full Conversation History to Agent
- **Problem**: Token limit exceeded; slow inference; high cost
- **Solution**: Load only last 20 messages; older messages available from DB
- **Trade-off**: Agent may not remember very old context (acceptable for MVP)

### Pitfall 3: Direct Database Access in Tools
- **Problem**: Breaks Phase-II abstraction; duplicates CRUD logic
- **Solution**: Tools ALWAYS call Phase-II HTTP APIs; no direct SQL
- **Error Handling**: Tool catches HTTP errors and returns user-friendly message

### Pitfall 4: Missing Confirmation Before Delete
- **Problem**: User accidentally deletes important task
- **Solution**: Agent asks explicit confirmation; requires "yes" or "confirm"
- **Testing**: Test refusing deletion (task should still exist)

### Pitfall 5: Leaking User Existence with 404
- **Problem**: Returns 404 for forbidden AND not-found; attacker knows resource exists
- **Solution**: Always return 403 Forbidden for cross-user access
```python
if conversation.user_id != jwt_user_id:
    raise ForbiddenException("Access denied")  # 403, same as resource doesn't exist
```

## Testing Strategy

### Unit Tests (90%+ coverage for MCP tools)
- Each tool: success path, parameter validation, Phase-II API error, user_id scoping
- Example: `test_add_task_success()`, `test_add_task_user_id_injection()`, `test_add_task_phase2_api_error()`

### Integration Tests (All user stories)
- US1: Create task via 5-6 turn conversation with confirmation
- US2: List and filter tasks with natural language
- US3: Update task with confirmation
- US4: Complete task with optional confirmation
- US5: Delete task with MANDATORY confirmation
- US6: Conversation persists across refresh/restart
- US7: Cross-user isolation (403 on access attempt)

### Security Tests
- JWT validation (missing token → 401, invalid signature → 401)
- User isolation (User B cannot access User A's conversation → 403)
- Tool user_id injection (tools receive correct user_id from JWT)
- SQL injection prevention (parameter binding)

### Performance Tests
- Chat response time <3 seconds (p95)
- Conversation history load <1 second
- Widget initial load impact <500ms

### Regression Tests
- All Phase-II tests still pass
- No API endpoint modifications
- No breaking changes to task schema

## Implementation Phases

### Phase 1: Database Schema & Migrations (2 days)
- Create SQLModel classes (Conversation, Message)
- Alembic migration with proper indexes
- Validation: tables exist, can query them

### Phase 2: MCP Server & Tool Definitions (4 days)
- 5 tool implementations with Phase-II API calls
- Parameter validation and error handling
- Unit tests (90% coverage)

### Phase 3: Chat Endpoint & Agent Integration (5 days)
- OpenAI Agents SDK initialization with conversation history
- Endpoint: POST `/api/v1/chat/conversations/{conversation_id}/messages`
- Message persistence and history retrieval
- Integration tests for all user stories

### Phase 4: Chat UI Widget (3 days)
- Floating ChatWidget (bottom-right)
- ChatWindow component with message list
- Lazy loading, animations, mobile responsiveness
- Integration with Phase-II layout

### Phase 5: Testing & Security (4 days)
- Complete test coverage (70%+)
- Security audit (isolation, JWT)
- Performance benchmarks
- Regression test report

## Key Files & Locations

| File | Purpose |
|------|---------|
| `specs/004-ai-chatbot/spec.md` | User stories and requirements |
| `specs/004-ai-chatbot/ARCHITECTURE.md` | This design document |
| `backend/src/models/conversation.py` | SQLModel for conversations |
| `backend/src/models/message.py` | SQLModel for messages |
| `backend/src/mcp_server/` | MCP tool implementations |
| `backend/src/agents/chatbot_agent.py` | OpenAI Agents SDK wrapper |
| `backend/src/api/chat.py` | Chat endpoint (POST /api/v1/chat/...) |
| `frontend/src/components/chat/ChatWidget.tsx` | Floating chat widget |
| `backend/alembic/versions/003_*` | Database migration |

## Environment Variables (Phase-III)

```env
# OpenAI API
OPENAI_API_KEY=sk-...  # Required for Agents SDK
OPENAI_MODEL=gpt-4      # Model to use (default: gpt-4)

# Chat configuration
CHAT_MESSAGE_LIMIT=10   # Max messages per minute (rate limiting)
CHAT_HISTORY_LIMIT=20   # Messages to load into agent context
CHAT_RESPONSE_TIMEOUT=10 # Seconds before timeout

# Phase-II integration
PHASE2_BASE_URL=http://localhost:8000  # Phase-II backend URL
```

## Abbreviations & Terminology

| Term | Meaning |
|------|---------|
| MCP | Model Context Protocol (tool definitions) |
| JWT | JSON Web Token (authentication) |
| LLM | Large Language Model (GPT-4) |
| TPS | Tokens Per Second (OpenAI rate limit) |
| p95 | 95th percentile (performance metric) |
| SC-XXX | Success Criterion number |
| US-X | User Story number |
| ADR-XXX | Architecture Decision Record |

---

## Lessons from Similar Projects

### From Phase-II Implementation
- SQLAlchemy Async is performant; use NullPool for Neon serverless
- JWT middleware should extract user_id early; use `request.state`
- Always validate ownership before operations (403, not 404)
- Test both success and error paths for every endpoint

### From Task Management Systems
- Users expect immediate visual feedback (task appears in list)
- Confirmation gates prevent 99% of accidental deletions
- Conversational interfaces need context (remember recent tasks)
- Long conversations kill token budgets (need windowing)

---

## Risk Registry

| Risk | Severity | Mitigation |
|------|----------|-----------|
| OpenAI API rate limits / cost | High | Rate limiting, token tracking, spending alerts |
| Cross-user data leakage | Critical | JWT validation, tool user_id injection, 403 errors |
| Agent hallucination | Medium | Confirmation gates, clarification prompts, parameter validation |
| Conversation history explosion | Medium | Token window (20 msgs), archival after 30 days, retention policy |
| Phase-II API changes break tools | High | Abstraction layer (TaskService), versioning, regression tests |

---

## Next Steps

1. **Review ARCHITECTURE.md** with team leads
2. **Create ADRs** for decisions 001-005
3. **Break into tasks** via `/sp.tasks` (Phase 1-5)
4. **Begin Phase 1** (Database schema) immediately
5. **Parallel Phase 2 & 3** once Phase 1 merged
6. **Continuous testing** from Phase 3 onward
