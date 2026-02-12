---
id: 002
title: Update constitution Phase-III AI chatbot
stage: constitution
date: 2026-02-11
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: 003-landing-page
user: user
command: /sp.constitution
labels: ["constitution", "phase-iii", "ai-chatbot", "governance", "mcp-server"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none (documentation change)
---

## Prompt

Update the existing CONSTITUTION.md file for Phase-III (Todo AI Chatbot).

Keep all Phase-II rules (Next.js, FastAPI, Better Auth, Neon DB, etc.) and add these new Phase-III rules:

- Phase-III Objective: Build AI-powered chatbot for natural language todo management
- Use OpenAI ChatKit (frontend), OpenAI Agents SDK + Official MCP SDK (backend)
- MCP server expose tools: add_task, list_tasks, complete_task, delete_task, update_task
- Stateless chat endpoint (/api/chat) – conversation state in DB (conversations + messages tables)
- All tools must filter by user_id (from JWT)
- Strict spec-driven development (Claude Code + Spec-Kit Plus only)
- New database models: Conversation, Message
- ChatKit domain allowlist configuration required for hosted UI
- Dark mode default, shadcn/ui for chat UI

Keep the old Phase-II sections intact and add a new section at the end:
# Phase-III Additions

Output ONLY the full updated CONSTITUTION.md content.

## Response snapshot

Constitution updated from v1.0.0 to v1.1.0 with Phase-III AI Chatbot Integration principles.

**Key Additions**:
- Section VII: AI Chatbot Integration (NON-NEGOTIABLE)
- MCP server requirements: 5 tools (add_task, list_tasks, complete_task, delete_task, update_task) with mandatory user_id filtering
- Chat endpoint architecture: Stateless POST /api/chat with database-persisted conversation state
- Database models: Conversation (id, user_id, title, timestamps) and Message (id, conversation_id, role, content, tool_calls, timestamp)
- ChatKit configuration: Domain allowlist for local/production, dark mode, shadcn/ui styling
- Extended development workflow: Phase-III specs in specs/features/phase3-*, MCP tools in specs/api/mcp-tools.md
- Extended quality gates: MCP tool validation, chat endpoint performance (p95 < 5s), conversation persistence, no AI hallucinations
- Governance extensions: AI model changes = MAJOR bump, MCP tool changes = MINOR bump

**Version Bump Rationale**: MINOR (0.X.0) - New principles and expanded guidance without breaking existing Phase-II rules.

**Files Flagged for Follow-up**:
- .specify/templates/plan-template.md
- .specify/templates/spec-template.md
- .specify/templates/tasks-template.md
- .specify/templates/commands/*.md

## Outcome

- ✅ Impact: Constitution extended with Phase-III AI chatbot principles while preserving all Phase-II rules. Version bumped to 1.1.0 (MINOR).
- 🧪 Tests: N/A (documentation change, no code tests required)
- 📁 Files: Modified .specify/memory/constitution.md (v1.0.0 → v1.1.0)
- 🔁 Next prompts: Validate template consistency, create Phase-III feature specs, update API documentation with chat endpoint
- 🧠 Reflection: Successfully maintained backward compatibility by adding new section rather than modifying existing principles. MCP server security constraints (user_id filtering) properly emphasized as NON-NEGOTIABLE.

## Evaluation notes (flywheel)

- Failure modes observed: None. Template structure preserved, all placeholders replaced, version semantics followed correctly.
- Graders run and results (PASS/FAIL): PASS - Constitution structure valid, no unresolved placeholders, version incremented appropriately, Sync Impact Report included.
- Prompt variant (if applicable): Standard constitution amendment workflow
- Next experiment (smallest change to try): Validate that dependent templates (.specify/templates/*.md) align with new Phase-III principles, particularly MCP tool patterns and chat endpoint architecture.
