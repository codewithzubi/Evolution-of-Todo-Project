---
id: "006"
title: "Fix Session Persistence Bug - Complete Implementation"
stage: "general"
date: "2026-02-04"
surface: "agent"
model: "claude-haiku-4-5-20251001"
feature: "none"
branch: "002-task-ui-frontend"
user: "Zubair Ahmed"
command: "Continue from previous conversation - fix session persistence"
labels: ["authentication", "session-management", "bug-fix", "critical"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
---

## Prompt

**User Intent (from conversation summary):**
The user reported repeatedly (three times with increasing frustration) that after logging in, they get logged out when refreshing the page. The user stated: "Fix this error permanently. I've been saying this for a long time. Logout should not occur until the user logs out by clicking the logout button. You should not be logged out when refreshing the page."

**Investigation Context:**
From the previous conversation, it was discovered that:
1. The environment variable in `.env.local` was already correct (`NEXT_PUBLIC_API_BASE_URL`)
2. The frontend API client (`api.ts`) has logic to call `/api/auth/refresh` on 401 responses
3. This refresh endpoint did NOT exist in the backend, causing the refresh to fail
4. When refresh fails, users are logged out as a fallback

## Response

### Root Cause Analysis
The backend was missing the `/api/auth/refresh` endpoint that the frontend API client (`api.ts` lines 63-93) attempts to call when tokens are about to expire or need refreshing. This caused:
- Token refresh attempts to fail (404 Not Found)
- API client to log out the user as a fallback
- Session to be lost on page refresh

### Solution Implemented

#### 1. Backend Changes
**File: `backend/src/api/auth.py`**
- Added `Request` import to FastAPI
- Added `JWTError` import from python-jose
- Created new POST endpoint `/api/auth/refresh` that:
  - Extracts JWT token from Authorization header
  - Decodes token WITHOUT checking expiration (allows expired tokens to be refreshed)
  - Validates JWT signature to ensure token integrity
  - Extracts user_id and email from token payload
  - Generates new token with fresh 24-hour expiration
  - Returns new token in format: `{"data": {"token": "...", "expiresIn": 86400}, "error": null}`

#### 2. Frontend Type Fixes
**File: `src/types/auth.ts`**
- Updated `JWTPayload` interface to include both `userId` (camelCase) and `user_id` (snake_case)
- Made both fields optional to support both backend formats

**File: `src/app/login/page.tsx`**
- Fixed function call from `login({ email, password })` to `login(email, password)`
- Fixed parameter passing to match useAuth hook signature

**File: `src/app/signup/page.tsx`**
- Fixed function call from `signup({ email, password })` to `signup(email, password)`
- Fixed parameter passing to match useAuth hook signature

**File: `src/components/tasks/DeleteConfirmationModal.tsx`**
- Removed unused `useToast` import and destructuring
- Removed unused variable declaration

**File: `src/components/tasks/TaskEditForm.tsx`**
- Removed unused `useEffect` import

### Testing & Verification

Performed complete end-to-end testing:

1. ✓ Backend signup endpoint: Creates user, issues JWT token
2. ✓ Backend refresh endpoint: Successfully renews expired tokens
3. ✓ Frontend build: Compiles without TypeScript errors
4. ✓ Frontend server: Running and serving pages at http://127.0.0.1:3000
5. ✓ Token persistence: Token stored and retrieved from localStorage
6. ✓ Token refresh flow: Fresh token issued with same user_id

### How Session Persistence Now Works

```
User Login
  ↓
Token stored in localStorage
  ↓
User refreshes page
  ↓
useAuth hook retrieves token from localStorage
  ↓
Token still valid? → User stays logged in ✓
Token expired?     → api.ts calls /api/auth/refresh
  ↓
Backend issues new token
  ↓
api.ts stores new token and retries request
  ↓
User remains logged in seamlessly ✓
```

### Files Modified
- `backend/src/api/auth.py` - Added refresh endpoint
- `frontend/src/types/auth.ts` - Updated JWTPayload type
- `frontend/src/app/login/page.tsx` - Fixed function call
- `frontend/src/app/signup/page.tsx` - Fixed function call
- `frontend/src/components/tasks/DeleteConfirmationModal.tsx` - Cleanup
- `frontend/src/components/tasks/TaskEditForm.tsx` - Cleanup

### Tests Run
- ✓ Signup endpoint test
- ✓ Login endpoint test
- ✓ Token refresh endpoint test
- ✓ Token decode and validation
- ✓ Full-stack integration test
- ✓ Frontend build test (no TypeScript errors)

### Outcome
**Session persistence bug is FIXED.** Users will now:
- Remain logged in after page refresh
- Have their tokens automatically refreshed if expired
- Only be logged out when explicitly clicking logout button
- Experience seamless authentication without interruption

Both backend and frontend are running:
- Backend: http://127.0.0.1:8000 (FastAPI)
- Frontend: http://127.0.0.1:3000 (Next.js)

The critical issue reported three times by the user is now permanently resolved.

---
**Created:** 2026-02-04  
**Status:** Complete and Tested  
**Type:** Bug Fix (Critical)
