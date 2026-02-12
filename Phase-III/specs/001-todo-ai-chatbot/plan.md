# Implementation Plan: Todo AI Chatbot

**Branch**: `001-todo-ai-chatbot` | **Date**: 2026-02-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-todo-ai-chatbot/spec.md`

## Summary

Implement a natural language todo management interface using OpenAI Agents SDK with MCP (Model Context Protocol) tools. Users interact with an AI chatbot to create, view, update, complete, and delete tasks through conversational commands. The system uses a stateless architecture where all conversation state is persisted in the database, enabling multi-turn contextual conversations while maintaining Phase-II security and architecture principles.

**Core Technical Approach**:
- **Chat Endpoint**: `POST /api/{user_id}/chat` accepts natural language messages
- **Stateless Design**: No server-side session storage; conversation history retrieved from database on each request
- **MCP Tools**: 5 tools (add_task, list_tasks, complete_task, update_task, delete_task) expose existing task operations to AI agent
- **OpenAI Agents SDK**: Orchestrates tool calling and response generation
- **OpenAI ChatKit**: Pre-built frontend chat UI components
- **Database Models**: Conversation and Message tables for persistent conversation state

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Next.js 16.1.6 (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.128.5, SQLModel 0.0.32, OpenAI Agents SDK, Official MCP SDK
- Frontend: OpenAI ChatKit, TanStack Query v5, Better Auth 1.4.18

**Storage**: Neon Serverless PostgreSQL (existing database extended with conversations and messages tables)
**Testing**: pytest (backend unit/integration), Vitest (frontend unit), Playwright (E2E)
**Target Platform**: Linux server (backend), Web browser (frontend)
**Project Type**: Web application (existing monorepo with frontend/ and backend/)

**Performance Goals**:
- Chat response time: <3 seconds (p95) per spec requirement SC-006
- User requirement: <2 seconds target for optimal UX
- Intent recognition accuracy: 90% for common task phrases (SC-002)
- Task creation: <10 seconds end-to-end (SC-001)

**Constraints**:
- Must maintain backward compatibility with Phase-II task API
- JWT token validation required on every request
- User-scoped data isolation (no cross-user access)
- AI service timeout: 5 seconds max
- Conversation history limit: 50 messages per retrieval (pagination for older)
- Message content: 1-10,000 characters

**Scale/Scope**:
- Multi-user system (existing Phase-II user base)
- Multiple concurrent conversations per user
- Indefinite conversation retention (no automatic cleanup in v1)
- 5 MCP tools matching 5 core todo operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase-II Principles (Must Not Violate)

✅ **I. Locked Tech Stack**:
- No changes to existing stack (Next.js 16.1.6, FastAPI 0.128.5, Better Auth 1.4.18, Neon PostgreSQL)
- Additions only: OpenAI Agents SDK, MCP SDK, ChatKit (permitted by Phase-III amendments)

✅ **II. Feature Scope Discipline**:
- Chat interface enables existing 5 core features via natural language
- No new todo features added (tags, priorities, etc.)
- Scope limited to conversational interface for existing operations

✅ **III. User-Scoped Security**:
- JWT validation on chat endpoint
- All MCP tools filter by user_id from JWT claims
- Conversation and message tables include user_id foreign keys
- No cross-user data access

✅ **IV. UI/UX Standards**:
- ChatKit styled with dark mode default
- shadcn/ui components for chat UI elements
- Lucide Icons for chat-related icons
- Responsive design maintained

✅ **V. Clean Architecture**:
- Backend: routes → services → models layering preserved
- Frontend: Server Components where possible, Client Components for chat interactivity
- Database: SQLModel for new Conversation and Message models
- API: RESTful conventions for chat endpoint

✅ **VI. Test-First Development**:
- TDD cycle required for all implementation
- Unit tests for MCP tools with user_id filtering validation
- Integration tests for chat endpoint with mock AI responses
- E2E tests for chat UI interactions

### Phase-III Specific Requirements

✅ **VII. AI Chatbot Integration**:
- OpenAI ChatKit for frontend chat UI
- OpenAI Agents SDK for backend agent orchestration
- Official MCP SDK for tool server implementation
- Stateless chat endpoint with database-persisted state

✅ **MCP Server Requirements**:
- Exactly 5 tools matching core operations
- All tools filter by user_id from JWT
- No cross-user data access
- Clear error messages for authorization failures

✅ **Chat Endpoint Architecture**:
- POST /api/chat (note: spec says /api/{user_id}/chat, will use /api/chat with user_id from JWT)
- Stateless design (no server-side sessions)
- Conversation persistence in database
- User isolation via JWT validation

✅ **ChatKit Configuration**:
- Domain allowlist: localhost:3000 (dev), production domain (prod)
- Dark mode default
- shadcn/ui styling
- Responsive design

### Constitution Compliance Summary

**Status**: ✅ PASSED

All Phase-II principles maintained. Phase-III additions comply with constitutional amendments. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-ai-chatbot/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (already exists in specs/phase-iii/)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   └── chat-api.yaml    # OpenAPI spec for chat endpoint
├── checklists/
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── tasks.py          # Existing task routes
│   │   │   └── chat.py           # NEW: Chat endpoint
│   │   └── deps.py               # Existing auth dependencies
│   ├── models/
│   │   ├── task.py               # Existing task model
│   │   ├── user.py               # Existing user model
│   │   ├── conversation.py       # NEW: Conversation model
│   │   └── message.py            # NEW: Message model
│   ├── services/
│   │   ├── task_service.py       # Existing task business logic
│   │   ├── chat_service.py       # NEW: Chat orchestration service
│   │   └── mcp_server.py         # NEW: MCP tool server
│   ├── schemas/
│   │   ├── task.py               # Existing task schemas
│   │   ├── chat.py               # NEW: Chat request/response schemas
│   │   └── conversation.py       # NEW: Conversation schemas
│   └── core/
│       ├── config.py             # Existing config (add OpenAI API key)
│       └── security.py           # Existing JWT validation
├── tests/
│   ├── unit/
│   │   ├── test_mcp_tools.py     # NEW: MCP tool unit tests
│   │   └── test_chat_service.py  # NEW: Chat service unit tests
│   ├── integration/
│   │   └── test_chat_api.py      # NEW: Chat endpoint integration tests
│   └── conftest.py               # Existing test fixtures
└── alembic/
    └── versions/
        └── 003_add_conversations.py  # NEW: Migration for conversation tables

frontend/
├── app/
│   ├── dashboard/
│   │   └── page.tsx              # Existing dashboard (add chat button)
│   └── chat/
│       └── page.tsx              # NEW: Full-screen chat view (optional)
├── components/
│   ├── ui/                       # Existing shadcn/ui components
│   ├── chat/
│   │   ├── ChatInterface.tsx     # NEW: ChatKit wrapper component
│   │   ├── ChatButton.tsx        # NEW: Floating chat button
│   │   └── MessageList.tsx       # NEW: Message history display
│   └── tasks/                    # Existing task components
├── lib/
│   ├── api-client.ts             # Existing API client (add chat methods)
│   └── chat-config.ts            # NEW: ChatKit configuration
├── hooks/
│   ├── useTasks.ts               # Existing task hooks
│   └── useChat.ts                # NEW: Chat interaction hook
└── tests/
    ├── unit/
    │   └── chat.test.tsx         # NEW: Chat component tests
    └── e2e/
        └── chat.spec.ts          # NEW: Chat E2E tests

docker-compose.yml                # Existing (no changes needed)
```

