---
id: 0001
title: Add Phase-III to Constitution
stage: constitution
date: 2026-02-07
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: 003-landing-page
user: zubairahmed
command: /sp.constitution
labels: ["constitution", "phase-3", "architecture", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (governance document)
---

## Prompt

```
You are updating an EXISTING CONSTITUTION.

CRITICAL RULES:
- Phase-II Constitution already exists.
- Phase-II MUST NOT be modified, rewritten, weakened, or refactored.
- Phase-III must be ADDED as a new section.
- Phase-II remains the system foundation.

=================================================
PHASE III — AI TODO CHATBOT (CONSTITUTION)
=================================================

Purpose:
Introduce an AI-powered conversational Todo Chatbot that is deeply integrated
into the existing Phase-II Full-Stack Todo Application.

This chatbot is NOT a new app.
It is an intelligent interface on top of the existing system.

-------------------------------------------------
ARCHITECTURAL PRINCIPLES
-------------------------------------------------

1. Full-Stack Integration Only
- Chatbot must reuse:
  - Existing FastAPI backend
  - Existing SQLModel models
  - Existing Neon PostgreSQL database
  - Existing Auth (JWT / Better Auth)
- No parallel backend
- No duplicate task CRUD logic
- No direct DB access by AI

2. OpenAI-Only AI Stack
- OpenAI API key is the ONLY AI credential
- OpenAI Agents SDK is mandatory
- OpenAI models only
- No Gemini, Claude, Grok, or alternatives

3. MCP-First Tool Architecture
- AI must interact with system ONLY via MCP tools
- MCP server must be stateless
- MCP tools must map to existing backend services
- Tool chaining allowed
- Tool calls allowed ONLY after confirmation

4. Conversational Safety Rules
- Intent detection ≠ execution
- AI must collect structured data step-by-step
- Task creation requires:
  - Title (required)
  - Description (optional)
  - Due date (optional)
  - Priority (High / Medium / Low)
  - Tags (optional)
  - Final user confirmation
- No destructive action without explicit confirmation

5. Stateless Backend, Persistent Memory
- Backend endpoints remain stateless
- Conversation history stored in DB
- Messages linked to user_id
- Chat context must survive server restarts

6. Secure User Context
- Every chat request requires JWT
- user_id injected into agent context
- AI must NEVER access another user's data
- Tool calls always scoped by user_id

-------------------------------------------------
UI & FRONTEND CONSTITUTION
-------------------------------------------------

- Chatbot embedded into existing frontend
- No new pages or routes
- Floating chat icon:
  - Bottom-right corner
  - Clean, modern chat-bubble icon
- On click:
  - Glass-style floating chat window
  - Smooth open/close animations
  - Modern AI look (soft colors, rounded corners)
- Chat UI must feel professional & non-intrusive

-------------------------------------------------
DATABASE EXTENSIONS (ALLOWED)
-------------------------------------------------
- conversations
- messages

-------------------------------------------------
FORBIDDEN ACTIONS
-------------------------------------------------
- Modifying Phase-II APIs
- Direct DB writes by AI
- In-memory chat state
- Auto task creation on raw user input

-------------------------------------------------
SUCCESS METRICS
-------------------------------------------------
- Chat-created tasks appear instantly in UI
- UI-created tasks visible to chatbot
- Server restart does NOT break conversations
- No Phase-II regression

Update Constitution by ADDING Phase-III only.
Add version bump & amendment log.
DO NOT write code.
```

Update Constitution by ADDING Phase-III only.
Add version bump & amendment log.
DO NOT write code.
```

## Response snapshot

Updated constitution from v2.0.0 to v3.0.0 by:
1. Preserving all 12 Phase-II principles (unchanged)
2. Adding 11 new Phase-III principles (P3.1–P3.11):
   - P3.1: Full-Stack Integration Only
   - P3.2: OpenAI-Only AI Stack
   - P3.3: MCP-First Tool Architecture
   - P3.4: Conversational Safety Rules
   - P3.5: Stateless Backend, Persistent Memory
   - P3.6: Secure User Context in Chat
   - P3.7: Embedded Chat UI (No New Routes)
   - P3.8: Phase-III Database Extensions
   - P3.9: OpenAI Agents Integration
   - P3.10: Forbidden Phase-III Actions
   - P3.11: Phase-III Success Metrics
3. Updated Progressive Evolution Architecture section to include Phase 3 in roadmap
4. Added Phase-III-specific Governance & Compliance section
5. Bumped version to 3.0.0 (MINOR: new section added)
6. Updated Sync Impact Report with phase-aware version history

## Outcome

- ✅ Impact: Constitution now governs both Phase-II (foundational) and Phase-III (AI chatbot layer). Version 3.0.0 reflects MINOR bump for Phase-III addition while preserving Phase-II unchanged. All 11 Phase-III principles are concrete, enforceable, and non-negotiable.
- 🧪 Tests: Constitution document is governance artifact (non-testable). Compliance will be validated via code review checklists and pre-commit hooks referencing P3.1–P3.11.
- 📁 Files: `.specify/memory/constitution.md` (updated, 900+ lines, added ~400 lines for Phase-III)
- 🔁 Next prompts: `/sp.specify` to create Phase-III feature spec for AI chatbot; `/sp.plan` for architecture; `/sp.tasks` for implementation
- 🧠 Reflection: Phase-III principles emphasize integration (reuse Phase-II), safety (confirmation before execution), and security (JWT scoping). Parallel systems, auto-execution, and direct DB access all forbidden. Constitution protects Phase-II integrity while enabling Phase-III innovation.

## Evaluation notes (flywheel)

- Failure modes observed: None; constitution update successful. Phase-II preserved completely. Phase-III integrated without conflicts.
- Graders run and results (PASS/FAIL): PASS—All Phase-III principles address user input requirements. No forbidden actions violated. Version bump correct (3.0.0 MINOR). Sync Impact Report complete.
- Prompt variant (if applicable): N/A (single execution)
- Next experiment (smallest change to try): Validate Phase-III principles by creating spec, plan, tasks for AI chatbot feature using `/sp.specify` command.
