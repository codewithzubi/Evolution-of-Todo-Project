---
description: "Task list for frontend implementation - Task Management UI with Better Auth"
---

# Tasks: Task Management Frontend UI

**Input**: Design documents from `/specs/002-task-ui-frontend/`
**Prerequisites**: plan.md ✅ (created), spec.md ✅ (created)
**Tests**: Included - test tasks marked explicitly for each user story

**Organization**: Tasks grouped by user story (US1-US8) to enable independent implementation and testing. All 8 user stories from spec.md mapped with clear dependencies and parallelization markers.

---

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, etc.) from spec.md
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Frontend project initialization, configuration, and basic structure

- [ ] T001 Initialize Next.js 16 project with App Router structure in `frontend/`
- [ ] T002 [P] Configure TypeScript strict mode with compiler options in `frontend/tsconfig.json`
- [ ] T003 [P] Set up Tailwind CSS with responsive breakpoints in `frontend/tailwind.config.ts`
- [ ] T004 [P] Configure Vitest for unit/integration testing in `frontend/vitest.config.ts`
- [ ] T005 [P] Configure ESLint and Prettier in `frontend/.eslintrc.json` and `frontend/prettier.config.json`
- [ ] T006 Setup package.json scripts for dev, build, test, lint in `frontend/package.json`
- [ ] T007 Create environment template `.env.example` with API_BASE_URL, JWT_SECRET variables
- [ ] T008 Create root layout with Next.js App Router in `frontend/src/app/layout.tsx`
- [ ] T009 Setup API base client service with fetch wrapper in `frontend/src/services/api.ts`
- [ ] T010 [P] Create TypeScript types for User entity in `frontend/src/types/auth.ts`
- [ ] T011 [P] Create TypeScript types for Task entity in `frontend/src/types/task.ts`
- [ ] T012 [P] Create TypeScript types for API responses in `frontend/src/types/api.ts`

**Checkpoint**: Setup complete - foundation ready for core infrastructure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T013 Implement JWT token persistence utilities in `frontend/src/utils/auth.ts`
- [ ] T014 Create AuthContext for auth state management in `frontend/src/hooks/useAuth.ts`
- [ ] T015 Implement useLocalStorage hook for secure token storage in `frontend/src/hooks/useLocalStorage.ts`
- [ ] T016 Setup Next.js middleware for route protection in `frontend/src/middleware.ts`
- [ ] T017 [P] Create reusable Button component in `frontend/src/components/common/Button.tsx`
- [ ] T018 [P] Create reusable Input component in `frontend/src/components/common/Input.tsx`
- [ ] T019 [P] Create reusable Card component in `frontend/src/components/common/Card.tsx`
- [ ] T020 [P] Create Loading spinner component in `frontend/src/components/common/Loading.tsx`
- [ ] T021 [P] Create ErrorBoundary component in `frontend/src/components/common/ErrorBoundary.tsx`
- [ ] T022 [P] Create Toast notification system in `frontend/src/components/common/Toast.tsx`
- [ ] T023 Create Header component with user info & logout in `frontend/src/components/layout/Header.tsx` (depends on T014)
- [ ] T024 [P] Create Form field components (FormInput, FormTextarea) in `frontend/src/components/common/Form.tsx`
- [ ] T025 Implement API error handling utility in `frontend/src/utils/errors.ts`
- [ ] T026 Implement date formatting utilities in `frontend/src/utils/format.ts`
- [ ] T027 Implement form validation utilities in `frontend/src/utils/validation.ts`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable users to create accounts and log in securely with JWT authentication and Better Auth integration

**Independent Test**: User can signup → receive JWT → logout → not able to access protected pages. Verify token stored in localStorage.

### Tests for User Story 1

- [ ] T028 [P] [US1] Contract test for POST /api/auth/signup in `frontend/tests/contract/auth-signup.contract.test.ts`
- [ ] T029 [P] [US1] Contract test for POST /api/auth/login in `frontend/tests/contract/auth-login.contract.test.ts`
- [ ] T030 [P] [US1] Contract test for JWT token validation in `frontend/tests/contract/auth-token.contract.test.ts`
- [ ] T031 [US1] Integration test for full auth workflow (signup→login→logout) in `frontend/tests/integration/auth.integration.test.ts`

### Implementation for User Story 1

