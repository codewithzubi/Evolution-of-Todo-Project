# Tasks: User Authentication System

**Input**: Design documents from `/specs/001-user-auth/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/auth.openapi.yaml

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

**TDD Note**: Write tests first (Red), implement (Green), refactor. Constitution requires test-first development.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3, US4, US5)
- **[Optional]**: Optional task, can be skipped or added later
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Project initialization and basic structure

- [ ] T001 [P] Create backend directory structure (app/, models/, services/, api/, middleware/, tests/)
- [ ] T002 [P] Create frontend directory structure (app/, components/, lib/, hooks/, tests/)
- [ ] T003 [P] Initialize backend with pyproject.toml and install dependencies (FastAPI 0.128.5, SQLModel 0.0.32, python-jose[cryptography], passlib[bcrypt])
- [ ] T004 [P] Initialize frontend with package.json and install dependencies (Next.js 16.1.6, Better Auth 1.4+, TanStack Query v5, shadcn/ui)
- [ ] T005 [P] Create backend/.env.example (DATABASE_URL, BETTER_AUTH_SECRET, FRONTEND_URL) and frontend/.env.local.example (NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create User SQLModel in backend/app/models/user.py (id UUID, email, hashed_password, created_at)
- [ ] T007 Create Pydantic models in backend/app/models/user.py (RegisterRequest, LoginRequest, UserResponse, TokenResponse)
- [ ] T008 Create Alembic migration for users table in backend/alembic/versions/001_create_users_table.py
- [ ] T009 [P] Implement password service in backend/app/services/password_service.py (hash_password, verify_password with bcrypt)
- [ ] T010 [P] Implement JWT service in backend/app/services/jwt_service.py (create_token, verify_token using BETTER_AUTH_SECRET)
- [ ] T011 Create FastAPI app in backend/app/main.py with CORS middleware (allow frontend origin only)
- [ ] T012 [P] [Optional] Implement rate limiting middleware in backend/app/middleware/rate_limit.py (5 attempts per 15 minutes per IP) - optional for Phase II
- [ ] T013 Create dependency injection in backend/app/api/deps.py (get_current_user_id extracts user_id from JWT)
- [ ] T014 [P] Configure Better Auth in frontend/lib/auth.ts (email/password provider, BETTER_AUTH_SECRET)
- [ ] T015 [P] Create API client in frontend/lib/api-client.ts (includes JWT token in Authorization header)
- [ ] T016 [P] Install shadcn/ui components (Button, Card, Input, Form) in frontend/components/ui/
- [ ] T017 [P] Create pytest configuration in backend/tests/conftest.py with test database fixtures

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - New User Registration (Priority: P1)

**Goal**: Users can create accounts with email/password and access dashboard

**Independent Test**: Navigate to signup page, enter valid email and password, verify redirect to dashboard

- [X] T018 [P] [US1] Write tests for registration in backend/tests/integration/test_auth_routes.py (valid registration, duplicate email, invalid email, short password)
- [X] T019 [US1] Implement register_user in backend/app/services/auth_service.py (validate email, check duplicates, hash password, create user)
- [X] T020 [US1] Implement POST /api/auth/register in backend/app/api/routes/auth.py (call auth_service, generate JWT, return TokenResponse)
- [X] T021 [US1] Create signup form in frontend/components/auth/signup-form.tsx (email input, password input, validation, error display)
- [X] T022 [US1] Create login/signup page in frontend/app/(auth)/login/page.tsx with tab toggle
- [X] T023 [US1] Implement useAuth hook in frontend/hooks/use-auth.ts with registration mutation (TanStack Query)

**Checkpoint**: User Story 1 complete and independently testable

---

## Phase 4: User Story 2 - Existing User Login (Priority: P1)

**Goal**: Returning users can log in and access their dashboard

**Independent Test**: Create account, logout, login with same credentials, verify dashboard access

- [X] T024 [P] [US2] Write tests for login in backend/tests/integration/test_auth_routes.py (valid login, invalid password, non-existent email)
- [X] T025 [US2] Implement login_user in backend/app/services/auth_service.py (verify credentials, generate JWT)
- [X] T026 [US2] Implement POST /api/auth/login in backend/app/api/routes/auth.py (call auth_service, return TokenResponse)
- [X] T027 [US2] Create login form in frontend/components/auth/login-form.tsx (email input, password input, error display)
- [X] T028 [US2] Add login mutation to useAuth hook in frontend/hooks/use-auth.ts
- [X] T029 [US2] Implement redirect logic: logged-in users accessing /login redirect to /dashboard

**Checkpoint**: User Stories 1 AND 2 both work independently

---

## Phase 5: User Story 3 - JWT Token Management (Priority: P1)

**Goal**: Authenticated users remain logged in across page refreshes with automatic token validation

**Independent Test**: Login, refresh page, open new tabs, verify authentication persists

- [X] T030 [P] [US3] Write tests for token validation in backend/tests/unit/test_jwt_service.py (valid token, expired token, invalid signature)
- [ ] T031 [P] [Optional] [US3] Implement GET /api/auth/me in backend/app/api/routes/auth.py (return current user from JWT using get_current_user_id dependency) - optional, Better Auth can be used directly
- [X] T032 [US3] Create useUser hook in frontend/hooks/use-user.ts (fetch current user with TanStack Query, cache, auto-refetch)
- [X] T033 [US3] Create protected route wrapper in frontend/app/(protected)/layout.tsx (check auth, redirect to login if unauthenticated)
- [X] T034 [US3] Add session expiry handling with redirect to login and "Session expired" message

**Checkpoint**: User Stories 1, 2, AND 3 all work independently

---

## Phase 6: User Story 4 - User Logout (Priority: P1)

**Goal**: Users can securely end their session

**Independent Test**: Login, click logout, verify redirect to landing page and inability to access protected pages

- [X] T035 [P] [US4] Write tests for logout in backend/tests/integration/test_auth_routes.py (successful logout)
- [X] T036 [US4] Implement POST /api/auth/logout in backend/app/api/routes/auth.py (return success message - client clears token)
- [X] T037 [US4] Add logout mutation to useAuth hook in frontend/hooks/use-auth.ts (clear token, redirect to landing page)
- [X] T038 [US4] Create logout button in dashboard navbar and implement logout handler

**Checkpoint**: All P1 user stories (1-4) independently functional

---

## Phase 7: User Story 5 - Google OAuth Login (Priority: P2)

**Goal**: Users can authenticate using Google account

**Independent Test**: Click "Sign in with Google", complete authorization, verify login

- [ ] T039 [P] [US5] Write tests for OAuth in backend/tests/integration/test_auth_routes.py (new user, existing user, account linking)
- [ ] T040 [US5] Configure Google OAuth in frontend/lib/auth.ts (client ID, client secret, redirect URI)
- [ ] T041 [US5] Implement OAuth callback in backend/app/api/routes/auth.py (exchange code, create/retrieve user, generate JWT)
- [ ] T042 [US5] Add "Sign in with Google" button to frontend/app/(auth)/login/page.tsx
- [ ] T043 [US5] Implement account linking in backend/app/services/auth_service.py (link OAuth to existing email account)

**Checkpoint**: All user stories (1-5) independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories

- [ ] T044 [P] Write E2E tests in frontend/tests/e2e/auth-flow.spec.ts (register → dashboard, login → logout, session persistence)
- [ ] T045 [P] Add loading states and toast notifications to auth forms (shadcn/ui Toast)
- [ ] T046 [P] Implement form accessibility (ARIA labels, keyboard navigation, focus management)
- [ ] T047 [P] Add rate limiting error handling with retry-after display (if rate limiting implemented)
- [ ] T048 [P] Run full test suite and verify 80% coverage (pytest --cov, vitest --coverage)
- [ ] T049 Final constitution compliance check (all 6 principles) and code cleanup

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational completion
  - Can proceed in parallel (if staffed) or sequentially by priority (P1 first, then P2)
- **Polish (Phase 8)**: Depends on desired user stories being complete

### User Story Independence

- **US1 (Registration)**: Independent after Foundational
- **US2 (Login)**: Independent after Foundational (naturally tested after US1)
- **US3 (Session Management)**: Independent after Foundational (integrates with US1/US2)
- **US4 (Logout)**: Independent after Foundational (requires US2 for testing)
- **US5 (Google OAuth)**: Independent after Foundational

### Within Each User Story

- Tests first (TDD: Red → Green → Refactor)
- Backend services before API routes
- API routes before frontend components
- Frontend components before integration

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel
- Once Foundational completes, all user stories can start in parallel (if team capacity allows)
- All tests marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (Registration)
4. **STOP and VALIDATE**: Test independently
5. Deploy/demo if ready

### Incremental Delivery (Recommended)

1. Setup + Foundational → Foundation ready
2. Add US1 (Registration) → Test → Deploy (MVP!)
3. Add US2 (Login) → Test → Deploy
4. Add US3 (Session Management) → Test → Deploy
5. Add US4 (Logout) → Test → Deploy
6. Add US5 (Google OAuth) → Test → Deploy
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational done:
   - Developer A: US1 (Registration)
   - Developer B: US2 (Login)
   - Developer C: US3 (Session Management)
   - Developer D: US4 (Logout)
3. Stories complete and integrate independently
4. Developer E: US5 (Google OAuth) after P1 stories

---

## Notes

- Total tasks: 49 (within target range)
- [P] tasks = different files, no dependencies
- [Optional] tasks = can be skipped or added later
- [Story] label maps task to user story for traceability
- Each user story independently completable and testable
- TDD: Write tests first, verify they fail, then implement
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Target: 80% test coverage for auth logic (constitution requirement)
- No sessions table, no refresh token endpoint (stateless JWT)
- Every database query filtered by user_id from JWT
