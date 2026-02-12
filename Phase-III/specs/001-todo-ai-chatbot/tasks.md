# Implementation Tasks: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Branch**: `001-todo-ai-chatbot`
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)
**Total Tasks**: 48

## Task Execution Strategy

**TDD Approach**: All implementation follows Red-Green-Refactor cycle per constitutional requirement.

**Parallel Execution**: Tasks marked with [P] can be executed in parallel with other [P] tasks in the same phase.

**User Story Mapping**:
- Phase 3 (MCP Tools): Enables all user stories (US1-US5)
- Phase 4 (Chat Endpoint): Core infrastructure for all user stories
- Phase 5 (Frontend): UI for all user stories
- Phase 6 (Polish): Cross-cutting improvements

**MVP Scope**: Complete Phases 1-5 for basic functionality (all 5 user stories enabled through chat interface).

---

## Phase 1: Setup & Dependencies

**Goal**: Install dependencies and configure environment for Phase-III development.

### Backend Setup

- [X] T001 Install OpenAI SDK in backend/pyproject.toml (add openai>=1.0.0)
- [ ] T002 [P] Install MCP SDK in backend/pyproject.toml (add mcp>=0.1.0)
- [ ] T003 [P] Install dateparser in backend/pyproject.toml (add dateparser>=1.2.0)
- [X] T004 Add OPENAI_API_KEY to backend/.env.example
- [X] T005 Add OPENAI_MODEL to backend/.env.example (default: gpt-4)

### Frontend Setup

- [ ] T006 Install ChatKit in frontend/package.json (add @openai/chatkit)
- [X] T007 Add NEXT_PUBLIC_CHAT_ENABLED to frontend/.env.local.example

---

## Phase 2: Foundational - Database Models & Migration

**Goal**: Create database schema for conversation persistence.

### Database Models (TDD)

- [ ] T008 Write test for Conversation model in backend/tests/unit/test_conversation_model.py
- [X] T009 Create Conversation model in backend/app/models/conversation.py (id, user_id, created_at, updated_at)
- [ ] T010 [P] Write test for Message model in backend/tests/unit/test_message_model.py
- [X] T011 [P] Create Message model in backend/app/models/message.py (id, conversation_id, user_id, role, content, tools_used, created_at)

### Database Migration

- [X] T012 Generate Alembic migration in backend/alembic/versions/004_add_conversations.py (conversations + messages tables with indexes)
- [X] T013 Test migration up/down in local database (verify tables created and rollback works)

---

## Phase 3: MCP Tools Integration

**Goal**: Expose existing task operations as MCP tools for AI agent.

**User Stories Enabled**: US1 (create), US2 (list), US3 (complete), US4 (update), US5 (delete)

### MCP Server Setup

- [ ] T014 Write test for MCP server initialization in backend/tests/unit/test_mcp_server.py
- [X] T015 Create MCP server module in backend/app/mcp/tools.py (MCP tools implementation)
- [X] T016 Add MCP tools integration to chat service in backend/app/services/chat_service.py

### MCP Tool: add_task (US1)

- [ ] T017 [P] Write test for add_task tool in backend/tests/unit/test_mcp_tools.py (test user_id filtering, parameter validation)
- [X] T018 [P] Implement add_task tool in backend/app/mcp/tools.py (wrap existing task service, validate user_id)

### MCP Tool: list_tasks (US2)

- [ ] T019 [P] Write test for list_tasks tool in backend/tests/unit/test_mcp_tools.py (test status filtering, user_id isolation)
- [X] T020 [P] Implement list_tasks tool in backend/app/mcp/tools.py (wrap existing task service, support status filter)

### MCP Tool: complete_task (US3)

- [ ] T021 [P] Write test for complete_task tool in backend/tests/unit/test_mcp_tools.py (test fuzzy matching, multiple matches error)
- [X] T022 [P] Implement complete_task tool in backend/app/mcp/tools.py (support task_id or task_title lookup)

### MCP Tool: update_task (US4)