- [ ] T032 [P] [US1] Implement auth service with signup/login/logout API calls in `frontend/src/services/auth.service.ts`
- [ ] T033 [P] [US1] Integrate Better Auth library in `frontend/src/lib/better-auth.ts` (depends on T032)
- [ ] T034 [US1] Build LoginPage with email/password form in `frontend/src/app/auth/login/page.tsx` (depends on T032)
- [ ] T035 [US1] Add form validation and error display on LoginPage in `frontend/src/app/auth/login/page.tsx` (depends on T034)
- [ ] T036 [US1] Build SignupPage with registration form in `frontend/src/app/auth/signup/page.tsx` (depends on T032)
- [ ] T037 [US1] Add form validation and error display on SignupPage in `frontend/src/app/auth/signup/page.tsx` (depends on T036)
- [ ] T038 [US1] Implement token refresh logic in API client in `frontend/src/services/api.ts` (depends on T009)
- [ ] T039 [US1] Create login/signup layout wrapper in `frontend/src/components/layout/AuthLayout.tsx`
- [ ] T040 [US1] Add unit tests for LoginPage component in `frontend/tests/unit/auth/LoginPage.test.tsx`
- [ ] T041 [US1] Add unit tests for SignupPage component in `frontend/tests/unit/auth/SignupPage.test.tsx`
- [ ] T042 [US1] Add unit tests for useAuth hook in `frontend/tests/unit/hooks/useAuth.test.ts`

**Checkpoint**: User Story 1 complete - authentication flow fully functional and testable independently

---

## Phase 4: User Story 2 - Task List with Pagination (Priority: P1) 🎯 MVP

**Goal**: Display authenticated user's tasks in paginated list format with clear task information and navigation

**Independent Test**: Logged-in user can view 10 tasks per page, navigate pages, see pagination controls. Task list shows title, description preview, due date, completion status.

### Tests for User Story 2

- [ ] T043 [P] [US2] Contract test for GET /api/users/{id}/tasks in `frontend/tests/contract/task-list.contract.test.ts`
- [ ] T044 [P] [US2] Contract test for pagination with offset/limit in `frontend/tests/contract/task-pagination.contract.test.ts`
- [ ] T045 [US2] Integration test for task list load and pagination in `frontend/tests/integration/task-list.integration.test.ts`

### Implementation for User Story 2

- [ ] T046 [P] [US2] Implement task service with getTasks API call in `frontend/src/services/task.service.ts`
- [ ] T047 [P] [US2] Setup TanStack Query (React Query) client in `frontend/src/lib/query.ts`
- [ ] T048 [US2] Create useTask hook for task queries in `frontend/src/hooks/useTask.ts` (depends on T046, T047)
- [ ] T049 [US2] Build TaskListPage with pagination in `frontend/src/app/tasks/page.tsx` (depends on T048)
- [ ] T050 [US2] Create TaskItem component displaying individual task in `frontend/src/components/tasks/TaskItem.tsx`
- [ ] T051 [US2] Create TaskList component rendering list of TaskItems in `frontend/src/components/tasks/TaskList.tsx` (depends on T050)
- [ ] T052 [US2] Add pagination controls component in `frontend/src/components/common/Pagination.tsx`
- [ ] T053 [US2] Implement empty state message when no tasks in `frontend/src/components/tasks/EmptyState.tsx`
- [ ] T054 [US2] Add loading skeleton for task list in `frontend/src/components/tasks/TaskListSkeleton.tsx`
- [ ] T055 [US2] Add error state handling with retry button in `frontend/src/app/tasks/page.tsx` (depends on T049)
- [ ] T056 [US2] Add unit tests for TaskListPage component in `frontend/tests/unit/pages/TaskListPage.test.tsx`
- [ ] T057 [US2] Add unit tests for TaskList component in `frontend/tests/unit/components/TaskList.test.tsx`
- [ ] T058 [US2] Add unit tests for Pagination component in `frontend/tests/unit/components/Pagination.test.tsx`

**Checkpoint**: User Story 2 complete - task list view fully functional with pagination

---

## Phase 5: User Story 3 - Create Task (Priority: P1) 🎯 MVP

**Goal**: Allow users to create new tasks with title, optional description and due date through intuitive form

**Independent Test**: User can access create task form, fill in title, submit, and task appears in list with success notification. Form validation prevents empty titles.

