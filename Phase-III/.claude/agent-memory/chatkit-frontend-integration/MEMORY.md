# ChatKit Frontend Integration Memory

## Project Context
- Phase-III AI Chatbot implementation for Evolution of Todo task management app
- Frontend: Next.js 16+ with App Router, React 19, Tailwind CSS, i18n (next-intl)
- Backend: FastAPI with existing authentication system (JWT tokens stored in localStorage)
- Task: Add non-invasive floating chat widget without modifying existing pages/components
- Architecture: Floating overlay (fixed position bottom-right, z-index 1000)

## Key Findings
1. **Existing Auth System**: Uses Better Auth with JWT tokens
   - Token stored in localStorage (key: `evolution_todo_jwt_token`)
   - useAuth() hook already provides user/token context
   - ApiClient class automatically injects JWT Authorization headers
   - Token refresh mechanism available via `/api/auth/refresh`

2. **Frontend Structure**:
   - Root layout: `frontend/src/app/layout.tsx` (don't modify)
   - Locale layout: `frontend/src/app/[locale]/layout.tsx` with LanguageProvider
   - Existing providers: Providers.tsx wraps app with auth/context
   - No ChatKit library currently in package.json

3. **Chat API Endpoints** (from backend):
   - POST /api/v1/chat/conversations - create new conversation
   - GET /api/v1/chat/conversations - list user's conversations
   - GET /api/v1/chat/conversations/{id} - get conversation details
   - DELETE /api/v1/chat/conversations/{id} - delete conversation
   - POST /api/v1/chat/conversations/{id}/messages - send message
   - GET /api/v1/chat/conversations/{id}/messages - list messages
   - DELETE /api/v1/chat/conversations/{id}/messages/{id} - delete message

4. **Integration Strategy**:
   - Create ChatWidget component with 'use client' directive
   - Wrap in error boundary to prevent affecting main app
   - Lazy load using next/dynamic to avoid blocking page load
   - Use existing apiClient for JWT-authenticated requests
   - Inject widget in root layout via Providers or separate wrapper

5. **Critical Constraints**:
   - ZERO modifications to existing pages, routes, or layout.tsx
   - Must not break existing navigation or UI
   - Widget must be fully optional/disabled for unauthenticated users
   - All chat requests must include JWT token from localStorage
   - Mobile responsive (full-width on mobile, fixed on desktop)

## Task Execution Order (Dependencies)
T346 → T347 (and parallel: T348, T12 parallel with T349) → T350 → T351 → T352 → T353
Parallel tracks: T354 (i18n), T355 (auth enhancements), T356-T357 (UX), T358 (docs)

## Common Pitfalls to Avoid
1. Don't modify existing layout.tsx - create separate wrapper
2. Don't hardcode API URLs - use NEXT_PUBLIC_API_BASE_URL env var
3. Don't assume localStorage available on server - use 'use client'
4. Don't skip error boundaries - chat failures shouldn't crash main app
5. Don't forget accessibility features - ARIA labels, keyboard nav, focus indicators

## Important File Paths
- Chat widget components: `/frontend/src/components/ChatWidget/`
- Auth hooks: `/frontend/src/hooks/useAuth.tsx`, new hooks in same dir
- API service: `/frontend/src/services/api.ts` (existing), new `chatApiService.ts`
- Translations: `/frontend/src/locales/{en,es,etc}/chat.json`
- Environment: `/frontend/.env.example` (update with CHATKIT vars)
- Docs: `/docs/CHAT_WIDGET_INTEGRATION.md`, `CHAT_WIDGET_QUICK_START.md`
