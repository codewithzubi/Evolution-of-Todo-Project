---
description: "Phase-III AI Todo Chatbot implementation tasks with OpenAI Agents SDK, MCP tools, and persistent conversations"
---

# Tasks: Phase-III AI Todo Chatbot

**Input**: Design documents from `/specs/004-ai-chatbot/` (spec.md, plan.md, ARCHITECTURE.md)
**Prerequisites**: plan.md ✅, spec.md ✅, ARCHITECTURE.md ✅
**Status**: Ready for implementation
**Branch**: `004-ai-chatbot`

**Organization**: Tasks are grouped by implementation phase and user story to enable parallel execution and independent testing. Each task references exact file paths and includes acceptance criteria.

**Format**: `- [ ] [TaskID] [P?] [Story] Description with exact file path`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1-US7) or foundation phase
- **File paths**: Exact backend/ and frontend/ structure from plan.md

---

## Overview: User Stories & Task Mapping

| User Story | Priority | Goal | Phase | Tasks |
|------------|----------|------|-------|-------|
| Foundation & Setup | Required | Database, dependencies, project structure | Phase 1-2 | T300-T329 |
| US1: Create Task via Conversation | P1 | MCP add_task tool + multi-step dialogue | Phase 3 | T330-T345 |
| US2: List and Filter Tasks | P1 | MCP list_tasks + natural language filtering | Phase 4 | T346-T360 |
| US3: Update Task Fields | P2 | MCP update_task + confirmation flow | Phase 5 | T361-T375 |
| US4: Mark Task Complete | P2 | MCP complete_task with optional confirmation | Phase 6 | T376-T385 |
| US5: Delete Task with Confirmation | P2 | MCP delete_task + mandatory confirmation | Phase 7 | T386-T395 |
| US6: Conversation Persistence | P1 | Database storage + resumption across browser refresh | Phase 8 | T396-T410 |
| US7: Multi-User Isolation | P1 | JWT scoping + 403 Forbidden for cross-user access | Phase 9 | T411-T425 |
| Testing & Polish | Required | Integration, security, performance, Phase-II regression | Phase 10 | T426+ |

---

## Phase 1: Database Schema & Migrations (Days 1-2)

**Purpose**: Create persistent storage for conversations and messages; establish database foundation

**Independent Test Criteria**:
- Alembic migrations run forward and backward without error
- Conversation and message tables created with correct columns and indexes
- Querying (user_id, created_at) index works efficiently
- Zero Phase-II table modifications

### Database Schema Tasks

- [ ] T300 Create `backend/src/models/conversation.py` with SQLModel Conversation schema:
  - Fields: id (UUID PK), user_id (UUID FK to users.id), title (str optional), created_at, updated_at, deleted_at (soft delete)
  - Validation: user_id required, title max 500 chars
  - Relationships: one_to_many with Message
  - Acceptance: Model loads in Python, can be imported, validates on instantiation

- [ ] T301 [P] Create `backend/src/models/message.py` with SQLModel Message schema:
  - Fields: id (UUID PK), conversation_id (UUID FK), user_id (UUID FK), role (enum: "user"/"assistant"/"system"), content (text), created_at, updated_at, metadata (JSON optional)
  - Validation: content required and non-empty (max 5000 chars), role must be valid enum
  - Relationships: many_to_one with Conversation
  - Acceptance: Model loads, validates role enum correctly, metadata JSON serializes/deserializes

- [ ] T302 [P] Create `backend/alembic/versions/001_create_conversations_table.py` migration:
  - Create conversations table with schema from T300
  - Add indexes: (user_id, created_at) for efficient user conversation listing
  - Add unique constraint on (user_id, deleted_at) for active conversation queries
  - Add foreign key: user_id → users.id with ON DELETE CASCADE
  - Acceptance: `alembic upgrade head` creates table, `alembic downgrade -1` removes it cleanly

- [ ] T303 [P] Create `backend/alembic/versions/002_create_messages_table.py` migration:
  - Create messages table with schema from T301
  - Add indexes: (conversation_id, created_at) for chronological message retrieval
  - Add indexes: (user_id, created_at) for user-scoped message queries
  - Add foreign keys: conversation_id → conversations.id, user_id → users.id (both ON DELETE CASCADE)
  - Add constraint: role must be one of 'user', 'assistant', 'system'
  - Acceptance: `alembic upgrade head` succeeds, `alembic downgrade -1` removes table cleanly

- [ ] T304 Create `backend/src/services/conversation_service.py` with Conversation CRUD:
  - `create_conversation(user_id: UUID, title: Optional[str]) -> Conversation`: Create new conversation, return object with id
  - `get_conversation(user_id: UUID, conversation_id: UUID) -> Conversation`: Fetch single conversation, verify user_id matches (raise 403 if not)
  - `list_conversations(user_id: UUID, limit: int = 50, offset: int = 0) -> Tuple[List[Conversation], int]`: Paginated list, total count
  - `update_conversation(user_id: UUID, conversation_id: UUID, title: str) -> Conversation`: Verify ownership, update, return
  - `delete_conversation(user_id: UUID, conversation_id: UUID) -> bool`: Soft delete (set deleted_at), return success
  - **Acceptance**: All methods accept correct parameters, enforce user_id filtering, queries return correct data, unit tests pass with 100% coverage

- [ ] T305 [P] Create `backend/src/services/message_service.py` with Message CRUD:
  - `create_message(conversation_id: UUID, user_id: UUID, role: str, content: str, metadata: Optional[dict]) -> Message`: Create and return message with id, timestamps
  - `get_message(user_id: UUID, message_id: UUID) -> Message`: Fetch single message, verify user_id matches
  - `list_messages_by_conversation(conversation_id: UUID, user_id: UUID, limit: int = 50, offset: int = 0) -> List[Message]`: Fetch messages ordered by created_at ASC, verify conversation ownership
  - `list_recent_messages(conversation_id: UUID, user_id: UUID, count: int = 20) -> List[Message]`: Fetch last N messages (for agent context window)
  - `delete_message(user_id: UUID, message_id: UUID) -> bool`: Soft delete, return success
  - **Acceptance**: All CRUD operations work end-to-end, user_id filtering enforced, ordered by created_at, unit tests ≥90% coverage

- [ ] T306 [P] Update `backend/.env.example` to include chat-related variables:
  - Add placeholders: `OPENAI_API_KEY=sk-...`, `OPENAI_MODEL=gpt-4-turbo-preview`, `MCP_SERVER_URL=http://localhost:8000`
  - Add database-related if not present: `DATABASE_URL=postgresql://...`
  - Acceptance: File readable, contains all required variables, example values match format

**Checkpoint**: Database schema created ✅ - Foundation phase can proceed

---

## Phase 2: Foundational Infrastructure (Days 2-3)

**Purpose**: Build MCP server, authentication middleware, and baseline services for chatbot

**Independent Test Criteria**:
- MCP server initializes, tools callable via SDK
- JWT extraction and validation on all endpoints
- Error handling returns consistent error format
- All new code ≥80% test coverage

### MCP Server & Tool Infrastructure

- [ ] T307 Create `backend/src/mcp/server.py` with MCP server initialization:
  - Initialize MCP server using Model Context Protocol SDK (e.g., `mcp.server.Server`)
  - Define tool registry and registration patterns
  - Implement tool call execution dispatcher
  - Add error handling for tool execution errors
  - Acceptance: Server initializes without errors, can register tools, can execute tools with proper error handling

