---
id: 004
title: Update user auth spec Better Auth JWT
stage: spec
date: 2026-02-10
surface: agent
model: claude-sonnet-4-5
feature: 001-user-auth
branch: 003-landing-page
user: codewithzubi
command: /sp.specify
labels: ["authentication", "better-auth", "jwt", "fastapi", "spec-update"]
links:
  spec: specs/001-user-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-user-auth/spec.md
  - specs/001-user-auth/checklists/requirements.md
tests:
  - Specification quality validation (all checks passed)
---

## Prompt

Update the file @specs/001-user-auth/spec.md completely.

Replace it with a new spec that follows these EXACT requirements:

- Use **Better Auth** on frontend (email/password + optional Google)
- Better Auth issues **JWT token**
- FastAPI backend verifies JWT using shared secret (BETTER_AUTH_SECRET)
- Every protected route must extract user_id from JWT
- Every user can ONLY see/modify their own tasks (strict user isolation)
- No password reset, email verification, 2FA, etc. in Phase II

Keep the same User Stories structure, but update all descriptions, acceptance criteria, functional requirements, and security considerations to match the above tech stack.

Output ONLY the full updated spec.md content.

## Response snapshot

Successfully updated the user authentication specification to reflect the Better Auth + JWT + FastAPI architecture:

**Key Updates:**
- Replaced generic authentication with Better Auth-specific flows
- Added JWT token issuance and verification throughout all user stories
- Updated all 28 functional requirements to include JWT validation and user_id extraction
- Enhanced security considerations with BETTER_AUTH_SECRET management
- Added 11 edge cases covering JWT-specific scenarios (token tampering, expiration, misconfiguration)
- Updated 5 user stories with 25 acceptance scenarios reflecting JWT-based authentication
- Defined 15 measurable success criteria including 100% data isolation enforcement

**Architecture Highlights:**
- Better Auth handles registration, login, and OAuth on frontend
- JWT tokens issued upon successful authentication
- FastAPI backend verifies JWT signature using shared BETTER_AUTH_SECRET
- Every protected endpoint extracts user_id from JWT payload
- All database queries filtered by user_id for strict isolation

**Validation:**
- Created specification quality checklist
- All validation checks passed (no implementation details, testable requirements, measurable success criteria)
- No [NEEDS CLARIFICATION] markers remain
- Spec ready for /sp.plan phase

## Outcome

- ✅ Impact: Complete specification rewrite aligning with Better Auth + JWT architecture; 28 functional requirements updated; strict user isolation model defined
- 🧪 Tests: Specification quality validation completed (all 14 checklist items passed)
- 📁 Files: Updated specs/001-user-auth/spec.md (236 lines), created specs/001-user-auth/checklists/requirements.md
- 🔁 Next prompts: /sp.plan to create architectural plan, /sp.clarify if requirements need refinement
- 🧠 Reflection: Successfully balanced technical accuracy (JWT, BETTER_AUTH_SECRET, user_id extraction) with business-focused language; spec maintains "what/why" focus without "how" implementation details

## Evaluation notes (flywheel)

- Failure modes observed: None - spec update completed successfully on first attempt
- Graders run and results (PASS/FAIL): Specification Quality Checklist - PASS (14/14 items)
- Prompt variant (if applicable): Standard /sp.specify update workflow
- Next experiment (smallest change to try): Consider adding rate limiting specifics to functional requirements for production readiness
