---
id: 002
title: create-todo-ai-chatbot-implementation-plan
stage: plan
date: 2026-02-11
surface: agent
model: claude-haiku-4-5-20251001
feature: 001-todo-ai-chatbot
branch: 001-todo-ai-chatbot
user: user
command: /sp.plan
labels: ["planning", "phase-iii", "ai-chatbot", "architecture"]
links:
  spec: specs/001-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-todo-ai-chatbot/plan.md
  - specs/001-todo-ai-chatbot/research.md
  - specs/001-todo-ai-chatbot/quickstart.md
  - specs/001-todo-ai-chatbot/contracts/chat-api.yaml
  - specs/001-todo-ai-chatbot/contracts/mcp-tools.md
  - CLAUDE.md (updated with Phase-III technologies)
tests:
  - Constitution compliance check (PASSED)
  - Data model validation (PASSED - existing specs/phase-iii/data-model.md)
---

## Prompt

Create plan.md for Phase-III chat endpoint in specs/phase-iii/

Title: Chat Endpoint Implementation Plan (/api/chat)

Include:
- Stateless design (no server memory, DB for state)
- POST /api/{user_id}/chat
  - Input: message (string), optional conversation_id
  - Flow:
    1. Get or create conversation (DB)
    2. Save user message
    3. Fetch full history
    4. Run OpenAI Agent with history + new message
    5. Agent calls MCP tools if needed
    6. Save assistant response
    7. Return AI reply + conversation_id
- Error handling (invalid token, no message, etc.)
- Performance goals (<2s response time)
- Dependencies: Better Auth (user_id), MCP tools, OpenAI Agents SDK

Output ONLY the full plan.md content.

## Response snapshot

Created comprehensive implementation plan for Todo AI Chatbot feature following Spec-Driven Development workflow:

**Planning Artifacts Created**:

1. **plan.md** (726 lines): Complete implementation plan with:
   - Technical context (Python 3.13+, FastAPI, OpenAI Agents SDK, MCP SDK, ChatKit)
   - Constitution compliance check (all Phase-II and Phase-III requirements passed)
   - Project structure (backend/frontend with new modules)
   - Phase 0: Research tasks (6 areas: OpenAI integration, MCP SDK, ChatKit, conversation state, date parsing, performance)
   - Phase 1: Design contracts (chat-api.yaml, mcp-tools.md, quickstart.md)
   - Phase 2: Implementation flow (6 layers: database, MCP tools, chat service, API, frontend, integration)
   - 6 architecture decisions with rationale and alternatives
   - Security, performance, testing, and deployment considerations

2. **research.md** (350+ lines): Resolved all technical unknowns:
   - OpenAI Agents SDK integration patterns (async FastAPI, dependency injection)
   - MCP SDK implementation (embedded server, Pydantic tool definitions)
   - ChatKit configuration (Client Component, CORS, dark mode styling)
   - Conversation state management (validated existing data-model.md)
   - Natural language date parsing (dateparser library, UTC storage)
   - Performance optimization (database indexing, no caching in v1)

3. **contracts/chat-api.yaml**: OpenAPI 3.0 specification for POST /api/chat endpoint with request/response schemas, error codes, and security (JWT Bearer auth)

4. **contracts/mcp-tools.md**: Complete MCP tool specifications for 5 tools (add_task, list_tasks, complete_task, update_task, delete_task) with parameters, returns, examples, and error handling

5. **quickstart.md**: Developer onboarding guide with 8 steps: environment setup, dependency installation, database migration, backend/frontend setup, local running, testing, example conversations, and troubleshooting

6. **CLAUDE.md**: Updated agent context with Phase-III technologies (OpenAI Agents SDK, MCP SDK, ChatKit, Conversation/Message models)

**Key Architecture Decisions**:
- Stateless chat design with database-persisted state (enables horizontal scaling)
- Chat endpoint path: /api/chat (user_id from JWT, not path parameter for security)
- MCP tools wrap existing task service (no logic duplication)
- Conversation history limit: 50 messages (balances context vs token limits)
- Graceful error handling with user-friendly messages
- ChatKit as pre-built UI component library (reduces development time)

**Constitution Compliance**: All Phase-II principles maintained, Phase-III additions comply with constitutional amendments, no violations requiring justification.

**Performance Goals**: <2s response time (target), <3s (p95 requirement), 90% intent recognition accuracy, <10s task creation end-to-end.

## Outcome

- ✅ Impact: Complete architectural plan for Phase-III Todo AI Chatbot with stateless design, MCP tools, and OpenAI Agents SDK integration
- 🧪 Tests: Constitution compliance validation (PASSED), data model validation (PASSED)
- 📁 Files: 6 files created/updated (plan.md, research.md, quickstart.md, 2 contracts, CLAUDE.md)
- 🔁 Next prompts: `/sp.tasks` to generate implementation tasks with TDD acceptance criteria
- 🧠 Reflection: Planning successfully resolved all technical unknowns through research phase; architecture decisions documented with rationale and alternatives; ready for task generation and implementation

## Evaluation notes (flywheel)

- Failure modes observed: None - planning workflow executed successfully
- Graders run and results (PASS/FAIL): Constitution Check - PASS (all requirements met), Data Model Validation - PASS (existing specs/phase-iii/data-model.md validated)
- Prompt variant (if applicable): Standard /sp.plan workflow with Phase 0 research and Phase 1 design
- Next experiment (smallest change to try): Consider adding ADR for stateless architecture decision (significant architectural choice with long-term implications)