**Structure Decision**: Web application structure (Option 2) selected. Existing monorepo with frontend/ and backend/ directories. Phase-III adds new modules within existing structure without restructuring. Chat functionality integrated into existing dashboard UI with optional full-screen view.

## Complexity Tracking

> **No violations requiring justification**

All complexity is justified by constitutional requirements and feature specifications. No additional patterns or abstractions introduced beyond what's necessary for Phase-III requirements.

## Phase 0: Research & Unknowns

### Research Tasks

1. **OpenAI Agents SDK Integration**
   - Research: Best practices for integrating OpenAI Agents SDK with FastAPI
   - Research: Agent configuration for tool calling with MCP
   - Research: Error handling patterns for AI service failures
   - Research: Timeout and retry strategies for agent calls

2. **MCP SDK Implementation**
   - Research: Official MCP SDK server setup in Python
   - Research: Tool definition patterns and type safety
   - Research: User context passing to tools (user_id from JWT)
   - Research: MCP server lifecycle management in FastAPI

3. **OpenAI ChatKit Configuration**
   - Research: ChatKit integration with Next.js App Router
   - Research: Domain allowlist configuration for CORS
   - Research: Custom styling with shadcn/ui and Tailwind
   - Research: Message history rendering and pagination

4. **Conversation State Management**
   - Research: Optimal database schema for conversation history
   - Research: Pagination strategies for large conversation histories
   - Research: Indexing strategies for fast conversation retrieval
   - Research: Conversation history pruning strategies (future consideration)