- [ ] T308 Create `backend/src/mcp/schemas.py` with Pydantic tool schemas:
  - `AddTaskInput`: title (str), description (Optional[str]), priority (Optional[str]), due_date (Optional[str]), tags (Optional[List[str]])
  - `ListTasksInput`: status (Optional[str]), priority (Optional[str]), overdue (Optional[bool]), date_range (Optional[dict])
  - `UpdateTaskInput`: task_id (str), title (Optional[str]), description (Optional[str]), priority (Optional[str]), due_date (Optional[str])
  - `CompleteTaskInput`: task_id (str), confirm (bool)
  - `DeleteTaskInput`: task_id (str), confirm (bool)
  - All include user_id (required, extracted from JWT)
  - Acceptance: All schemas validate correctly, required fields enforced, optional fields nullable

- [ ] T309 [P] Create `backend/src/mcp/tools.py` with 5 MCP tools (framework only, no implementation):
  - Skeleton for `add_task(input: AddTaskInput) -> dict`: Tool definition with description, parameters
  - Skeleton for `list_tasks(input: ListTasksInput) -> dict`: Tool definition with description, parameters
  - Skeleton for `update_task(input: UpdateTaskInput) -> dict`: Tool definition with description, parameters
  - Skeleton for `complete_task(input: CompleteTaskInput) -> dict`: Tool definition with description, parameters
  - Skeleton for `delete_task(input: DeleteTaskInput) -> dict`: Tool definition with description, parameters
  - All tools registered with MCP server
  - Acceptance: All 5 tools callable, return error if executed without implementation, tool schema documented

### API & Authentication

- [ ] T310 Update `backend/src/api/middleware.py` (or create if not exists) with JWT validation:
  - Extract `Authorization: Bearer <token>` header from all requests to `/api/v1/chat/*` endpoints
  - Verify JWT signature using JWT_SECRET (same as Phase-II)
  - Extract `user_id` claim and attach to request state
  - Return 401 Unauthorized if token missing, invalid, or expired
  - Allow public endpoints (auth routes) to bypass middleware
  - Acceptance: Middleware applies to chat routes only, valid tokens pass, invalid tokens reject with 401, user_id extracted correctly

- [ ] T311 Create `backend/src/api/chat.py` (route handler skeleton):
  - Route: `POST /api/v1/chat/conversations/{conversation_id}/messages`
  - Endpoint signature: `async def create_message(conversation_id: UUID, user_id: UUID = Depends(extract_user_id), request: CreateMessageRequest) -> CreateMessageResponse`
  - Validate JWT (done by middleware)
  - Return 403 Forbidden if conversation doesn't belong to authenticated user
  - Acceptance: Route registered, accepts POST requests, middleware validates auth, skeleton returns error responses

- [ ] T312 [P] Create `backend/src/agents/factory.py` with OpenAI Agents SDK initialization:
  - Function: `create_agent() -> Agent`: Initialize OpenAI agent with GPT-4 model
  - Configure system prompt: "You are a helpful AI assistant for task management. Help users create, list, update, and complete tasks through natural conversation. Always ask for confirmation before destructive operations."
  - Bind all 5 MCP tools to agent
  - Set tool execution timeout (5-10 seconds)
  - Acceptance: Agent initializes, tools bound correctly, system prompt set, model specified as GPT-4+

- [ ] T313 [P] Create `backend/src/agents/prompts.py` with system prompts:
  - `SYSTEM_PROMPT_BASE`: Base prompt for conversational task management
  - `TOOL_CONFIRMATION_PROMPT`: Prompt snippet for confirmation gates (e.g., "Confirm deletion by saying 'yes'")
  - `CONTEXT_PROMPT`: Prompt for building agent context from conversation history
  - Acceptance: All prompts are strings, exported and importable, provide clear guidance for agent behavior

### Error Handling & Logging

- [ ] T314 Create `backend/src/api/errors.py` with chat-specific exceptions (extend from Phase-II if exists):
  - `ChatException`: Base exception with message and error_code
  - `ConversationNotFoundException`: 404, conversation_id not found
  - `ConversationAccessDeniedException`: 403, user doesn't own conversation
  - `ToolExecutionException`: 500, tool execution failed (with user-friendly message)
  - `AgentException`: 500, agent reasoning failed
  - Acceptance: All exceptions inherit from ChatException, can be caught and converted to HTTP responses, include user-friendly messages

- [ ] T315 [P] Create `backend/src/logging.py` with structured logging (if not exists):
  - Configure logging with JSON formatter for production
  - Log tool calls with input parameters (no sensitive data)
  - Log agent reasoning steps and decisions
  - Log errors with stack traces
  - Acceptance: Logging configured, logs are structured, tool calls logged with correlation IDs

**Checkpoint**: MCP server ready, authentication working, error handling in place ✅

---

## Phase 3: User Story 1 - Create Task via Conversation (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks through multi-step dialogue with the chatbot. User says "Create a task to buy groceries", AI asks clarifying questions (title, description, priority, due date), summarizes, requests confirmation ("yes"/"no"), then invokes `add_task` MCP tool.

**Independent Test**:
- User sends "Create a task to buy groceries" → AI responds with 2-3 questions
- User answers questions → AI summarizes collected data
- User says "yes" → AI invokes add_task tool, task appears in Phase-II task list
- Task visible without page refresh
- User A's chatbot cannot create tasks in User B's task list

### Implementation: add_task MCP Tool

- [ ] T316 Implement `add_task()` in `backend/src/mcp/tools.py`:
  - Parameters: user_id (UUID from JWT), title (str), description (Optional[str]), priority (Optional[str]), due_date (Optional[str]), tags (Optional[List[str]])
  - Call existing Phase-II endpoint: `POST /api/v1/users/{user_id}/tasks` with request body
  - Parse response: extract task_id, created_at, return as JSON
  - Error handling: if endpoint returns 422 (validation error), return user-friendly message to agent ("Title is required and must be 1-255 characters")
  - Acceptance: Tool callable, parameters validated, Phase-II endpoint called correctly, returns task object with id, timestamps

- [ ] T317 [P] Create unit tests in `backend/tests/unit/test_mcp_tools_add_task.py`:
  - Test add_task with title only → returns task with all fields
  - Test add_task with all fields → returns complete task
  - Test add_task without title → returns validation error message
  - Test add_task with user_id from JWT → task created with correct user_id
  - Test add_task from User A → task_id belongs to User A (verify via Phase-II endpoint)
  - Acceptance: All tests pass, ≥90% coverage for add_task function