### Tests for User Story 3

- [ ] T059 [P] [US3] Contract test for POST /api/users/{id}/tasks in `frontend/tests/contract/task-create.contract.test.ts`
- [ ] T060 [P] [US3] Contract test for task validation schema in `frontend/tests/contract/task-validation.contract.test.ts`
- [ ] T061 [US3] Integration test for create task workflow in `frontend/tests/integration/task-create.integration.test.ts`

### Implementation for User Story 3

- [ ] T062 [P] [US3] Implement createTask API call in task service in `frontend/src/services/task.service.ts` (depends on T046)
- [ ] T063 [P] [US3] Create TaskCreateForm component with inputs in `frontend/src/components/tasks/TaskCreateForm.tsx`
- [ ] T064 [US3] Add form validation for title (required, max 255 chars) in `frontend/src/components/tasks/TaskCreateForm.tsx` (depends on T063)
- [ ] T065 [US3] Add optional description and due date inputs in `frontend/src/components/tasks/TaskCreateForm.tsx` (depends on T063)
- [ ] T066 [US3] Create TaskCreateModal wrapper for form in `frontend/src/components/tasks/TaskCreateModal.tsx` (depends on T063)
- [ ] T067 [US3] Add "Create Task" button to TaskListPage in `frontend/src/app/tasks/page.tsx` (depends on T049)
- [ ] T068 [US3] Implement modal open/close logic in `frontend/src/app/tasks/page.tsx` (depends on T067)
- [ ] T069 [US3] Add form submission with success/error handling in `frontend/src/components/tasks/TaskCreateForm.tsx` (depends on T064)
- [ ] T070 [US3] Refresh task list after successful creation in `frontend/src/app/tasks/page.tsx` (depends on T069)
- [ ] T071 [US3] Add success toast notification after task creation in `frontend/src/components/tasks/TaskCreateForm.tsx` (depends on T069)
- [ ] T072 [US3] Add unit tests for TaskCreateForm component in `frontend/tests/unit/components/TaskCreateForm.test.tsx`
- [ ] T073 [US3] Add unit tests for TaskCreateModal component in `frontend/tests/unit/components/TaskCreateModal.test.tsx`

**Checkpoint**: User Story 3 complete - users can create and view tasks (MVP feature set complete)

---

## Phase 6: User Story 4 - Mark Task Complete (Priority: P1) 🎯 MVP

**Goal**: Allow users to quickly toggle task completion status directly from the list view with immediate visual feedback

**Independent Test**: User can click checkbox on task, see visual change (strikethrough), and backend reflects completed status. Incomplete tasks can be toggled back to incomplete.

### Tests for User Story 4

- [ ] T074 [P] [US4] Contract test for PATCH /api/users/{id}/tasks/{id}/complete in `frontend/tests/contract/task-complete.contract.test.ts`
- [ ] T075 [US4] Integration test for task completion toggle in `frontend/tests/integration/task-complete.integration.test.ts`

### Implementation for User Story 4

- [ ] T076 [P] [US4] Implement toggleTaskComplete API call in task service in `frontend/src/services/task.service.ts` (depends on T046)
- [ ] T077 [US4] Add completion toggle checkbox to TaskItem component in `frontend/src/components/tasks/TaskItem.tsx` (depends on T050)
- [ ] T078 [US4] Implement click handler for completion toggle in `frontend/src/components/tasks/TaskItem.tsx` (depends on T077)
- [ ] T079 [US4] Add loading state during toggle in `frontend/src/components/tasks/TaskItem.tsx` (depends on T078)
- [ ] T080 [US4] Add visual feedback (strikethrough/dimmed) for completed tasks in `frontend/src/components/tasks/TaskItem.tsx`
- [ ] T081 [US4] Handle API errors and revert toggle on failure in `frontend/src/components/tasks/TaskItem.tsx` (depends on T079)
- [ ] T082 [US4] Show error toast if completion toggle fails in `frontend/src/components/tasks/TaskItem.tsx` (depends on T081)
- [ ] T083 [US4] Update task in cache after successful toggle in `frontend/src/hooks/useTask.ts` (depends on T048)
- [ ] T084 [US4] Add unit tests for TaskItem completion toggle in `frontend/tests/unit/components/TaskItem.test.tsx`