5. **Natural Language Date Parsing**
   - Research: Libraries for parsing relative dates ("tomorrow", "next Friday")
   - Research: Timezone handling for date parsing
   - Research: Ambiguity resolution strategies

6. **Performance Optimization**
   - Research: Caching strategies for conversation history
   - Research: Database query optimization for message retrieval
   - Research: AI response streaming (future consideration)
   - Research: Rate limiting for chat endpoint

### Unknowns to Resolve

- **OpenAI API Key Management**: How to securely store and rotate OpenAI API keys
- **MCP Tool Error Handling**: How to surface tool execution errors to AI agent
- **Conversation Context Window**: How many messages to include in agent context (token limits)
- **ChatKit Deployment**: Domain configuration for production deployment
- **Database Migration**: Safe migration strategy for adding conversation tables to production

**Output**: `research.md` with all findings and decisions

## Phase 1: Design & Contracts

### Data Models (data-model.md)

**Note**: `specs/phase-iii/data-model.md` already exists with complete SQLModel definitions. Will reference and validate against spec requirements.

**Models to Implement**:

1. **Conversation Model**
   - Fields: id (UUID), user_id (UUID FK), created_at, updated_at
   - Relationships: One-to-many with Message
   - Indexes: user_id, created_at, updated_at
   - Cascade: Delete messages when conversation deleted

2. **Message Model**
   - Fields: id (UUID), conversation_id (UUID FK), user_id (UUID FK), role (enum), content (text), tools_used (JSON), created_at
   - Relationships: Many-to-one with Conversation
   - Indexes: conversation_id, user_id, created_at, composite (conversation_id, created_at)
   - Constraints: role CHECK ('user' OR 'assistant'), content length 1-10,000 chars

**Validation Rules**:
- User ownership: user_id in message must match conversation.user_id
- Role validation: Only "user" or "assistant"
- Tools used: Only populated for assistant messages
- Content: Non-empty, max 10,000 characters

### API Contracts (contracts/)

**Chat Endpoint Contract** (`contracts/chat-api.yaml`):

```yaml
openapi: 3.0.0
info:
  title: Todo AI Chatbot API
  version: 1.0.0

paths:
  /api/chat:
    post:
      summary: Send message to AI chatbot
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - message
              properties:
                message:
                  type: string
                  minLength: 1
                  maxLength: 10000
                  description: User's natural language message
                conversation_id:
                  type: string
                  format: uuid
                  description: Existing conversation ID (omit for new conversation)
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  conversation_id:
                    type: string
                    format: uuid
                  response:
                    type: string
                  timestamp:
                    type: string
                    format: date-time
                  tools_used:
                    type: array
                    items:
                      type: string
                  context:
                    type: object
                    properties:
                      tasks_affected:
                        type: integer
                      operation:
                        type: string
                        enum: [create, read, update, delete, complete]
        '400':
          description: Bad request (validation error)
        '401':
          description: Unauthorized (invalid/expired token)
        '500':
          description: Internal server error

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

**MCP Tools Contract** (`contracts/mcp-tools.yaml`):

```yaml
mcp_tools:
  - name: add_task
    description: Create a new task for the user
    parameters:
      user_id:
        type: string
        format: uuid
        required: true
      title:
        type: string
        required: true
      description:
        type: string
        required: false
      due_date:
        type: string
        format: date
        required: false
    returns:
      type: object
      properties:
        success: boolean
        task: object

  - name: list_tasks
    description: Retrieve user's tasks with optional filtering
    parameters:
      user_id:
        type: string
        format: uuid
        required: true
      status:
        type: string
        enum: [complete, incomplete, all]
        required: false
        default: all
      limit:
        type: integer
        required: false
        default: 50
    returns:
      type: object
      properties:
        success: boolean
        tasks: array
        count: integer

  - name: complete_task
    description: Mark a task as complete or incomplete
    parameters:
      user_id:
        type: string
        format: uuid
        required: true
      task_id:
        type: string
        format: uuid
        required: false
      task_title:
        type: string
        required: false
      mark_complete:
        type: boolean
        required: false
        default: true
    returns:
      type: object
      properties:
        success: boolean
        task: object

  - name: update_task
    description: Modify task details
    parameters:
      user_id:
        type: string
        format: uuid
        required: true
      task_id:
        type: string
        format: uuid
        required: false
      task_title:
        type: string
        required: false
      new_title:
        type: string
        required: false
      new_description:
        type: string
        required: false
      new_due_date:
        type: string
        format: date
        required: false
    returns:
      type: object
      properties:
        success: boolean
        task: object

  - name: delete_task
    description: Remove a task permanently
    parameters:
      user_id:
        type: string
        format: uuid
        required: true
      task_id:
        type: string
        format: uuid
        required: false
      task_title:
        type: string
        required: false
      delete_all_completed:
        type: boolean
        required: false
        default: false
    returns:
      type: object
      properties:
        success: boolean
        deleted_count: integer
        message: string