- [ ] T023 [P] Write test for update_task tool in backend/tests/unit/test_mcp_tools.py (test partial updates, user_id validation)
- [X] T024 [P] Implement update_task tool in backend/app/mcp/tools.py (support updating title, description, due_date)

### MCP Tool: delete_task (US5)

- [ ] T025 [P] Write test for delete_task tool in backend/tests/unit/test_mcp_tools.py (test single delete, delete_all_completed)
- [X] T026 [P] Implement delete_task tool in backend/app/mcp/tools.py (support task_id, task_title, or delete_all_completed)

---

## Phase 4: Chat Service & Endpoint

**Goal**: Implement stateless chat endpoint with OpenAI Agents SDK integration.

**User Stories Enabled**: All (US1-US5) via conversational interface

### Chat Schemas

- [X] T027 Create ChatRequest schema in backend/app/schemas/chat.py (message, conversation_id)
- [X] T028 [P] Create ChatResponse schema in backend/app/schemas/chat.py (success, conversation_id, response, timestamp, tools_used, context)

### Chat Service (TDD)

- [ ] T029 Write test for conversation creation in backend/tests/unit/test_chat_service.py
- [X] T030 Implement get_or_create_conversation in backend/app/services/chat_service.py
- [ ] T031 [P] Write test for message persistence in backend/tests/unit/test_chat_service.py
- [X] T032 [P] Implement save_message in backend/app/services/chat_service.py (save user and assistant messages)
- [ ] T033 Write test for conversation history retrieval in backend/tests/unit/test_chat_service.py (test 50 message limit)
- [X] T034 Implement get_conversation_history in backend/app/services/chat_service.py (load last 50 messages)
- [ ] T035 Write test for OpenAI agent integration in backend/tests/unit/test_chat_service.py (mock OpenAI API)
- [X] T036 Implement process_message in backend/app/services/chat_service.py (orchestrate: save user msg → fetch history → call agent → save assistant msg)

### Chat Endpoint (TDD)

- [ ] T037 Write integration test for POST /api/chat in backend/tests/integration/test_chat_api.py (test full flow with mock AI)
- [X] T038 Create chat router in backend/app/api/routes/chat.py (POST /api/chat endpoint)
- [X] T039 Implement JWT validation in chat endpoint (extract user_id from token)
- [X] T040 Implement error handling in chat endpoint (400 validation, 401 auth, 500 AI service failures)
- [X] T041 Register chat router in backend/app/main.py

---

## Phase 5: Frontend ChatKit Integration

**Goal**: Add conversational UI to dashboard for natural language task management.

**User Stories Enabled**: All (US1-US5) via chat interface

### API Client

- [X] T042 Add sendChatMessage method to frontend/lib/api-client.ts (POST /api/chat with JWT)

### Chat Components

- [X] T043 Create ChatInterface component in frontend/components/chat/ChatInterface.tsx (wrap ChatKit with TanStack Query)
- [X] T044 [P] Create ChatButton component in frontend/components/chat/ChatButton.tsx (floating button with Lucide MessageSquare icon)
- [X] T045 [P] Create useChat hook in frontend/hooks/useChat.ts (manage chat state with TanStack Query)

### Dashboard Integration

- [X] T046 Add ChatButton to dashboard in frontend/app/dashboard/page.tsx
- [X] T047 Style ChatInterface with dark mode in frontend/components/chat/ChatInterface.tsx (apply shadcn/ui classes)

---

## Phase 6: Polish & Error Handling

**Goal**: Improve UX with loading states, error messages, and edge case handling.

### Error Handling

- [X] T048 Add error toast notifications in frontend/components/chat/ChatInterface.tsx (display API errors to user)

---

## Task Dependencies

### Critical Path
1. Phase 1 (Setup) → Phase 2 (Database) → Phase 3 (MCP Tools) → Phase 4 (Chat Service) → Phase 5 (Frontend) → Phase 6 (Polish)

### Parallel Opportunities

**Phase 2 (Database Models)**:
- T008-T009 (Conversation model) can run parallel with T010-T011 (Message model)