**Checkpoint**: User Story 4 complete - task completion fully functional with optimistic UI updates

---

## Phase 7: User Story 5 - Update Task (Priority: P2)

**Goal**: Allow users to edit task details (title, description, due date) after creation with persistence to backend

**Independent Test**: User can click edit on task, modify fields, save changes, and see updated values in list. No API call if values unchanged.

### Tests for User Story 5

- [ ] T085 [P] [US5] Contract test for PUT /api/users/{id}/tasks/{id} in `frontend/tests/contract/task-update.contract.test.ts`
- [ ] T086 [US5] Integration test for task update workflow in `frontend/tests/integration/task-update.integration.test.ts`

### Implementation for User Story 5

- [ ] T087 [P] [US5] Implement updateTask API call in task service in `frontend/src/services/task.service.ts` (depends on T046)
- [ ] T088 [P] [US5] Create TaskEditForm component with pre-filled values in `frontend/src/components/tasks/TaskEditForm.tsx`
- [ ] T089 [US5] Add form validation matching create form rules in `frontend/src/components/tasks/TaskEditForm.tsx` (depends on T088)
- [ ] T090 [US5] Create TaskEditModal wrapper for form in `frontend/src/components/tasks/TaskEditModal.tsx` (depends on T088)
- [ ] T091 [US5] Add "Edit" button to TaskItem component in `frontend/src/components/tasks/TaskItem.tsx` (depends on T050)
- [ ] T092 [US5] Open edit modal with task pre-filled on button click in `frontend/src/app/tasks/page.tsx` (depends on T091)
- [ ] T093 [US5] Implement optimization - skip API call if values unchanged in `frontend/src/components/tasks/TaskEditForm.tsx` (depends on T089)
- [ ] T094 [US5] Handle API errors in edit form with user feedback in `frontend/src/components/tasks/TaskEditForm.tsx` (depends on T093)
- [ ] T095 [US5] Update task in cache after successful edit in `frontend/src/hooks/useTask.ts` (depends on T048)
- [ ] T096 [US5] Add success toast notification after task update in `frontend/src/components/tasks/TaskEditForm.tsx`
- [ ] T097 [US5] Add unit tests for TaskEditForm component in `frontend/tests/unit/components/TaskEditForm.test.tsx`

**Checkpoint**: User Story 5 complete - task editing fully functional with optimizations

---

## Phase 8: User Story 6 - Delete Task (Priority: P2)

**Goal**: Enable users to delete tasks with confirmation to prevent accidental deletion

**Independent Test**: User can click delete on task, see confirmation dialog, confirm deletion, and task disappears from list. Can cancel to keep task.

### Tests for User Story 6

- [ ] T098 [P] [US6] Contract test for DELETE /api/users/{id}/tasks/{id} in `frontend/tests/contract/task-delete.contract.test.ts`
- [ ] T099 [US6] Integration test for task deletion workflow in `frontend/tests/integration/task-delete.integration.test.ts`

### Implementation for User Story 6

- [ ] T100 [P] [US6] Implement deleteTask API call in task service in `frontend/src/services/task.service.ts` (depends on T046)
- [ ] T101 [US6] Create ConfirmDeleteModal component in `frontend/src/components/common/ConfirmDeleteModal.tsx`
- [ ] T102 [US6] Add "Delete" button to TaskItem component in `frontend/src/components/tasks/TaskItem.tsx` (depends on T050)
- [ ] T103 [US6] Show confirmation dialog on delete button click in `frontend/src/app/tasks/page.tsx` (depends on T102)
- [ ] T104 [US6] Implement deletion with loading state in `frontend/src/components/common/ConfirmDeleteModal.tsx` (depends on T101)
- [ ] T105 [US6] Handle API errors with retry option in `frontend/src/components/common/ConfirmDeleteModal.tsx` (depends on T104)
- [ ] T106 [US6] Remove task from cache after successful deletion in `frontend/src/hooks/useTask.ts` (depends on T048)
- [ ] T107 [US6] Show success toast notification after deletion in `frontend/src/components/common/ConfirmDeleteModal.tsx` (depends on T106)
- [ ] T108 [US6] Add unit tests for ConfirmDeleteModal component in `frontend/tests/unit/components/ConfirmDeleteModal.test.tsx`

**Checkpoint**: User Story 6 complete - task deletion with confirmation working

---

