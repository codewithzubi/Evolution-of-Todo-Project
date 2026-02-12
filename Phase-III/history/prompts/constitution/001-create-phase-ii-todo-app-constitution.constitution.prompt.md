---
id: 001
title: Create Phase II Todo App Constitution
stage: constitution
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution", "initialization", "phase-ii", "todo-app", "hackathon"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

You are an expert Product Architect for Hackathon II – Phase II.

Create a complete **CONSTITUTION.md** file for **Phase II: Full-Stack Todo Web Application** (standalone project – Phase I se koi connection nahi).

### Tech Stack (Latest Stable – Locked)
- Next.js 16.1.6 (App Router + TypeScript)
- FastAPI 0.128.5
- SQLModel 0.0.32
- Better Auth 1.4.18 (with JWT)
- Neon Serverless PostgreSQL
- shadcn/ui + Tailwind + Lucide Icons + TanStack Query v5
- UV + Python 3.13+

### Core Features
Only 5 Basic Features:
- Add Task
- View Tasks
- Update Task
- Delete Task
- Mark Complete/Incomplete

### Authentication
- Better Auth (email/password + Google optional)
- JWT token on FastAPI backend
- Every user sees only their own tasks

### UI Requirements (Exact & Locked)
1. **Public Landing Page** (/)
   - Dark modern hero with big headline
   - Large phone mockup showing the dashboard inside
   - Features section (3-4 cards)
   - Final CTA button → redirects to /login
   - Clean SaaS style (Opal/Linear inspired)

2. **Login & Signup Page** (/login)
   - Centered card, dark gradient background
   - Toggle between login/signup

3. **Dashboard** (/dashboard)
   - Left sidebar: All Tasks | Pending | Completed
   - Top navbar: Logo + Search + + Add Task + User avatar + Logout
   - Main area: Responsive task grid

4. **Task Card**
   - shadcn Card
   - Left: Checkbox
   - Title (bold) + truncated description
   - Status badge (Pending = orange, Completed = green)
   - Hover: Edit & Delete icons

### Project Structure
Use Spec-Kit monorepo:
hackathon-todo/
├── .spec-kit/config.yaml
├── specs/ (overview.md, features/, api/, database/, ui/)
├── frontend/ (Next.js app)
├── backend/ (FastAPI)
├── CLAUDE.md (root + frontend + backend)
├── docker-compose.yml
└── README.md

Dark mode default everywhere. Clean architecture. No extra features.

Output ONLY the full Markdown content of CONSTITUTION.md. No extra text.

## Response snapshot

Created comprehensive constitution for Phase II Full-Stack Todo Application with 6 core principles:

1. **Locked Tech Stack (NON-NEGOTIABLE)**: Fixed versions for Next.js 16.1.6, FastAPI 0.128.5, SQLModel 0.0.32, Better Auth 1.4.18, Neon PostgreSQL, shadcn/ui, TanStack Query v5
2. **Feature Scope Discipline (NON-NEGOTIABLE)**: Exactly 5 features (Add, View, Update, Delete, Mark Complete/Incomplete) - no feature creep allowed
3. **User-Scoped Security (NON-NEGOTIABLE)**: JWT-based authentication, user data isolation, no cross-user data leakage
4. **UI/UX Standards (NON-NEGOTIABLE)**: Exact specifications for landing page, login/signup, dashboard, and task cards with dark mode default
5. **Clean Architecture**: Monorepo structure with frontend/backend separation, layered architecture, proper separation of concerns
6. **Test-First Development (NON-NEGOTIABLE)**: TDD cycle (Red-Green-Refactor) with 80% coverage requirement

Additional sections:
- **Technology Constraints**: Locked dependency versions with exact package.json and pyproject.toml specifications
- **Development Workflow**: Spec-driven development process, Git workflow with conventional commits, quality gates
- **Governance**: Amendment process, semantic versioning, compliance enforcement

Constitution version 1.0.0 ratified and amended on 2026-02-09.

## Outcome

- ✅ Impact: Initial constitution established for Phase II Todo Application with strict scope and tech stack controls
- 🧪 Tests: No tests (documentation artifact)
- 📁 Files: Created .specify/memory/constitution.md (267 lines)
- 🔁 Next prompts: /sp.specify to create feature specifications, /sp.plan for architecture planning
- 🧠 Reflection: Constitution enforces discipline through NON-NEGOTIABLE principles to prevent scope creep and ensure hackathon delivery success

## Evaluation notes (flywheel)

- Failure modes observed: None - initial creation
- Graders run and results (PASS/FAIL): N/A - initial constitution
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate constitution compliance during first feature specification