**Phase 3 (MCP Tools)**:
- All tool implementations (T017-T026) can run in parallel after T014-T016 (MCP server setup)

**Phase 4 (Chat Service)**:
- T027-T028 (schemas) can run parallel
- T031-T032 (message persistence) can run parallel with T029-T030 (conversation creation)

**Phase 5 (Frontend)**:
- T043-T045 (all chat components) can run in parallel after T042 (API client)

### User Story Completion Order

All user stories (US1-US5) are enabled simultaneously once Phase 5 is complete, as they all use the same chat interface with different MCP tools.

**Independent Testing**:
- US1: Send "Add a task to buy groceries" → verify task created
- US2: Send "What tasks do I have?" → verify task list returned
- US3: Send "Mark grocery task as done" → verify task completed
- US4: Send "Change report due date to Monday" → verify task updated
- US5: Send "Delete grocery task" → verify task deleted

---

## Acceptance Criteria

### Phase 1-2: Foundation Ready
- [ ] All dependencies installed
- [ ] Database migration applied successfully
- [ ] Conversation and Message tables exist with proper indexes

### Phase 3: MCP Tools Functional
- [ ] All 5 MCP tools registered and callable
- [ ] User_id filtering enforced in all tools
- [ ] Tool tests pass with 100% coverage

### Phase 4: Chat Endpoint Working
- [ ] POST /api/chat accepts messages and returns AI responses
- [ ] Conversation history persisted and retrieved correctly
- [ ] JWT validation enforces user isolation
- [ ] Response time <3 seconds (p95)

### Phase 5: Frontend Integrated
- [ ] Chat button visible in dashboard
- [ ] ChatKit interface styled with dark mode
- [ ] Messages sent and responses displayed
- [ ] Conversation history maintained across messages

### Phase 6: Production Ready
- [ ] Error messages displayed to users
- [ ] Loading states shown during AI processing
- [ ] All edge cases handled gracefully

---

## Testing Strategy

### Unit Tests (pytest)
- Database models: Validation, relationships, constraints
- MCP tools: User_id filtering, parameter validation, error cases
- Chat service: Conversation management, message persistence, agent orchestration

### Integration Tests (pytest + TestClient)
- Chat endpoint: Full request/response cycle with mock AI
- Database operations: CRUD for conversations and messages
- Auth: JWT validation and user_id extraction

### E2E Tests (Playwright)
- Chat flow: User sends message → AI responds → task created
- Multi-turn conversation: Context maintained across messages
- Error scenarios: Invalid input, auth failure, AI service timeout

---

## Performance Targets

- **SC-001**: Task creation <10 seconds end-to-end
- **SC-002**: Intent recognition 90% accuracy (track tool call success rate)
- **SC-006**: Response time <3 seconds (p95)
- **Database queries**: <100ms for conversation history retrieval

---

## Implementation Notes

1. **TDD Cycle**: Write test → Run test (RED) → Implement code (GREEN) → Refactor → Repeat
2. **User_id Security**: Every MCP tool and database query MUST filter by user_id from JWT
3. **Error Handling**: All errors logged for debugging, user-friendly messages returned to frontend
4. **Conversation Limit**: Load last 50 messages for agent context (pagination for older messages)
5. **AI Timeout**: 5 seconds max per constitutional constraint
6. **Stateless Design**: No server-side session storage; all state in database

---

## Rollback Plan

If issues arise during implementation:

1. **Database Migration**: Run `alembic downgrade -1` to rollback conversation tables
2. **Feature Flag**: Set `NEXT_PUBLIC_CHAT_ENABLED=false` to hide chat UI
3. **MCP Server**: Comment out MCP server initialization in FastAPI lifespan
4. **Git Revert**: Revert to last stable commit on main branch

---

## Next Steps After Task Completion

1. Run full test suite: `pytest backend/tests && npm run test --prefix frontend`
2. Verify all success criteria met (see Acceptance Criteria section)
3. Performance testing: Measure response times under load
4. Security audit: Verify user_id filtering in all code paths
5. Documentation: Update API docs with chat endpoint
6. Deployment: Apply database migration in staging, then production