## Phase 9: User Story 7 - Task Detail View (Priority: P2)

**Goal**: Display complete task details in focused view with edit and delete options

**Independent Test**: User can click on task in list, see all details (title, full description, due date, created_at, completed status), perform edit/delete actions.

### Tests for User Story 7

- [ ] T109 [P] [US7] Contract test for GET /api/users/{id}/tasks/{id} in `frontend/tests/contract/task-detail.contract.test.ts`
- [ ] T110 [US7] Integration test for task detail view and actions in `frontend/tests/integration/task-detail.integration.test.ts`

### Implementation for User Story 7

- [ ] T111 [P] [US7] Build TaskDetailPage in `frontend/src/app/tasks/[id]/page.tsx`
- [ ] T112 [US7] Fetch task details on page load using useTask hook in `frontend/src/app/tasks/[id]/page.tsx` (depends on T111)
- [ ] T113 [US7] Display all task fields (title, description, due_date, created_at, updated_at, status) in `frontend/src/app/tasks/[id]/page.tsx` (depends on T112)
- [ ] T114 [US7] Add completion toggle checkbox on detail page in `frontend/src/app/tasks/[id]/page.tsx` (depends on T113)
- [ ] T115 [US7] Add Edit button linking to edit modal in `frontend/src/app/tasks/[id]/page.tsx` (depends on T113)
- [ ] T116 [US7] Add Delete button with confirmation in `frontend/src/app/tasks/[id]/page.tsx` (depends on T113)
- [ ] T117 [US7] Add back/close button to return to task list in `frontend/src/app/tasks/[id]/page.tsx` (depends on T113)
- [ ] T118 [US7] Add loading skeleton for task detail in `frontend/src/components/tasks/TaskDetailSkeleton.tsx`
- [ ] T119 [US7] Add error state with retry in `frontend/src/app/tasks/[id]/page.tsx` (depends on T112)
- [ ] T120 [US7] Add unit tests for TaskDetailPage component in `frontend/tests/unit/pages/TaskDetailPage.test.tsx`

**Checkpoint**: User Story 7 complete - task detail view fully functional

---

## Phase 10: User Story 8 - Responsive Design (Priority: P1) 🎯 MVP

**Goal**: Ensure all pages and components work optimally on mobile (375px), tablet (768px), and desktop (1024px+) devices

**Independent Test**: All pages responsive at 375px, 768px, 1024px with readable text, accessible buttons, proper form layout on mobile. Touch targets ≥48px height.

### Testing for User Story 8

- [ ] T121 [P] [US8] Responsive design testing on mobile 375px in all pages and components
- [ ] T122 [P] [US8] Responsive design testing on tablet 768px with layout adaptation
- [ ] T123 [P] [US8] Responsive design testing on desktop 1024px+ with full-width optimization
- [ ] T124 [P] [US8] Verify all buttons and inputs are ≥48px height on mobile (touch target sizing)
- [ ] T125 [P] [US8] Verify form inputs don't get hidden by mobile keyboard in `frontend/src/components/tasks/TaskCreateForm.tsx`
- [ ] T126 [US8] Add responsive Tailwind breakpoints to all components (already in config)
- [ ] T127 [US8] Test Header responsiveness and mobile navigation in `frontend/src/components/layout/Header.tsx`
- [ ] T128 [US8] Test TaskList pagination controls on mobile screens in `frontend/src/components/common/Pagination.tsx`
- [ ] T129 [US8] Verify TaskItem layout adapts to narrow screens in `frontend/src/components/tasks/TaskItem.tsx`
- [ ] T130 [US8] Verify forms stack vertically on mobile in `frontend/src/components/tasks/TaskCreateForm.tsx`

**Checkpoint**: User Story 8 complete - fully responsive design across all breakpoints

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories, quality gates, and production readiness

### Code Quality & Testing

- [ ] T131 [P] Run ESLint across all frontend code and fix violations in `frontend/src/`
- [ ] T132 [P] Run TypeScript strict mode check and fix all errors in `frontend/src/`
- [ ] T133 [P] Generate test coverage report with `vitest --coverage` in `frontend/`
- [ ] T134 Verify test coverage ≥70% - add unit tests if needed for coverage gaps
- [ ] T135 [P] Add unit tests for utility functions in `frontend/tests/unit/utils/`
- [ ] T136 [P] Add unit tests for API service error handling in `frontend/tests/unit/services/`
- [ ] T137 [P] Add unit tests for form validation utilities in `frontend/tests/unit/utils/validation.test.ts`

