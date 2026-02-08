# Phase-III Implementation Summary

**Status**: Architecture Design Complete - Ready for ADR & Task Breakdown
**Created**: 2026-02-07
**Reference**: `specs/004-ai-chatbot/ARCHITECTURE.md`

---

## Architecture Highlights

### System Design Principle
**Stateless Backend + Database Persistence + MCP-First Tools**

```
User Message → FastAPI (JWT Validation) → Conversation History (DB)
  → OpenAI Agents SDK → MCP Tools → Phase-II APIs → Response → DB Persistence
```

### Key Design Rules

1. **No In-Memory State**: All conversation data persists to Neon immediately
2. **MCP-First**: AI never directly queries database; all operations flow through tools
3. **JWT Scoping**: Every query filtered by `user_id` extracted from JWT
4. **Confirmation Gates**: Write operations require explicit user confirmation
5. **403 Not 404**: Cross-user access returns 403 (security best practice)
6. **Zero Phase-II Changes**: Reuses existing `/api/{user_id}/tasks/*` endpoints

---

## Technology Stack (Phase-III Only)

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **AI Agent** | OpenAI Agents SDK | Multi-turn reasoning + tool execution |
| **Tools** | MCP Server (Python) | Task CRUD operations (call Phase-II APIs) |
| **Chat Endpoint** | FastAPI | `POST /api/v1/chat/conversations/{conversation_id}/messages` |
| **Database** | Neon PostgreSQL | Conversations + Messages tables |
| **Chat UI** | Next.js Client Component | Floating ChatWidget (bottom-right) |

---

## Database Schema (New Tables Only)