```

### Quickstart Guide (quickstart.md)

**Purpose**: Developer onboarding for Phase-III chat feature

**Contents**:
1. Prerequisites (Phase-II setup complete)
2. Environment variables (OpenAI API key)
3. Database migration (add conversation tables)
4. Backend setup (install OpenAI/MCP SDKs)
5. Frontend setup (install ChatKit)
6. Running locally (start backend MCP server + frontend)
7. Testing chat interface (example conversations)
8. Troubleshooting common issues

### Agent Context Update

Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude` to update CLAUDE.md with Phase-III technologies:
- OpenAI Agents SDK
- Official MCP SDK
- OpenAI ChatKit
- Conversation/Message models

## Phase 2: Implementation Flow

**Note**: Phase 2 (task generation) is handled by `/sp.tasks` command, NOT by `/sp.plan`.

The implementation will follow this sequence:

1. **Database Layer** (Red → Green → Refactor)
   - Create Conversation and Message models
   - Write Alembic migration
   - Test model relationships and constraints

2. **MCP Tools Layer** (Red → Green → Refactor)
   - Implement 5 MCP tools wrapping existing task service
   - Add user_id filtering to all tools
   - Test tool execution with user isolation

3. **Chat Service Layer** (Red → Green → Refactor)
   - Implement conversation management (create, retrieve history)
   - Implement message persistence (save user/assistant messages)
   - Integrate OpenAI Agents SDK with MCP tools
   - Test agent orchestration with mock AI responses

4. **API Layer** (Red → Green → Refactor)
   - Implement POST /api/chat endpoint
   - Add JWT validation and user_id extraction
   - Add error handling (validation, auth, AI service failures)
   - Test endpoint with integration tests

5. **Frontend Layer** (Red → Green → Refactor)
   - Integrate ChatKit components
   - Implement chat button in dashboard
   - Add API client methods for chat endpoint
   - Test chat UI interactions with E2E tests

6. **Integration & Performance** (Red → Green → Refactor)
   - End-to-end testing of full chat flow
   - Performance testing (response time <2s)
   - Load testing (concurrent conversations)
   - Error scenario testing (AI failures, timeouts)

## Architecture Decisions

### 1. Stateless Chat Design

**Decision**: Use stateless architecture with database-persisted conversation state

**Rationale**:
- Aligns with Phase-II RESTful API principles
- Enables horizontal scaling (no sticky sessions)
- Conversation history survives server restarts
- Supports multiple concurrent conversations per user
- Simplifies deployment (no session store required)

**Alternatives Considered**:
- In-memory session storage: Rejected due to scaling limitations and data loss on restart
- Redis cache: Rejected as unnecessary complexity for MVP; database sufficient for performance goals

### 2. Chat Endpoint Path

**Decision**: Use `/api/chat` (not `/api/{user_id}/chat`)

