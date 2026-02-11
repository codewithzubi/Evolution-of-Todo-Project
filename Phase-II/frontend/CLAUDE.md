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
