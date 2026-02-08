---
id: 1
title: Update CLAUDE.md with project requirements
stage: general
date: 2026-02-01
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: master
user: zubair-ahmed
command: Update CLAUDE.md
labels: ["project-setup", "technology-stack", "agent-assignments", "configuration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - CLAUDE.md
tests:
  - File syntax validation (YAML frontmatter, Markdown)
  - Readability check for agent assignments
  - Technology stack accuracy
---

## Prompt

Update the claude.md file based on my project requirements. In this file:

Use Auth Agent for authentication
Use Frontend Agent for frontend development (e.g., Next.js)
Use DB Agent for database design and operations
Use Backend Agent for FastAPI development
Below are my project requirements:

Basic Level Functionality
Objective: Using Claude Code and Spec-Kit Plus transform the console app into a modern multi-user web application with persistent storage.
💡Development Approach: Use the Agentic Dev Stack workflow: Write spec → Generate plan → Break into tasks → Implement via Claude Code. No manual coding allowed. We will review the process, prompts, and iterations to judge each phase and project.
Requirements
Implement all 5 Basic Level features as a web application
Create RESTful API endpoints
Build responsive frontend interface
Store data in Neon Serverless PostgreSQL database
Authentication – Implement user signup/signin using Better Auth
Technology Stack
Layer
Technology
Frontend
Next.js 16+ (App Router)
Backend
Python FastAPI
ORM
SQLModel
Database
Neon Serverless PostgreSQL
Spec-Driven
Claude Code + Spec-Kit Plus
Authentication
Better Auth

Better Auth can be configured to issue JWT (JSON Web Token) tokens when users log in. These tokens are self-contained credentials that include user information and can be verified by any service that knows the secret key.
How It Works
User logs in on Frontend → Better Auth creates a session and issues a JWT token
Frontend makes API call → Includes the JWT token in the Authorization: Bearer <token> header
Backend receives request → Extracts token from header, verifies signature using shared secret
Backend identifies user → Decodes token to get user ID, email, etc. and matches it with the user ID in the URL
Backend filters data → Returns only tasks belonging to that use

## Response snapshot

Updated CLAUDE.md with:
- Project overview section explaining transformation objective and SDD approach
- Technology stack table mapping each layer to assigned agent
- Agent responsibilities and assignments for Frontend, Backend, DB, and Auth agents
- JWT token-based authentication flow (4-step process with security considerations)
- API design patterns for RESTful endpoints, error handling
- Database design patterns for multi-user row-level security
- Updated project structure including backend/, frontend/, and .env.example

## Outcome

- ✅ Impact: Configuration file now reflects complete tech stack and agent-driven architecture; provides clear reference for all development phases
- 🧪 Tests: YAML frontmatter valid, Markdown syntax correct, no unresolved placeholders
- 📁 Files: 1 file modified (CLAUDE.md)
- 🔁 Next prompts: Run `/sp.specify` to create feature specifications for the 5 Basic Level features
- 🧠 Reflection: CLAUDE.md now serves as single source of truth for project context, agent assignments, and authentication flow; ready for specification phase

## Evaluation notes (flywheel)

- Failure modes observed: None; all edits applied successfully
- Graders run and results (PASS/FAIL): PASS - File readable, syntax valid, agent assignments clear
- Prompt variant (if applicable): Initial project configuration
- Next experiment: Begin feature specification phase with `/sp.specify` command to create spec.md for feature set
