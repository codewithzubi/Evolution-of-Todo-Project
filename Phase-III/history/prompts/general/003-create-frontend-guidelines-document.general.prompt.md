---
id: 003
title: Create Frontend Guidelines Document
stage: general
date: 2026-02-10
surface: agent
model: claude-sonnet-4-5
feature: none
branch: 003-landing-page
user: user
command: direct-request
labels: ["documentation", "frontend", "guidelines"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/CLAUDE.md
tests:
  - none
---

## Prompt

Create a new file frontend/CLAUDE.md with this exact content:

# Frontend Guidelines – Phase II

## Stack
- Next.js 16.1.6 (App Router + TypeScript)
- Tailwind CSS + shadcn/ui + Lucide Icons
- TanStack Query v5
- next-themes (dark mode default)

## Rules
- Server components by default
- 'use client' only when needed (interactivity)
- All API calls → @/lib/api.ts (with JWT auto attach)
- Components follow shadcn/ui style
- Landing page = app/page.tsx
- Dashboard = app/dashboard/page.tsx
- Login = app/login/page.tsx

## Response snapshot

Created frontend/CLAUDE.md with the specified frontend development guidelines for Phase II. The file documents the tech stack (Next.js 16.1.6, Tailwind CSS, shadcn/ui, TanStack Query v5, next-themes) and establishes key development rules including server components by default, centralized API calls through @/lib/api.ts with JWT auto-attachment, and standard page locations.

## Outcome

- ✅ Impact: Established frontend development standards for Phase II project
- 🧪 Tests: No tests required for documentation
- 📁 Files: Created 1 file (frontend/CLAUDE.md)
- 🔁 Next prompts: Begin implementing landing page following these guidelines
- 🧠 Reflection: Clear, concise guidelines that align with modern Next.js best practices and the project's architecture

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A - documentation task
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): N/A
