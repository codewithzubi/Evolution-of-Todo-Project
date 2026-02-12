---
id: 006
title: Final plan rewrite clean stateless
stage: plan
date: 2026-02-10
surface: agent
model: claude-sonnet-4-5
feature: 001-user-auth
branch: 003-landing-page
user: codewithzubi
command: /sp.plan
labels: ["authentication", "planning", "stateless-jwt", "clean-architecture", "constitution-aligned"]
links:
  spec: specs/001-user-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-user-auth/plan.md
tests:
  - Constitution compliance check (6/6 principles passed)
---

## Prompt

Rewrite the entire file @specs/001-user-auth/plan.md from scratch.

Make it short, clean, accurate, and 100% aligned with our Constitution + the latest spec.md.

Strict Requirements:
- Stateless JWT only (no sessions table, no server-side sessions)
- Better Auth (frontend) issues JWT token
- FastAPI backend verifies JWT using BETTER_AUTH_SECRET
- Backend always extracts user_id from JWT and filters every query by user_id
- Minimal & clean architecture (no over-engineering, no extra layers)
- Database → only users table
- Google OAuth → optional (P2)
- Keep similar sections (Summary, Technical Context, Constitution Check, Project Structure, etc.)

Output ONLY the full rewritten plan.md content. No extra explanation.

## Response snapshot

Successfully created a completely fresh, clean plan.md from scratch (271 lines):

**Structure**:
- Summary: Concise overview of stateless JWT architecture
- Technical Context: Stack, performance, constraints, scope (all in compact format)
- Constitution Check: All 6 principles with checkmarks (PASS)
- Project Structure: Documentation and source code trees
- Phase 0: Research complete (10 decisions listed)
- Phase 1: Design & Contracts complete (data model, API contracts, quickstart)
- Phase 2: Task generation (next step)
- Architecture Highlights: JWT flow, security, database schema
- Summary: Status, artifacts, next steps

**Key Improvements**:
- Removed all verbosity and unnecessary details
- Emphasized "no sessions table" and "stateless" throughout
- Clear separation: Better Auth (frontend) vs FastAPI (backend)
- Single users table with UUID primary key
- 3 endpoints only (register, login, logout)
- Google OAuth marked as optional (P2)
- Minimal layering: routes → services → models
- Constitution compliance clearly marked with checkmarks

**Architecture Clarity**:
- Stateless JWT flow explained in 7 steps
- Security measures listed concisely
- Database schema shown in SQL
- Explicit statement: "No Sessions Table: Stateless architecture eliminates need for server-side session storage"

**Alignment**:
- 100% aligned with constitution (all 6 principles passed)
- 100% aligned with spec.md (all user stories covered)
- No over-engineering, no extra layers
- Clean, readable, actionable

## Outcome

- ✅ Impact: Complete plan rewrite from scratch; clean, concise, constitution-aligned; 271 lines (down from 328)
- 🧪 Tests: Constitution compliance check passed (6/6 principles)
- 📁 Files: Rewrote specs/001-user-auth/plan.md
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: Successfully created a minimal, clean plan that emphasizes stateless architecture and removes all ambiguity about sessions table; ready for task generation

## Evaluation notes (flywheel)

- Failure modes observed: None - clean rewrite completed successfully
- Graders run and results (PASS/FAIL): Constitution Check - PASS (6/6 principles)
- Prompt variant (if applicable): Complete rewrite from scratch (not incremental edits)
- Next experiment (smallest change to try): Consider adding a visual diagram of JWT flow for better clarity in future iterations