### Accessibility & UX

- [ ] T138 [P] Add ARIA labels to all interactive elements across components
- [ ] T139 [P] Verify semantic HTML (proper heading hierarchy, etc.) across all pages
- [ ] T140 [P] Test keyboard navigation (Tab through all pages, no keyboard traps)
- [ ] T141 [P] Verify color contrast meets WCAG AA (4.5:1 for normal text, 3:1 for large)
- [ ] T142 Add skip-to-main-content link in Header component in `frontend/src/components/layout/Header.tsx`
- [ ] T143 [P] Test with screen reader (NVDA, JAWS, VoiceOver)

### Performance Optimization

- [ ] T144 [P] Implement code splitting for pages in `frontend/src/app/`
- [ ] T145 [P] Add dynamic imports for modals to reduce bundle size
- [ ] T146 [P] Lazy load TaskItem components for large lists (virtualization if >1000 items)
- [ ] T147 Measure and optimize First Contentful Paint (FCP) - target <2s
- [ ] T148 Measure and optimize Largest Contentful Paint (LCP) - target <2.5s
- [ ] T149 Verify bundle size <200KB gzipped with webpack-bundle-analyzer

### Documentation & Setup

- [ ] T150 Create comprehensive README.md with project overview, setup instructions, tech stack
- [ ] T151 Update quickstart.md with step-by-step developer onboarding guide
- [ ] T152 Add JSDoc comments to all components documenting props and behavior
- [ ] T153 Add JSDoc comments to all API service methods with example usage
- [ ] T154 Document authentication flow in `frontend/CLAUDE.md`
- [ ] T155 Create FRONTEND.md with component library, patterns, and guidelines

### Error Handling & Edge Cases