- [ ] T318 Create system prompt for task creation in `backend/src/agents/prompts.py`:
  - Add `TASK_CREATION_GUIDE`: Defines the multi-step conversation flow
    - Step 1: Clarify task title (ask if user's initial phrase is complete, or ask for title)
    - Step 2: Ask for optional description ("Would you like to add more details?")
    - Step 3: Ask for optional priority ("How important is this? High, medium, or low?")
    - Step 4: Ask for optional due date ("When should this be completed?")
    - Step 5: Summarize ("Here's what I'll create: [title, description, priority, due_date]. Correct?")
    - Step 6: If user says "yes" or confirms → invoke `add_task` tool
    - Step 7: If user says "no" or revises → offer to modify specific fields
  - Acceptance: Prompt is clear, steps are numbered, tool invocation is conditional on confirmation

### Implementation: Chat Endpoint for Task Creation

- [ ] T319 Implement chat endpoint `POST /api/v1/chat/conversations/{conversation_id}/messages` in `backend/src/api/chat.py`:
  - Extract conversation_id and user_id from JWT
  - Fetch conversation from database, verify user_id matches (403 if not)
  - Fetch last 20 messages from database for agent context
  - Build message array: [{role: "user"/"assistant", content: "..."}]
  - Create CreateMessageRequest body with user's message
  - Store user message in database immediately
  - Call agent.process(messages=[...history...], user_message=request.content)
  - Parse agent response: check for tool_calls
  - For each tool_call: execute MCP tool, capture result
  - Store assistant response and tool results in database
  - Return response to client: { data: { assistant_message, tool_calls }, error: null }
  - Acceptance: Endpoint callable, messages stored, agent invoked, tool calls executed, response returned with 200

- [ ] T320 [P] Create integration tests in `backend/tests/integration/test_chat_create_task.py`:
  - Setup: Create conversation and add initial messages
  - Test 1: User says "Create task" → agent responds with clarifying questions (≥2)
  - Test 2: User provides title → agent asks for description
  - Test 3: User provides all details → agent summarizes and asks for confirmation
  - Test 4: User says "yes" → agent invokes add_task tool, returns success
  - Test 5: Task created in database with correct user_id, title, description, etc.
  - Test 6: Conversation history persisted (all messages in database)
  - Test 7: 403 Forbidden when User B tries to access User A's conversation
  - Acceptance: All tests pass, ≥80% coverage for endpoint, messages persisted, tool invoked correctly

### Implementation: Frontend Chat Widget (US1 Display)

- [ ] T321 Create `frontend/src/components/ChatWidget.tsx` with floating chat UI:
  - Client component (`'use client'`)
  - Floating button/icon in bottom-right corner, position: fixed, z-index: 1000
  - Click button to open/close ChatWindow
  - Styling: Tailwind CSS, smooth animations (opacity, scale)
  - Display unread message count badge
  - Acceptance: Widget renders, floats correctly, opens/closes without errors, animations smooth

- [ ] T322 [P] Create `frontend/src/components/ChatWindow.tsx` with chat message display:
  - Message list: display messages with role-based styling (user = right/blue, assistant = left/gray)
  - Message input field with send button
  - Loading state while awaiting response
  - Scroll to bottom on new message
  - Display tool calls in a visual format (e.g., "Tool: add_task called")
  - Acceptance: Messages display correctly, input sends messages, scroll works, loading state shows

- [ ] T323 [P] Create `frontend/src/hooks/useChat.ts` with chat state management:
  - State: messages (array), isLoading (bool), error (string or null), conversationId (UUID)
  - Function: `initialize(conversationId: UUID)`: Load conversation history from API
  - Function: `sendMessage(content: string)`: Send message to chat endpoint, update messages array
  - Function: `clearError()`: Clear error state
  - Side effect: Auto-scroll to latest message when messages change
  - Side effect: Fetch conversation history on mount
  - Acceptance: Hook initializes, state updates on message send, history loads on mount, auto-scroll works

- [ ] T324 [P] Create `frontend/src/services/chatApi.ts` with API client:
  - Function: `fetchConversationHistory(conversationId: UUID, token: string) -> Promise<Message[]>`: GET /api/v1/chat/conversations/{conversationId}/messages
  - Function: `sendMessage(conversationId: UUID, content: string, token: string) -> Promise<ChatResponse>`: POST /api/v1/chat/conversations/{conversationId}/messages with { content }
  - Include JWT token in Authorization header
  - Handle errors: return user-friendly messages (network error, 401, 403, 500)
  - Acceptance: API calls work, JWT passed correctly, responses parsed, errors handled

- [ ] T325 Update `frontend/src/app/[locale]/layout.tsx` to include ChatWidget:
  - Import ChatWidget component with dynamic/lazy loading (lazy: true, ssr: false)
  - Add ChatWidget to layout below main content
  - Pass authentication context (user, token) to ChatWidget via props or context
  - Acceptance: Layout renders with ChatWidget, no hydration errors, ChatWidget loads without blocking page

- [ ] T326 [P] Create `frontend/tests/unit/test_useChat.test.ts`:
  - Test: useChat initializes with empty messages
  - Test: sendMessage updates local state and calls API
  - Test: error state updated when API returns error
  - Test: conversation history loaded on mount
  - Acceptance: All tests pass, ≥80% coverage

- [ ] T327 [P] Create `frontend/tests/integration/test_chat_create_task.test.tsx`:
  - Setup: Render ChatWidget with mocked API
  - Test: User types "Create task" → message appears in UI
  - Test: API response parsed, assistant message displays
  - Test: Tool call result displays (e.g., "Task created: Buy Groceries")
  - Test: Conversation history persisted across component remount
  - Acceptance: All tests pass, ≥70% coverage

**Checkpoint**: Users can create tasks via chatbot ✅ - Task appears in Phase-II UI within 1 second

---

## Phase 4: User Story 2 - List and Filter Tasks (Priority: P1)

**Goal**: Users ask chatbot for task lists with optional natural language filters. "Show my overdue tasks", "List high-priority items", etc. AI parses intent, calls `list_tasks` MCP tool, displays results in readable format.

**Independent Test**:
- User asks "Show my tasks" → AI lists all tasks with status, priority, due date
- User asks "Overdue tasks" → AI filters and displays only incomplete past-due tasks
- User asks "High priority" → AI displays only high-priority items
- Filtering results match Phase-II API exactly (zero false positives)

### Implementation: list_tasks MCP Tool

- [ ] T328 Implement `list_tasks()` in `backend/src/mcp/tools.py`:
  - Parameters: user_id (UUID), status (Optional[str]), priority (Optional[str]), overdue (Optional[bool]), date_range (Optional[dict])
  - Call Phase-II endpoint: `GET /api/v1/users/{user_id}/tasks?status=...&priority=...&overdue=true/false&...`
  - Parse response: extract array of task objects
  - Format response: return JSON with task array and metadata (total count, filters applied)
  - Error handling: if endpoint returns error, return user-friendly message
  - Acceptance: Tool callable, filters applied correctly, results match Phase-II API exactly, ≥90% coverage

- [ ] T329 [P] Create unit tests in `backend/tests/unit/test_mcp_tools_list_tasks.py`:
  - Test: list_tasks without filters → returns all tasks for user_id
  - Test: list_tasks with status="complete" → returns only completed tasks
  - Test: list_tasks with overdue=true → returns incomplete tasks past due_date
  - Test: list_tasks with priority="high" → returns only high-priority tasks
  - Test: list_tasks results exactly match Phase-II API (compare outputs)
  - Test: User B cannot see User A's tasks (user_id scoping)
  - Acceptance: All tests pass, ≥90% coverage

- [ ] T330 Create system prompt for task listing in `backend/src/agents/prompts.py`:
  - Add `TASK_LISTING_GUIDE`: Defines conversation flow for "Show my tasks"
    - Parse user intent: detect status filters (complete, incomplete), priority filters (high, medium, low), date filters (overdue, today, this week, this month)
    - Call `list_tasks` tool with parsed filters
    - Format response: bulleted list with task title, priority emoji, due date, status
    - If user asks about "the third one", maintain task reference numbers in conversation
  - Acceptance: Prompt is clear, filter parsing defined, formatting specified

### Implementation: Chat Endpoint for Task Listing (reuse from T319)

- [ ] T331 Update chat endpoint to handle list_tasks calls (extend T319):
  - Extend agent reasoning to recognize "list" intents
  - Agent calls list_tasks MCP tool instead of add_task for listing requests
  - Store tool results and display in conversation
  - Acceptance: Agent recognizes list requests, calls correct tool, results displayed

- [ ] T332 [P] Create integration tests in `backend/tests/integration/test_chat_list_tasks.py`:
  - Setup: Create 5 tasks with different statuses, priorities, due dates
  - Test 1: User asks "Show my tasks" → agent lists all 5 tasks
  - Test 2: User asks "Overdue" → agent lists only incomplete overdue tasks
  - Test 3: User asks "High priority" → agent lists only high-priority tasks
  - Test 4: Results exactly match Phase-II API (compare JSON)
  - Test 5: User asks "What about the third one?" → agent understands positional reference
  - Test 6: User B cannot see User A's tasks (403 test)
  - Acceptance: All tests pass, ≥80% coverage, zero false positives in filtering

### Frontend: Task Display (reuse ChatWindow from T322)

- [ ] T333 Update `frontend/src/components/ChatWindow.tsx` to format task lists:
  - Detect when assistant message contains task list (tool output)
  - Render tasks as table or cards with: title, priority (colored), due_date, status
  - Add clickable task items (highlight for interaction)
  - Acceptance: Task lists display clearly, formatting matches design, clickable items work

**Checkpoint**: Users can list and filter tasks via chatbot ✅ - Filters match Phase-II API exactly

---

## Phase 5: User Story 3 - Update Task Fields (Priority: P2)

**Goal**: Users update task details via conversation. "Change the first task to high priority", "Update the description for the grocery task", etc. AI clarifies which task and field, asks for confirmation, invokes `update_task` MCP tool.

**Independent Test**:
- User says "Change first task to high priority" → AI confirms which task and change
- User says "yes" → Task updated in Phase-II immediately
- Updated task visible in UI without refresh

### Implementation: update_task MCP Tool

- [ ] T334 Implement `update_task()` in `backend/src/mcp/tools.py`:
  - Parameters: user_id (UUID), task_id (UUID), title (Optional[str]), description (Optional[str]), priority (Optional[str]), due_date (Optional[str]), tags (Optional[List[str]])
  - Call Phase-II endpoint: `PUT /api/v1/users/{user_id}/tasks/{task_id}` with updated fields
  - Verify task_id belongs to user_id (403 if not)
  - Return updated task object
  - Error handling: return user-friendly messages for validation/404 errors
  - Acceptance: Tool callable, user_id verified, Phase-II endpoint called, returns updated task

- [ ] T335 [P] Create unit tests in `backend/tests/unit/test_mcp_tools_update_task.py`:
  - Test: update_task with title → title updated, other fields unchanged
  - Test: update_task with priority → priority updated
  - Test: update_task with multiple fields → all fields updated
  - Test: update_task for task not owned by user → returns error/403
  - Test: update_task with invalid task_id → returns 404 message
  - Acceptance: All tests pass, ≥90% coverage

- [ ] T336 Create system prompt for task updates in `backend/src/agents/prompts.py`:
  - Add `TASK_UPDATE_GUIDE`: Defines conversation flow for updates
    - Detect "update" or "change" intent
    - Ask user to clarify which task (if context ambiguous)
    - Ask what field to change (title, description, priority, due date)
    - Ask for new value
    - Summarize change: "I'll change [task name]'s [field] from [old] to [new]. OK?"
    - If user confirms → invoke update_task
  - Acceptance: Prompt is clear, confirmation required, summary format defined

### Implementation: Chat Endpoint for Task Updates (extend T319)

- [ ] T337 Update chat endpoint to handle update_task calls (extend T319):
  - Agent recognizes update intents
  - Agent calls update_task MCP tool with parsed parameters
  - Agent summarizes change before executing (confirmation gate)
  - Acceptance: Agent recognizes update requests, calls tool, confirmation required

- [ ] T338 [P] Create integration tests in `backend/tests/integration/test_chat_update_task.py`:
  - Setup: Create task with known values
  - Test 1: User says "Change first task to high priority" → agent confirms, then updates
  - Test 2: Task updated in database with correct values
  - Test 3: Task appears updated in Phase-II API response
  - Test 4: User B cannot update User A's task (403)
  - Test 5: User cancels update ("No") → task remains unchanged
  - Acceptance: All tests pass, ≥80% coverage

### Frontend: Update Confirmation Display (extend ChatWindow)

- [ ] T339 Update `frontend/src/components/ChatWindow.tsx` to display update confirmations:
  - Detect confirmation prompts in assistant messages
  - Highlight confirmation required state
  - Display old value vs. new value
  - Acceptance: Confirmations display clearly, formatting emphasizes change

**Checkpoint**: Users can update tasks via chatbot ✅

---

## Phase 6: User Story 4 - Mark Task Complete (Priority: P2)

**Goal**: Users mark tasks complete via conversation. "Mark the grocery task complete", "Done with task #1", etc. AI identifies task, optionally confirms if overdue, invokes `complete_task` MCP tool.

**Independent Test**:
- User says "Mark task complete" → AI identifies task, completes it
- Completed task appears as done in Phase-II UI without refresh
- Completed task removed from "incomplete" filter views

### Implementation: complete_task MCP Tool

- [ ] T340 Implement `complete_task()` in `backend/src/mcp/tools.py`:
  - Parameters: user_id (UUID), task_id (UUID), confirm (bool)
  - Verify task_id belongs to user_id (403 if not)
  - Call Phase-II endpoint: `PATCH /api/v1/users/{user_id}/tasks/{task_id}/complete` with completed=true
  - Check if task is overdue; if yes, include optional encouragement message in response
  - Return updated task object with completed_at timestamp
  - Error handling: return user-friendly messages
  - Acceptance: Tool callable, user_id verified, task marked complete, timestamp set

- [ ] T341 [P] Create unit tests in `backend/tests/unit/test_mcp_tools_complete_task.py`:
  - Test: complete_task marks task completed
  - Test: completed_at timestamp set correctly
  - Test: complete_task for task not owned by user → error/403
  - Test: complete_task for already completed task → idempotent (no error)
  - Acceptance: All tests pass, ≥90% coverage

- [ ] T342 Create system prompt for task completion in `backend/src/agents/prompts.py`:
  - Add `TASK_COMPLETION_GUIDE`: Defines conversation flow
    - Detect "complete", "done", "mark done" intent
    - Clarify which task if needed
    - Check if task is overdue; if yes, offer encouragement
    - Invoke complete_task
    - Confirm: "Great! I've marked [task] as complete."
  - Acceptance: Prompt is clear, overdue check defined, encouragement optional

### Implementation: Chat Endpoint for Completion (extend T319)

- [ ] T343 Update chat endpoint to handle complete_task calls (extend T319):
  - Agent recognizes completion intents
  - Agent calls complete_task MCP tool
  - Optional confirmation for overdue tasks (agent can ask "Congrats on finishing that overdue task!")
  - Acceptance: Agent recognizes completion, calls tool

- [ ] T344 [P] Create integration tests in `backend/tests/integration/test_chat_complete_task.py`:
  - Setup: Create task
  - Test 1: User says "Mark complete" → task marked completed
  - Test 2: completed_at timestamp set in database
  - Test 3: Task removed from "incomplete" filter in Phase-II
  - Test 4: Overdue task completion triggers agent encouragement
  - Test 5: User B cannot complete User A's task (403)
  - Acceptance: All tests pass, ≥80% coverage

**Checkpoint**: Users can mark tasks complete via chatbot ✅

---

## Phase 7: User Story 5 - Delete Task with Confirmation (Priority: P2)

**Goal**: Users delete tasks via conversation with mandatory confirmation. "Delete the old task", "Remove that one". AI shows task name and asks "Are you sure?" before invoking `delete_task` MCP tool. Only deletes if user explicitly confirms with "yes".

**Independent Test**:
- User says "Delete task" → AI shows task name, asks "Are you sure?"
- User says "No" → task remains unchanged
- User says "Yes" → task deleted from Phase-II immediately

### Implementation: delete_task MCP Tool

- [ ] T345 Implement `delete_task()` in `backend/src/mcp/tools.py`:
  - Parameters: user_id (UUID), task_id (UUID), confirm (bool)
  - Verify confirm=true (tool should NOT be called unless user explicitly confirmed)
  - Verify task_id belongs to user_id (403 if not)
  - Call Phase-II endpoint: `DELETE /api/v1/users/{user_id}/tasks/{task_id}`
  - Return success message with deleted task ID
  - Error handling: return user-friendly messages
  - Acceptance: Tool requires confirmation flag, user_id verified, Phase-II endpoint called, task deleted

- [ ] T346 [P] Create unit tests in `backend/tests/unit/test_mcp_tools_delete_task.py`:
  - Test: delete_task with confirm=true → deletes task
  - Test: delete_task with confirm=false → does not delete, returns error
  - Test: delete_task for task not owned by user → error/403
  - Test: delete_task for non-existent task → error/404
  - Acceptance: All tests pass, ≥90% coverage, confirm flag enforced

- [ ] T347 Create system prompt for task deletion in `backend/src/agents/prompts.py`:
  - Add `TASK_DELETION_GUIDE`: Defines conversation flow
    - Detect "delete", "remove", "discard" intent
    - Clarify which task if needed
    - Mandatory confirmation: "Are you sure you want to delete: [task name]?"
    - Wait for explicit "yes" or similar affirmation before invoking tool
    - Only call delete_task with confirm=true if user confirms
    - If user says "no" or declines → cancel operation, offer next steps
  - Acceptance: Prompt emphasizes confirmation requirement, tool call conditional on explicit "yes"

### Implementation: Chat Endpoint for Deletion (extend T319)

- [ ] T348 Update chat endpoint to handle delete_task calls (extend T319):
  - Agent recognizes deletion intents
  - Agent requires and verifies user confirmation (FR-007)
  - Agent only calls delete_task(confirm=true) after explicit confirmation
  - Acceptance: Agent enforces confirmation gate before tool invocation

- [ ] T349 [P] Create integration tests in `backend/tests/integration/test_chat_delete_task.py`:
  - Setup: Create task
  - Test 1: User says "Delete task" → agent shows task name, asks confirmation
  - Test 2: User says "No" → task remains in database
  - Test 3: User says "Yes" → agent calls delete_task, task removed from Phase-II
  - Test 4: Deleted task removed from list_tasks results
  - Test 5: User B cannot delete User A's task (403)
  - Test 6: Mandatory confirmation prevents accidental deletion (SC-006)
  - Acceptance: All tests pass, ≥80% coverage, confirmation mandatory

**Checkpoint**: Users can delete tasks with confirmation ✅ - Accidental deletions prevented

---

## Phase 8: User Story 6 - Conversation Persistence and Resumption (Priority: P1)

**Goal**: Users start conversations, close browser, return later. Chatbot loads previous conversation history from database and allows seamless resumption. All messages displayed in chronological order with full context.

**Independent Test**:
- User creates conversation with 10+ messages
- User refreshes browser or closes/reopens
- Previous messages load from database in correct order
- User can continue conversation with full context

### Implementation: Conversation Management Endpoints

- [ ] T350 Implement `POST /api/v1/chat/conversations` endpoint in `backend/src/api/chat.py`:
  - Create new conversation for authenticated user
  - Request body: { title: Optional[str] }
  - Response: { data: { conversation_id: UUID, created_at: timestamp }, error: null }
  - Store conversation in database with user_id from JWT
  - Acceptance: Endpoint callable, conversation created with correct user_id, returned with id

- [ ] T351 [P] Implement `GET /api/v1/chat/conversations` endpoint in `backend/src/api/chat.py`:
  - List all conversations for authenticated user
  - Query params: limit, offset for pagination
  - Response: { data: { conversations: [...], total: int }, error: null }
  - Order by created_at DESC (newest first)
  - Verify all returned conversations belong to authenticated user
  - Acceptance: Endpoint callable, paginated results returned, user isolation enforced

- [ ] T352 [P] Implement `GET /api/v1/chat/conversations/{conversation_id}/messages` endpoint in `backend/src/api/chat.py`:
  - Fetch message history for conversation
  - Verify conversation belongs to authenticated user (403 if not)
  - Query params: limit, offset for pagination
  - Response: { data: { messages: [{id, role, content, created_at}, ...], total: int }, error: null }
  - Order by created_at ASC (oldest first)
  - Acceptance: Endpoint callable, messages returned in chronological order, user isolation enforced

### Implementation: Frontend Conversation Management

- [ ] T353 Update `frontend/src/hooks/useChat.ts` to support conversation selection:
  - Add state: conversationId (UUID or null)
  - Add function: `listConversations()`: Fetch list from GET /api/v1/chat/conversations
  - Add function: `selectConversation(conversationId: UUID)`: Load messages for conversation, set as active
  - Add function: `createConversation(title: Optional[str])`: POST /api/v1/chat/conversations, select new conversation
  - Acceptance: Hook functions work, state updates correctly, conversation switching works

- [ ] T354 [P] Update `frontend/src/services/chatApi.ts` to support conversation endpoints:
  - Add function: `listConversations(token: string) -> Promise<Conversation[]>`
  - Add function: `createConversation(token: string, title: Optional[str]) -> Promise<UUID>` (returns conversation_id)
  - Add function: `fetchConversationMessages(conversationId: UUID, token: string) -> Promise<Message[]>`
  - Acceptance: API functions callable, JWT passed, responses parsed

- [ ] T355 Update `frontend/src/components/ChatWidget.tsx` to support conversation persistence:
  - Add conversation list sidebar (collapsible)
  - Display list of conversations with titles and last message preview
  - Allow user to click conversation to load it
  - Show "New Conversation" button
  - Acceptance: Sidebar displays conversations, clicking loads messages, new conversation creates entry

- [ ] T356 Update `frontend/src/components/ChatWindow.tsx` to preserve scroll position:
  - On conversation switch, save scroll position
  - On conversation load, restore scroll to last message
  - Add "Load earlier messages" button at top (pagination)
  - Acceptance: Scroll position preserved, pagination works

- [ ] T357 [P] Create integration tests in `backend/tests/integration/test_conversation_persistence.py`:
  - Setup: Create conversation with 10 messages
  - Test 1: Close and reopen browser → messages loaded from database
  - Test 2: Messages displayed in correct chronological order
  - Test 3: User can send new message in resumed conversation
  - Test 4: Server restart → conversation history still available
  - Test 5: Conversation summary (title, last_message) accurate
  - Acceptance: All tests pass, ≥80% coverage

- [ ] T358 [P] Create integration tests in `frontend/tests/integration/test_conversation_persistence.test.tsx`:
  - Test: Load ChatWidget, create conversation
  - Test: Switch away, switch back → messages preserved
  - Test: Refresh page → conversation loads automatically
  - Test: Load earlier messages via pagination
  - Acceptance: All tests pass, ≥70% coverage

**Checkpoint**: Conversation persistence working ✅ - Users can resume conversations seamlessly

---

## Phase 9: User Story 7 - Multi-User Isolation (Priority: P1)

**Goal**: User A and User B both use chatbot. Neither can see other's conversation history or tasks. All MCP tool calls scoped by user_id extracted from JWT. Return 403 Forbidden (not 404) on cross-user access to avoid leaking existence.

**Independent Test**:
- User A creates tasks and conversations
- User B logs in, cannot see User A's tasks or conversations
- User B attempts direct API access to User A's conversation → 403 Forbidden
- Zero cross-user data leakage in MCP tool results

### Implementation: User Isolation Verification

- [ ] T359 Create comprehensive security tests in `backend/tests/integration/test_user_isolation.py`:
  - Setup: Create 2 users (A and B) with JWT tokens
  - Test 1: User A lists conversations → sees only User A's conversations
  - Test 2: User B lists conversations → sees only User B's conversations, not A's
  - Test 3: User B attempts to GET /api/v1/chat/conversations/{user-a-conversation-id} → 403 Forbidden (not 404)
  - Test 4: User A creates task via chatbot → task appears in User A's task list only
  - Test 5: User B lists tasks → sees only User B's tasks, not A's
  - Test 6: User B attempts to update User A's task via chatbot → 403 error returned to agent
  - Test 7: User B attempts to delete User A's task via chatbot → 403 error returned to agent
  - Test 8: Tool results for list_tasks filtered by user_id → zero User A tasks in User B's results
  - Test 9: Messages table filtered by user_id and conversation_id → no cross-user data visible
  - Acceptance: All tests pass, ≥90% coverage, zero cross-user data leaks

- [ ] T360 Create unit tests in `backend/tests/unit/test_mcp_tools_user_isolation.py`:
  - Test: Each MCP tool (add_task, list_tasks, update_task, complete_task, delete_task) validates user_id
  - Test: Tool calls from User B with User A's task_id → error/403
  - Test: Tool calls with mismatched user_id and JWT claim → error/403
  - Acceptance: All tests pass, ≥90% coverage, all tools enforce user_id scoping

### Implementation: 403 Forbidden Responses

- [ ] T361 Update conversation service in `backend/src/services/conversation_service.py`:
  - All methods verify user_id ownership
  - If conversation doesn't belong to user_id, raise `ConversationAccessDeniedException` (403)
  - Do NOT raise NotFoundException (404) to avoid leaking existence
  - Acceptance: Service enforces 403 for cross-user access

- [ ] T362 [P] Update message service in `backend/src/services/message_service.py`:
  - All methods verify user_id ownership (via conversation_id FK)
  - Return 403 if message doesn't belong to user_id
  - Acceptance: Service enforces 403 for cross-user access

- [ ] T363 [P] Update chat endpoint in `backend/src/api/chat.py`:
  - All conversation GET/POST calls verify user_id from JWT matches
  - All message GET/POST calls verify conversation belongs to user_id
  - Return 403 Forbidden (not 404) on access violations
  - Log cross-user access attempts for audit trail
  - Acceptance: Endpoint returns 403 on cross-user access, logs attempts

- [ ] T364 [P] Update MCP tools in `backend/src/mcp/tools.py`:
  - All tools accept user_id parameter (extracted from JWT by caller)
  - All tools pass user_id to Phase-II endpoints
  - All tools validate task_id ownership before operation
  - Return error message if ownership validation fails
  - Acceptance: All tools enforce user_id filtering, Phase-II endpoints called with correct user_id

### Implementation: Database Isolation Constraints

- [ ] T365 Verify database schema enforces user_id isolation (no SQL-level bypass):
  - conversations table has NOT NULL user_id FK to users.id
  - messages table has NOT NULL user_id FK to users.id
  - Queries on conversations and messages always filter by user_id
  - No unfiltered SELECT * queries on conversations or messages
  - Acceptance: Schema verified, all queries in code include user_id filter

**Checkpoint**: Multi-user isolation enforced ✅ - Zero cross-user data leakage possible

---

## Phase 10: Testing, Security Validation & Polish (Days 6-8)

**Purpose**: Comprehensive testing, security validation, Phase-II regression tests, performance testing, documentation, deployment readiness

**Independent Test Criteria**:
- ≥70% code coverage for backend and frontend
- All 12 success criteria (SC-001 to SC-012) verified
- Zero Phase-II regression (all Phase-II tests pass)
- Zero cross-user data leaks
- Response time < 3 seconds for chatbot responses
- Page load impact < 500ms

### Comprehensive Integration Testing

- [ ] T366 Create comprehensive integration test suite in `backend/tests/integration/test_all_user_stories.py`:
  - Test US1 end-to-end: Create task via chatbot, verify in Phase-II UI
  - Test US2 end-to-end: List and filter tasks, verify results match Phase-II
  - Test US3 end-to-end: Update task, verify change in Phase-II
  - Test US4 end-to-end: Mark task complete, verify in Phase-II
  - Test US5 end-to-end: Delete task with confirmation, verify removal from Phase-II
  - Test US6 end-to-end: Conversation persistence across refresh
  - Test US7 end-to-end: Multi-user isolation across all operations
  - Test: All 7 user stories work independently and sequentially
  - Acceptance: All tests pass, ≥80% coverage, each user story tested in isolation and integration

- [ ] T367 [P] Create performance tests in `backend/tests/performance/test_chatbot_latency.py`:
  - Test: Single message round-trip time < 3 seconds (p95)
  - Test: Tool execution time < 2 seconds (add_task, list_tasks, update_task, complete_task, delete_task)
  - Test: Database queries < 100ms (conversation fetch, message insert, list messages)
  - Test: Agent reasoning time < 2 seconds (including tool selection)
  - Measure and report p50, p95, p99 latencies
  - Acceptance: All latency targets met, report generated

- [ ] T368 [P] Create load testing in `backend/tests/performance/test_chatbot_concurrent.py`:
  - Test: 10 concurrent users sending messages → no errors, all responses within SLA
  - Test: 50 concurrent users → system stable, no connection pool exhaustion
  - Test: 100 concurrent users → horizontal scaling tested (if applicable)
  - Report: throughput (msgs/sec), error rate, resource usage
  - Acceptance: 100+ concurrent users supported, <1% error rate

- [ ] T369 [P] Create Phase-II regression tests in `backend/tests/integration/test_phase2_regression.py`:
  - Run all Phase-II task CRUD tests (create, list, read, update, complete, delete)
  - Verify no Phase-II API changes or breaking changes
  - Verify Phase-II authentication still works (JWT validation)
  - Verify Phase-II authorization still works (user_id filtering)
  - Verify Phase-II data models unchanged (tasks, users tables)
  - Acceptance: All Phase-II tests pass, zero breaking changes

### Frontend Integration & E2E Tests

- [ ] T370 Create frontend integration tests in `frontend/tests/integration/test_chatbot_e2e.test.tsx`:
  - Test: Widget loads on page
  - Test: User can type and send message
  - Test: Messages persist across component remount
  - Test: Conversation list loads
  - Test: Can switch between conversations
  - Test: Task creation dialog works end-to-end
  - Test: Error states display correctly
  - Acceptance: All tests pass, ≥70% coverage

- [ ] T371 [P] Create accessibility tests in `frontend/tests/integration/test_accessibility.test.tsx`:
  - Test: ChatWidget keyboard navigable (Tab, Enter, Escape)
  - Test: Focus management correct (focus trap when open)
  - Test: ARIA labels present on interactive elements
  - Test: Screen reader announces messages
  - Run axe accessibility audit
  - Acceptance: Zero critical accessibility issues, WCAG 2.1 AA compliant

### Security Testing & Validation

- [ ] T372 Create detailed security test report in `backend/tests/security/test_security_validations.py`:
  - Test: JWT validation on every /api/v1/chat/* endpoint
  - Test: 401 Unauthorized for missing JWT token
  - Test: 401 Unauthorized for invalid JWT signature
  - Test: 401 Unauthorized for expired JWT token
  - Test: User_id claim extracted and used correctly
  - Test: HTTPS enforcement (if in production environment)
  - Test: No hardcoded secrets in source code (environment variables only)
  - Test: SQL injection prevention (parameterized queries only)
  - Test: No cross-site scripting (XSS) vulnerabilities in frontend (sanitized content)
  - Acceptance: All security tests pass, zero vulnerabilities found

- [ ] T373 [P] Create security audit checklist in `specs/004-ai-chatbot/SECURITY_AUDIT.md`:
  - Document JWT validation implementation
  - Document user isolation enforcement (user_id scoping)
  - Document 403 Forbidden for cross-user access
  - Document error handling (no sensitive info leaked in error messages)
  - Document secret management (environment variables, no hardcoding)
  - Document rate limiting (if applicable)
  - Document logging and monitoring (audit trails for cross-user access attempts)
  - Acceptance: Checklist completed, all items verified, no vulnerabilities identified

### Code Quality & Coverage

- [ ] T374 Generate code coverage reports:
  - Backend coverage: `pytest --cov=backend/src --cov-report=html`
  - Frontend coverage: `vitest --coverage --reporter=html`
  - Target: ≥70% overall, ≥80% for critical paths (authentication, tool execution, user isolation)
  - Identify uncovered lines and justify (e.g., error fallback, rare edge cases)
  - Acceptance: Coverage reports generated, targets met, justifications documented

- [ ] T375 [P] Run code quality checks:
  - Backend: `ruff check backend/src` (linting), `mypy backend/src` (type checking)
  - Frontend: `eslint src` (linting), `tsc --noEmit` (type checking)
  - Zero warnings, all issues fixed
  - Acceptance: Linting and type checking pass, no warnings

### Documentation & Deployment

- [ ] T376 Create deployment guide in `specs/004-ai-chatbot/DEPLOYMENT.md`:
  - Prerequisites: Python 3.13+, Node 18+, Neon PostgreSQL, OpenAI API key
  - Backend setup: Install dependencies, run migrations, configure environment
  - Frontend setup: Install dependencies, build, deploy
  - Environment variables checklist: OPENAI_API_KEY, DATABASE_URL, JWT_SECRET, etc.
  - Docker setup (if applicable): Dockerfile, docker-compose.yml
  - Testing checklist: Run unit tests, integration tests, load tests before deployment
  - Rollback plan: How to revert if issues occur
  - Acceptance: Guide complete, clear, tested with actual deployment

- [ ] T377 [P] Update CLAUDE.md with Phase-III API documentation:
  - Document new endpoints: POST /api/v1/chat/conversations, GET /api/v1/chat/conversations, GET /api/v1/chat/conversations/{id}/messages, POST /api/v1/chat/conversations/{id}/messages
  - Document MCP tools: add_task, list_tasks, update_task, complete_task, delete_task (schemas, parameters, responses)
  - Document authentication: JWT header required on all /api/v1/chat/* endpoints
  - Document user isolation: user_id extracted from JWT, all queries filtered by user_id, 403 Forbidden on cross-user access
  - Document error responses: standard error format, status codes, user-friendly messages
  - Acceptance: Documentation complete, examples provided, API contract clear

- [ ] T378 [P] Create operation runbooks in `specs/004-ai-chatbot/RUNBOOKS.md`:
  - Runbook 1: Troubleshooting chatbot response timeouts (>3 seconds)
  - Runbook 2: Investigating cross-user data leak incidents
  - Runbook 3: Recovering from database connection pool exhaustion
  - Runbook 4: Monitoring OpenAI API rate limits and costs
  - Runbook 5: Analyzing agent reasoning failures (hallucinations, incorrect tool calls)
  - Acceptance: Runbooks complete, clear troubleshooting steps, actionable recommendations

### Final Verification & Checkpoint

- [ ] T379 Create comprehensive verification checklist in `specs/004-ai-chatbot/VERIFICATION.md`:
  - Verify all 7 user stories implemented and tested
  - Verify all 22 functional requirements met
  - Verify all 12 success criteria (SC-001 to SC-012) achieved
  - Verify zero Phase-II regression
  - Verify ≥70% code coverage
  - Verify zero security vulnerabilities
  - Verify performance targets met (< 3 sec latency, < 500ms page load impact)
  - Verify Phase-II data integrity (tasks, users untouched)
  - Acceptance: Checklist completed, all items verified, sign-off ready

- [ ] T380 [P] Create implementation summary in `specs/004-ai-chatbot/IMPLEMENTATION_COMPLETE.md`:
  - Summary: Feature overview, what was built, how to use
  - Architecture: System design, components, data flow
  - Testing results: Coverage reports, test counts, performance metrics
  - Known issues: Any limitations, workarounds, future improvements
  - Next steps: Recommendations for Phase-IV features (voice, analytics, etc.)
  - Acceptance: Summary complete, accurate, useful for future teams

**Checkpoint**: Phase-III complete, ready for production ✅

---

## Dependency Graph & Sequential Requirements

### Critical Path (Must Complete in Order)
```
Phase 1 (T300-T306): Database Schema
  ↓
Phase 2 (T307-T315): MCP Server & Foundation
  ↓
Phase 3 (T316-T327): US1 - Create Task (MVP) 🎯
  ↓
Phase 4 (T328-T333): US2 - List Tasks
  ↓
Phase 5 (T334-T339): US3 - Update Task
  ↓
Phase 6 (T340-T344): US4 - Complete Task
  ↓
Phase 7 (T345-T349): US5 - Delete Task
  ↓
Phase 8 (T350-T358): US6 - Persistence
  ↓
Phase 9 (T359-T365): US7 - Isolation
  ↓
Phase 10 (T366-T380): Testing & Polish
```

### Parallelizable Tasks (Can Run Concurrently)
**After Phase 1 Complete:**
- T307-T309 (MCP Server skeleton) + T310-T313 (API skeleton)
- These can start in parallel after database schema ready

**After Phase 2 Complete:**
- T316-T323 (US1 Implementation) runs in parallel on backend and frontend
- Backend: T316-T320 (tool, tests, endpoint)
- Frontend: T321-T327 (widget, tests)

**After Phase 3 Complete:**
- T328-T333 (US2) can run in parallel with T334-T339 (US3) on separate branches
- Frontend updates (T333, T339) can run in parallel with backend (T328-T335)

**Phase 10 Can Run Partially in Parallel:**
- Performance tests (T367-T368) can run with security tests (T372-T373)
- Documentation (T376-T378) can run with coverage reports (T374-T375)

---

## Parallel Execution Example (2-3 Engineers)

### Timeline (7-8 Days with Parallel Work)

**Day 1-2: Phases 1-2 (Sequential)**
- Engineer A: T300-T306 (Database schema & migrations)
- Engineer B (starts Day 2): T307-T309 (MCP server skeleton)

**Day 2-3: Phase 2 Completion (Parallel)**
- Engineer A: T310-T315 (API endpoints, error handling)
- Engineer B: T307-T309 complete (MCP foundation)
- Engineer C (starts Day 3): T321-T327 (Frontend widget)

**Day 3-5: Phase 3 (US1) + Phase 4 (US2) Parallel**
- Engineer A: T316-T320 (add_task tool, tests)
- Engineer B: T328-T332 (list_tasks tool, tests)
- Engineer C: T321-T327 (ChatWidget, useChat hook, tests)

**Day 4-5: Phase 5-6 (US3-US4) Parallel**
- Engineer A: T334-T338 (update_task & complete_task tools)
- Engineer B: T340-T344 (complete_task tool & tests)
- Engineer C: T339 (ChatWindow updates for confirmations)

**Day 5-6: Phase 7-8 (US5, Persistence) Parallel**
- Engineer A: T345-T349 (delete_task tool, confirmation tests)
- Engineer B: T350-T358 (Conversation management endpoints, tests)
- Engineer C: T353-T356 (Conversation UI, persistence, tests)

**Day 6-7: Phase 9 (Isolation) + Phase 10 Start**
- Engineer A: T359-T365 (Security tests, user isolation validation)
- Engineer B: T366-T368 (Integration & performance tests)
- Engineer C: T370-T371 (Frontend E2E & accessibility tests)

**Day 7-8: Phase 10 (Testing & Polish)**
- All Engineers: T372-T380 (Security audit, coverage, documentation, verification)

**Total: 7-8 Days** (vs. 14-16 days if sequential)

---

## MVP Scope (Recommended First Delivery)

**MVP = Phases 1-3 + Phase 8 (Persistence)**

### MVP Features
- Database schema for conversations and messages (T300-T306)
- MCP server with add_task tool (T307-T320)
- Chat endpoint POST /api/v1/chat/conversations/{id}/messages (T319)
- Frontend ChatWidget with floating UI (T321-T327)
- Conversation persistence (T350-T358)
- Basic multi-user isolation (T359-T365)

### MVP Success Criteria (Subset)
- SC-001: Task creation < 90 seconds ✅
- SC-002: 95% of tasks appear in UI within 1 second ✅
- SC-003: Conversation history persists across refresh ✅
- SC-012: Zero Phase-II regression ✅

### MVP Task Count
- T300-T327: Core implementation (28 tasks)
- T350-T358: Persistence (9 tasks)
- T359-T365: Basic isolation (7 tasks)
- **Total MVP: 44 tasks** (est. 4-5 days with 2 engineers)

### Post-MVP Features (Phase-IV)
- T328-T349: List, Update, Complete, Delete tasks (22 tasks)
- T366-T380: Comprehensive testing, documentation (15+ tasks)

---

## Total Task Count Summary

| Phase | Task Range | Count | Focus |
|-------|-----------|-------|-------|
| Phase 1: Database Schema | T300-T306 | 7 | Migrations, models, services |
| Phase 2: Foundation | T307-T315 | 9 | MCP server, API skeleton, auth |
| Phase 3: US1 Create | T316-T327 | 12 | Tool impl, chat endpoint, widget |
| Phase 4: US2 List | T328-T333 | 6 | Tool impl, integration tests |
| Phase 5: US3 Update | T334-T339 | 6 | Tool impl, integration tests |
| Phase 6: US4 Complete | T340-T344 | 5 | Tool impl, integration tests |
| Phase 7: US5 Delete | T345-T349 | 5 | Tool impl, integration tests |
| Phase 8: US6 Persistence | T350-T358 | 9 | Conversation mgmt, UI updates |
| Phase 9: US7 Isolation | T359-T365 | 7 | Security tests, verification |
| Phase 10: Testing & Polish | T366-T380 | 15 | Integration, security, docs |
| **TOTAL** | **T300-T380** | **81** | Full feature + comprehensive testing |

---

## Acceptance Criteria by Phase

### Phase 1 Checkpoint
- [ ] Conversations and messages tables exist in Neon
- [ ] Alembic migrations run forward/backward cleanly
- [ ] SQLModel models load and validate
- [ ] Services accept correct parameters and enforce user_id filtering
- [ ] Zero Phase-II table modifications

### Phase 2 Checkpoint
- [ ] MCP server initializes without errors
- [ ] All 5 tools registered and callable
- [ ] JWT validation enforces 401 on invalid tokens
- [ ] Error handling returns consistent format
- [ ] ≥80% test coverage for foundations

### Phase 3 Checkpoint (MVP Release)
- [ ] User can create task via 5-6 turn chatbot conversation
- [ ] Task appears in Phase-II UI within 1 second without refresh
- [ ] ChatWidget loads, opens/closes smoothly
- [ ] Confirmation gates prevent accidental tool calls
- [ ] ≥80% code coverage

### Phase 4 Checkpoint
- [ ] Users can list all tasks and filter by status/priority/overdue
- [ ] Filtering results exactly match Phase-II API
- [ ] Users can reference tasks by position ("third one")
- [ ] ≥80% code coverage

### Phase 5 Checkpoint
- [ ] Users can update task fields via conversation
- [ ] Updates visible in Phase-II UI within 1 second
- [ ] Confirmation required before execution
- [ ] ≥80% code coverage

### Phase 6 Checkpoint
- [ ] Users can mark tasks complete via chatbot
- [ ] Completed task removed from "incomplete" filter views
- [ ] Optional encouragement for overdue tasks
- [ ] ≥80% code coverage

### Phase 7 Checkpoint
- [ ] Deletion requires explicit "yes" confirmation
- [ ] Refusal to confirm ("No") prevents deletion
- [ ] Deleted task removed from Phase-II immediately
- [ ] ≥80% code coverage

### Phase 8 Checkpoint
- [ ] Conversation history persists across browser refresh
- [ ] Messages load in chronological order
- [ ] Users can resume conversation with full context
- [ ] Server restart doesn't lose message history
- [ ] ≥80% code coverage

### Phase 9 Checkpoint
- [ ] User A cannot see User B's conversations (zero results)
- [ ] User A cannot access User B's conversation via direct API (403)
- [ ] Tool results filtered by user_id (zero cross-user tasks)
- [ ] ≥90% coverage for isolation tests

### Phase 10 Checkpoint (Complete Release)
- [ ] ≥70% overall code coverage (backend + frontend)
- [ ] All 12 success criteria achieved (SC-001 to SC-012)
- [ ] Zero Phase-II regression (all Phase-II tests pass)
- [ ] Zero security vulnerabilities
- [ ] Performance targets met (< 3 sec latency, < 500ms page load)
- [ ] Deployment guide complete
- [ ] Sign-off ready

---

## Notes for Implementation Teams

### For Backend Engineer
- Start with Phase 1 (database) - this is your critical path
- Phase 2 MCP server foundation must be complete before tool implementation
- Each tool implementation is independent (add_task, list_tasks, etc. can be parallel)
- Focus on user_id filtering in ALL queries - this is non-negotiable for security
- Test each tool with unit tests before integration
- Run Phase-II regression tests continuously to catch breaking changes early

### For Frontend Engineer
- Wait for T319 (chat endpoint contract) before starting widget implementation
- ChatWidget is a Client Component - use 'use client' and manage state with useChat hook
- useChat hook is critical - test it thoroughly (message order, pagination, error handling)
- Lazy load ChatWidget to avoid page load impact
- Test conversation switching and persistence carefully
- Keyboard navigation and accessibility are required (T371)

### For QA/Testing Engineer
- Start security testing (T359-T365) early - don't wait for full implementation
- Use multi-user setup for all tests (User A vs User B accounts)
- Performance tests (T367-T368) should run on realistic hardware
- Phase-II regression tests (T369) must pass on every commit
- Coverage reports (T374) should be generated daily
- Document all test results in VERIFICATION.md for sign-off

### General Notes
- Use feature branches for each phase (feature/phase-1, feature/phase-3-us1, etc.)
- Merge to `004-ai-chatbot` branch when phase complete
- No direct commits to main until Phase 10 complete and approved
- Use PR reviews for all changes - at least 1 approval before merge
- Document any deviations from plan in ADR (if architectural) or commit message (if tactical)

---

**Status**: ✅ **COMPLETE** - Ready for implementation | **Total Tasks**: 81 | **Estimated Duration**: 7-8 days (parallel) or 14-16 days (sequential)