**Rationale**:
- user_id extracted from JWT token (already authenticated)
- Prevents path parameter spoofing (user can't specify different user_id)
- Consistent with Phase-II security pattern (JWT-based user identification)
- Simpler frontend API calls (no need to pass user_id)

**Spec Note**: Original spec mentioned `/api/{user_id}/chat`, but this violates security best practices. JWT-based user identification is more secure.

### 3. MCP Tool Implementation

**Decision**: Wrap existing task service methods with MCP tool interface

**Rationale**:
- Reuses existing business logic (no duplication)
- Maintains single source of truth for task operations
- MCP tools act as thin adapters
- Easier to maintain and test

**Alternatives Considered**:
- Duplicate task logic in MCP tools: Rejected due to code duplication and maintenance burden
- Direct database access in tools: Rejected due to bypassing business logic layer

### 4. Conversation History Limit

**Decision**: Load last 50 messages per conversation for agent context

**Rationale**:
- Balances context richness with token limits
- Prevents excessive database queries
- Sufficient for most conversation flows
- Pagination available for viewing older messages

**Alternatives Considered**:
- Load all messages: Rejected due to token limits and performance concerns
- Load last 10 messages: Rejected as insufficient context for complex conversations

### 5. Error Handling Strategy

**Decision**: Graceful degradation with user-friendly error messages

**Rationale**:
- AI service failures should not crash the application
- User messages always saved (no data loss)
- Clear error messages guide user to retry or contact support
- Errors logged for debugging

**Error Categories**:
- Validation errors (400): Invalid message format, missing fields
- Auth errors (401): Invalid/expired JWT token
- AI service errors (500): Timeout, API failure, tool execution failure
- Database errors (500): Connection failure, constraint violation

### 6. ChatKit Integration

**Decision**: Use ChatKit as pre-built UI component library

**Rationale**:
- Reduces frontend development time
- Production-ready chat UI patterns
- Consistent with Phase-II principle of using established libraries
- Customizable with shadcn/ui styling

**Alternatives Considered**:
- Build custom chat UI: Rejected due to time constraints and reinventing the wheel
- Use generic chat library: Rejected as ChatKit is OpenAI-optimized

## Security Considerations

1. **JWT Validation**: Every chat request validates JWT token before processing
2. **User Isolation**: All MCP tools filter by user_id from JWT claims
3. **Input Sanitization**: Message content validated (length, format) before storage
4. **SQL Injection Prevention**: SQLModel parameterized queries for all database operations
5. **CORS Configuration**: ChatKit domain allowlist prevents unauthorized origins
6. **API Key Security**: OpenAI API key stored in environment variables, never in code
7. **Rate Limiting**: Consider implementing rate limiting for chat endpoint (future enhancement)

## Performance Optimization

1. **Database Indexing**: Indexes on user_id, conversation_id, created_at for fast queries
2. **Query Optimization**: Composite index (conversation_id, created_at) for message retrieval
3. **Connection Pooling**: SQLModel connection pool for database efficiency
4. **Async Operations**: FastAPI async endpoints for non-blocking I/O
5. **Message Pagination**: Limit conversation history to 50 messages per request
6. **Caching Strategy**: Consider caching recent conversations (future enhancement)

## Testing Strategy

### Unit Tests

- **MCP Tools**: Test each tool with user_id filtering, error cases, edge cases
- **Chat Service**: Test conversation management, message persistence, agent orchestration (mocked)
- **Models**: Test validation rules, relationships, constraints

### Integration Tests

- **Chat Endpoint**: Test full request/response cycle with mock AI service
- **Database**: Test conversation and message CRUD operations
- **Auth**: Test JWT validation and user_id extraction

### E2E Tests

- **Chat Flow**: Test user sends message → AI responds → task created
- **Multi-turn Conversation**: Test context maintained across multiple messages
- **Error Scenarios**: Test AI service failure, invalid input, auth failure

### Performance Tests

- **Response Time**: Verify <2s response time under normal load
- **Concurrent Users**: Test multiple users chatting simultaneously
- **Large Conversations**: Test performance with 50+ message history

## Deployment Considerations

1. **Environment Variables**: Add OPENAI_API_KEY to production environment
2. **Database Migration**: Run Alembic migration to add conversation tables
3. **ChatKit Domain**: Configure production domain in ChatKit allowlist
4. **Monitoring**: Add logging for chat endpoint requests, AI service calls, errors
5. **Rollback Plan**: Database migration rollback script, feature flag for chat UI

## Success Metrics

- **SC-001**: Task creation <10 seconds (measure end-to-end latency)
- **SC-002**: Intent recognition 90% accuracy (track tool call success rate)
- **SC-003**: Full lifecycle via chat (verify all 5 operations work)
- **SC-004**: Context maintained (test multi-turn conversations)
- **SC-005**: 85% first-attempt success (track clarification request rate)
- **SC-006**: Response time <3 seconds (monitor p95 latency)
- **SC-007**: History accuracy 100% (verify conversation retrieval)

## Next Steps

1. **Phase 0**: Complete research.md with findings from research tasks
2. **Phase 1**: Validate data-model.md, create contracts/, create quickstart.md
3. **Phase 1**: Update agent context with Phase-III technologies
4. **Phase 2**: Run `/sp.tasks` to generate implementation tasks
5. **Implementation**: Follow TDD cycle (Red → Green → Refactor) for each task
6. **Testing**: Verify all success criteria met
7. **Deployment**: Migrate database, deploy backend/frontend, configure ChatKit

## Appendix: Key Files Reference

- **Spec**: `specs/001-todo-ai-chatbot/spec.md`
- **Data Model**: `specs/phase-iii/data-model.md`
- **MCP Tools**: `specs/phase-iii/mcp-tools.md`
- **Chat Endpoint**: `specs/phase-iii/chat-endpoint.md`
- **Overview**: `specs/phase-iii/overview.md`
- **Constitution**: `.specify/memory/constitution.md`