- [ ] T156 [P] Handle JWT token expiration - show session expired modal and redirect to login
- [ ] T157 [P] Handle network errors with retry logic for all API calls
- [ ] T158 [P] Handle 404 errors (task doesn't exist) with friendly message
- [ ] T159 [P] Handle 403 errors (access another user's task) with permission denied message
- [ ] T160 [P] Handle localStorage full error gracefully with user guidance
- [ ] T161 [P] Handle rapid successive updates (queue requests or show conflict message)
- [ ] T162 Handle form submission with network failure - preserve form data for retry

### Security & Best Practices

- [ ] T163 [P] Verify no secrets committed to code (API keys, tokens in files)
- [ ] T164 [P] Verify no console.log statements with sensitive data
- [ ] T165 [P] Add Content Security Policy headers in next.config.ts
- [ ] T166 [P] Verify XSS prevention - no dangerouslySetInnerHTML used
- [ ] T167 [P] Verify CSRF protection - all state-changing requests use POST/PUT/DELETE
- [ ] T168 Verify JWT verification on every page load - refresh if expired

### Integration & E2E

- [ ] T169 Cross-browser testing: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- [ ] T170 Run full E2E test suite: signup → login → create task → complete task → delete task → logout
- [ ] T171 Test with backend API in staging environment
- [ ] T172 Load testing with 100+ concurrent users using k6 or similar
- [ ] T173 Validate all API responses match expected schema from backend spec

### Final Validation

- [ ] T174 Verify all 8 user stories independently testable and functional
- [ ] T175 Verify all acceptance criteria from spec.md are met
- [ ] T176 Run full test suite: `pnpm test`
- [ ] T177 Run full linting: `pnpm lint`
- [ ] T178 Run full type check: `pnpm type-check`
- [ ] T179 Run build: `pnpm build` - verify no errors
- [ ] T180 Verify production build starts without errors: `pnpm start`

**Checkpoint**: Polish complete - production-ready frontend

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately (12 tasks, ~2 days)
- **Foundational (Phase 2)**: Depends on Setup (15 tasks, ~3 days) - CRITICAL, BLOCKS all stories
- **User Stories (Phases 3-10)**: All depend on Foundational completion
  - User Story 1 (Auth): Can start after Foundational (11 tasks, ~2 days)
  - User Story 2 (Task List): Can start after US1 or parallel after Foundational (13 tasks, ~2.5 days)
  - User Story 3 (Create Task): Can start after US2 or parallel (12 tasks, ~2 days)
  - User Story 4 (Complete Task): Can start after US2 or parallel (8 tasks, ~1.5 days)
  - User Story 5 (Update Task): Can start after US3 or parallel (10 tasks, ~2 days)
  - User Story 6 (Delete Task): Can start after US5 or parallel (8 tasks, ~1.5 days)
  - User Story 7 (Detail View): Can start after US6 or parallel (10 tasks, ~2 days)
  - User Story 8 (Responsive): Can run throughout all phases (10 tasks, ~1.5 days)
- **Polish (Phase 11)**: Depends on all desired stories being complete (50 tasks, ~5 days)

### User Story Dependencies

All user stories are **independent after Foundational phase**:

- **US1 (Auth)**: No dependencies on other stories
- **US2 (Task List)**: Independent of US1 (can start in parallel after Foundational)
- **US3 (Create)**: Independent of US1, US2 (can start in parallel after Foundational)
- **US4 (Complete)**: Independent of US1, US2, US3 (can start in parallel after Foundational)
- **US5 (Update)**: Independent of other stories (can start in parallel after Foundational)
- **US6 (Delete)**: Independent of other stories (can start in parallel after Foundational)
- **US7 (Detail)**: Independent of other stories (can start in parallel after Foundational)
- **US8 (Responsive)**: Can run in parallel with all other story implementation

### Task Dependencies (Within Each Phase)

**Within Each Story**:
- Contract tests (marked [P]) can run in parallel
- Models/components (marked [P]) can run in parallel
- Services before endpoints
- Core implementation before integration/tests

**Cross-Story Task Dependencies**:
- T032, T046, T076, etc. (API service calls) depend on T009 (API base client) from Setup
- T034-T037 (Auth pages) depend on T032 (auth service)
- T049-T057 (Task list) depend on T046, T047 (task service and query client)

### Parallel Opportunities

**Phase 1 (Setup)**:
- T002-T005 can run in parallel (different config files)
- T010-T012 can run in parallel (different type files)
- Overall: 12 tasks, with ~8 parallelizable → ~4 days wall-clock time

**Phase 2 (Foundational)**:
- T017-T022 can run in parallel (different components)
- T024 can run with T017-T022
- Overall: 15 tasks, with ~10 parallelizable → ~4 days wall-clock time

**Phase 3 (US1 Auth)**:
- T028-T030 contract tests can run in parallel
- T032, T033 can run in parallel
- Overall: 11 tasks, with ~5 parallelizable → ~3 days wall-clock time

**Phase 4 (US2 Task List)**:
- T043-T044 contract tests can run in parallel
- T046, T047 can run in parallel
- Overall: 13 tasks, with ~5 parallelizable → ~3.5 days wall-clock time

**Phases 5-10 (US3-US8)**:
- Each story has 2-4 parallelizable tasks
- Different stories can run in parallel by different developers
- Example: 5 developers on 5 stories = ~1.5 days per story wall-clock time

**Phase 11 (Polish)**:
- T131-T146 marked [P] can run in parallel
- ~30 of 50 tasks are parallelizable
- Overall: 50 tasks, with ~30 parallelizable → ~3 days wall-clock time

### Total Timeline

**Sequential (1 developer)**:
- Setup: 3 days
- Foundational: 4 days (BLOCKS stories)
- Stories 1-8 sequential: 2 + 2.5 + 2 + 1.5 + 2 + 1.5 + 2 + 1.5 = 15 days
- Polish: 3 days
- **Total: ~25-28 days**

**Parallel (5 developers after Foundational)**:
- Setup: 3 days
- Foundational: 4 days
- Stories 1-8 in parallel: ~2 days (all working on different stories)
- Polish: 3 days
- **Total: ~12 days wall-clock time**

---

## Parallel Example: After Foundational Phase

With adequate team capacity, launch all story phases in parallel:

```
Developer 1: US1 Auth (T028-T042)
Developer 2: US2 Task List (T043-T058)
Developer 3: US3 Create Task (T059-T073)
Developer 4: US4 Complete Task (T074-T084)
Developer 5: US5 Update Task (T085-T097) + US6 Delete Task (T098-T108) after US5
```

All stories proceed in parallel, completing ~2 days after starting (with realistic dependencies within stories).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. **Complete Phase 1**: Setup (days 1-3)
2. **Complete Phase 2**: Foundational (days 3-6)
3. **Complete Phase 3**: User Story 1 - Auth (days 7-8)
4. **STOP and VALIDATE**: Test auth flow independently
5. **Deploy/Demo**: Basic auth working

**MVP Completed**: Users can signup/login with JWT authentication ✅

### Incremental Delivery (Progressive Value)

1. Setup + Foundational (days 1-6)
2. Add US1 Auth (days 7-8) → Deploy MVP
3. Add US2 Task List (days 9-10.5) → Users see tasks
4. Add US3 Create Task (days 11-12.5) → Users create tasks
5. Add US4 Complete Task (days 13-14) → Core MVP complete
6. Add US5 Update Task (days 15-16.5) → Enhanced features
7. Add US6 Delete Task (days 17-18) → Full CRUD
8. Add US7 Detail View (days 19-20.5) → Enhanced UX
9. Add US8 Responsive (parallel with all above)
10. Polish (days 21-23) → Production ready

**Each increment adds measurable user value without breaking previous features**

### Team Strategy (5 Developers)

**Day 1-6**: All 5 developers on Setup + Foundational (knowledge sharing, code review)

**Day 7+**: Parallel execution
- Dev 1: US1 Auth
- Dev 2: US2 Task List
- Dev 3: US3 Create + US4 Complete
- Dev 4: US5 Update + US6 Delete
- Dev 5: US7 Detail + US8 Responsive

**Integration**: As each story completes, merge to main branch with tests passing

**Polish**: All 5 developers on Phase 11 for final quality gates

---

## Notes

- **[P] tasks** = parallelizable (different files, no inter-task dependencies)
- **[Story] labels** = maps task to specific user story for traceability
- **Each user story** independently completable and testable after Foundational phase
- **Tests first**: Contract tests written and failing BEFORE implementation
- **Commit frequently**: After each task or logical group (T001, T002-T005, T006-T008, etc.)
- **Stop at checkpoints**: Validate story independently before proceeding
- **Avoid**: Cross-story hard dependencies (stories should integrate, not block each other)

### Task Execution Checklist

For each task T-XXX:
- [ ] Read task description carefully
- [ ] Verify dependencies are complete (listed in description)
- [ ] Write code following constitution principles (Task ID comments, spec references)
- [ ] Run tests: `pnpm test` for unit tests
- [ ] Run linter: `pnpm lint` for ESLint violations
- [ ] Run type check: `pnpm type-check` for TypeScript errors
- [ ] Commit with message: `[Task]: T-XXX, [From]: specs/002-task-ui-frontend/spec.md#US-X`
- [ ] Mark task as [X] complete in this file
- [ ] Proceed to next task or checkpoint validation

---

## Success Criteria Summary

### Phase 1-2 Completion (Setup + Foundational)
- [ ] Project structure created per plan.md
- [ ] TypeScript strict mode enabled with zero errors
- [ ] All common components available and tested
- [ ] API base client with JWT handling ready
- [ ] Foundation ready for user story implementation

### Phase 3-10 Completion (All User Stories)
- [ ] 8 user stories fully implemented
- [ ] Each story independently testable
- [ ] Total test coverage ≥70%
- [ ] Zero ESLint violations
- [ ] Zero TypeScript errors in strict mode
- [ ] All API integrations working with backend

### Phase 11 Completion (Polish)
- [ ] All edge cases handled with friendly error messages
- [ ] Responsive design tested at all breakpoints
- [ ] Accessibility audit passed (WCAG AA)
- [ ] Performance targets met (<2s FCP, <1s task list load)
- [ ] Security hardening complete
- [ ] Production build passes all checks

### Ready for Deployment
- [ ] All tests passing (`pnpm test`)
- [ ] Linting clean (`pnpm lint`)
- [ ] Type checking clean (`pnpm type-check`)
- [ ] Build succeeds (`pnpm build`)
- [ ] Production start works (`pnpm start`)
- [ ] E2E tests pass with backend
- [ ] All documentation updated

---

**Status**: ✅ Ready for `/sp.implement` execution

**Next Steps**: Run `/sp.implement` command to autonomously execute all tasks in phase/parallel order, or begin manual execution starting with Phase 1 (Setup) tasks.