### Conversations Table
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,  -- Soft delete
    INDEX (user_id, created_at)
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    user_id UUID NOT NULL REFERENCES users(id),
    role VARCHAR(20) CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT,
    metadata JSONB,  -- Tool calls, tokens, etc.
    created_at TIMESTAMP,
    INDEX (conversation_id, created_at),
    INDEX (user_id, conversation_id)
);
```

**Key Feature**: Both tables indexed on `user_id` for efficient per-user queries.

---

## MCP Tools (5 Total)

### 1. add_task
**Calls**: POST `/{user_id}/tasks`
**Parameters**: title (required), description, priority, due_date, tags
**Returns**: task_id, title, success message
**Confirmation**: Required (agent asks title → description → priority → due_date → confirm)

### 2. list_tasks
**Calls**: GET `/{user_id}/tasks`
**Parameters**: user_id, status (completed/incomplete), priority, overdue, limit
**Returns**: Array of tasks
**Confirmation**: Not required (read-only)

### 3. update_task
**Calls**: PATCH `/{user_id}/tasks/{task_id}`
**Parameters**: user_id, task_id, title/description/priority/due_date (optional)
**Returns**: Updated task
**Confirmation**: Required (confirm which field and new value)

### 4. complete_task
**Calls**: PATCH `/{user_id}/tasks/{task_id}/complete`
**Parameters**: user_id, task_id
**Returns**: Updated task with completed_at timestamp
**Confirmation**: Optional (encouragement offered if task overdue)

### 5. delete_task
**Calls**: DELETE `/{user_id}/tasks/{task_id}`
**Parameters**: user_id, task_id
**Returns**: success or error
**Confirmation**: MANDATORY ("Are you sure you want to delete [task name]? Say yes.")

---

## Chat Endpoint

**Route**: `POST /api/v1/chat/conversations/{conversation_id}/messages`

**Request**:
```json
{
  "content": "Create a task to buy groceries"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "conversation_id": "uuid",
    "user_message": "Create a task to buy groceries",
    "assistant_message": "Great! I'll help you create that. What's the priority level? (low, medium, high)",
    "created_at": "2026-02-07T12:00:00Z"
  },
  "error": null
}
```

**Security**:
- JWT validation on every request
- User_id extracted from JWT (cannot be forged)
- 403 Forbidden if user doesn't own conversation
- Tool calls scoped by user_id

---

## Agent Prompt Strategy

### System Prompt
```
You are a helpful task management assistant. Your role is to:
1. Help users create, list, update, complete, and delete tasks
2. Ask clarifying questions when information is missing
3. Summarize task details before creating/updating
4. Request explicit confirmation before destructive operations
5. Be conversational and supportive
```

### Confirmation Pattern for Create
```
User: "Create a task to buy groceries"
Agent: "I'll help! What's the priority level? (low, medium, or high)"
User: "High priority"
Agent: "And when should this be done? (e.g., tomorrow, next Monday)"
User: "Due tomorrow"
Agent: "Perfect! I'll create: 'Buy groceries' (priority: high, due: tomorrow). Confirm? Say 'yes'."
User: "Yes"
Agent: (calls add_task tool) "Done! I've created your task."
```

### Confirmation Pattern for Delete
```
User: "Delete that old task"
Agent: "Are you sure? This is permanent. Delete 'Old task'? Please say 'yes' to confirm."
User: "Yes"
Agent: (calls delete_task tool) "Deleted."
```

---

## Success Criteria & Implementation

| SC-ID | Target | Implementation |
|-------|--------|----------------|
| SC-001 | Task creation <90s (5-6 turns) | Agent asks clarifying questions sequentially |
| SC-002 | 95% tasks in UI within 1s | Immediate Phase-II API call on confirmation |
| SC-003 | 100% message recovery | Database persistence; load on conversation open |
| SC-004 | Zero false-positive filters | list_tasks client-side filtering + agent intent |
| SC-005 | Updates visible in <1s | Immediate PATCH to Phase-II |
| SC-006 | 100% accidental deletion prevention | Mandatory explicit confirmation |
| SC-007 | Zero cross-user leaks | JWT scoping, 403 errors, user_id injection |
| SC-008 | Response time 2-3s (p95) | Optimized agent + efficient tool calls |
| SC-009 | Widget load <500ms impact | Lazy loading, async initialization |
| SC-010 | 90% user intuitivity | Clear UI + agent guidance |
| SC-011 | 70% test coverage | Unit + integration + security tests |
| SC-012 | Zero Phase-II regression | All Phase-II tests pass |

---

## Implementation Timeline (18 Days)

### Phase 1: Database (Days 1-2)
- Create Conversation & Message SQLModels
- Alembic migration with indexes
- **Deliverable**: New tables in Neon

### Phase 2: MCP Tools (Days 3-6)
- Implement 5 tools (add, list, update, complete, delete)
- Call Phase-II endpoints via HTTP
- Unit tests (90% coverage)
- **Deliverable**: Tools callable; all tests pass

### Phase 3: Chat Endpoint & Agent (Days 5-9)
- OpenAI Agents SDK integration
- Chat endpoint with JWT validation
- Message persistence and history retrieval
- Integration tests for all user stories
- **Deliverable**: End-to-end chat flows working

### Phase 4: Chat UI Widget (Days 7-9)
- Floating ChatWidget component
- Message history loading
- Animations and mobile responsiveness
- **Deliverable**: Widget embedded in Phase-II layout

### Phase 5: Testing & Security (Days 10-13)
- Complete test suite (70%+ coverage)
- Security audit
- Performance benchmarks
- Regression tests
- **Deliverable**: Test report, zero failures

---

## Risk Mitigation

### Risk 1: OpenAI API Cost/Rate Limits
- Mitigation: Rate limiting (10 msg/min per user), token tracking, spending alerts
- Token window: Only last 20 messages to agent

### Risk 2: Cross-User Data Leakage
- Mitigation: JWT validation, user_id scoping, 403 errors, tool injection
- Testing: User B cannot access User A's data

### Risk 3: Agent Hallucination
- Mitigation: Confirmation gates, clarification prompts, parameter validation
- Testing: Verify tool parameters match user intent

### Risk 4: Conversation History Explosion
- Mitigation: Token window (20 msgs), archival after 30 days, retention policy
- Database optimization: Partitioning, soft deletes

### Risk 5: Phase-II API Changes
- Mitigation: Abstraction layer (TaskService), versioning, regression tests
- Testing: Tool ↔ Phase-II endpoint alignment verified on every Phase-II release

---

## Architectural Decisions (ADRs Needed)

**ADR-001**: Stateless Backend with Database Persistence
- **Why**: Horizontal scaling, restart resilience, audit trail

**ADR-002**: OpenAI Agents SDK (not LangChain/Anthropic)
- **Why**: Native tool support, minimal wrapper code, built-in error handling

**ADR-003**: MCP-First Architecture (AI never queries database)
- **Why**: Zero CRUD duplication, single source of truth (Phase-II)

**ADR-004**: JWT-Scoped User Isolation (403 Forbidden, not 404)
- **Why**: Security best practice (don't leak resource existence)

**ADR-005**: Token Window of 20 Messages
- **Why**: Balances context quality with token efficiency and cost

---

## Next Steps

### 1. Review & Approve Architecture
- [ ] Review ARCHITECTURE.md with team leads
- [ ] Confirm design aligns with constraints
- [ ] Identify any missing pieces

### 2. Create ADRs (Optional but Recommended)
- [ ] Run `/sp.adr ADR-001: Stateless Backend with Database Persistence`
- [ ] Run `/sp.adr ADR-002: OpenAI Agents SDK Integration`
- [ ] Run `/sp.adr ADR-003: MCP-First Tool Architecture`
- [ ] Run `/sp.adr ADR-004: JWT-Scoped User Isolation`
- [ ] Run `/sp.adr ADR-005: Token Window Management`

### 3. Break into Implementation Tasks
- [ ] Run `/sp.tasks` to decompose Phase 1-5 into actionable tasks
- [ ] Assign owners to each task
- [ ] Estimate effort per task

### 4. Begin Phase 1 (Database)
- [ ] Create SQLModel classes
- [ ] Create Alembic migration
- [ ] Test migration on local Neon instance
- [ ] Merge to main branch

### 5. Parallel Phase 2 & 3
- [ ] Implement MCP tools (call Phase-II endpoints)
- [ ] Implement ChatbotAgent (OpenAI SDK)
- [ ] Implement chat endpoint
- [ ] Write integration tests

### 6. Phase 4 (UI) & Phase 5 (Testing)
- [ ] Create ChatWidget component
- [ ] Run full test suite
- [ ] Security audit
- [ ] Performance validation

---

## Key Files Created

| File | Purpose |
|------|---------|
| `specs/004-ai-chatbot/ARCHITECTURE.md` | Full architecture design (this document's source) |
| `specs/004-ai-chatbot/IMPLEMENTATION_SUMMARY.md` | This summary (quick reference) |
| `.claude/agent-memory/architecture-planner/MEMORY.md` | Persistent memory for architect agent |

---

## Questions Answered by This Design

**Q1**: How does the AI agent execute tasks without direct database access?
**A**: All operations flow through MCP tools that call Phase-II HTTP endpoints. User_id injected from JWT ensures scoping.

**Q2**: How do we prevent accidental task deletions?
**A**: Mandatory explicit confirmation ("Are you sure?"). Agent requires "yes" before calling delete_task tool.

**Q3**: How does the chatbot remember previous conversations?
**A**: All messages persisted to database immediately. On next conversation, load last 20 messages as context.

**Q4**: How do we ensure User A can't see User B's tasks?
**A**: JWT validation on entry. User_id extracted, injected into all queries/tools. 403 Forbidden on cross-user access.

**Q5**: How do we stay within OpenAI token limits?
**A**: Load only last 20 messages to agent (full history in DB). Token tracking with alerts.

**Q6**: What happens if Phase-II API changes?
**A**: Abstraction layer (TaskService) encapsulates HTTP calls. Only this layer needs updates, not core agent logic.

**Q7**: Why not use LangChain instead of OpenAI SDK?
**A**: OpenAI Agents SDK has native tool support and minimal wrapper code. Easier to debug, less abstraction.

**Q8**: Can the chatbot handle bulk operations (e.g., "delete all high-priority tasks")?
**A**: Yes. Agent summarizes scope and asks confirmation per-item if needed. Prevents accidental bulk deletes.

---

## Success Definition

**Phase-III is considered successful when**:

1. All 7 user stories pass acceptance tests (US1-US7)
2. All 12 success criteria met (SC-001 through SC-012)
3. 70%+ test coverage achieved
4. All Phase-II tests still pass (zero regression)
5. Security audit passed (user isolation, JWT validation)
6. Performance targets met (2-3 second response time)
7. Architecture review approved by team leads

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-07 | Initial architecture design complete |

---

**Ready to proceed with ADR creation and task breakdown.**
