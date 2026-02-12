# Tasks: Task CRUD Operations

**Input**: Design documents from `/specs/002-task-crud/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/tasks.openapi.yaml, quickstart.md

**Tests**: Test-First Development (TDD) is required per constitution. Tests are included for all user stories.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/app/`, `backend/tests/`, `frontend/tests/`
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for task CRUD components

- [ ] T001 Create backend task module structure at backend/app/models/task.py, backend/app/services/task_service.py, backend/app/api/tasks.py
- [ ] T002 [P] Create frontend dashboard structure at frontend/app/dashboard/page.tsx and frontend/components/dashboard/
- [ ] T003 [P] Create backend test structure at backend/tests/unit/test_task_service.py and backend/tests/integration/test_tasks_api.py
- [ ] T004 [P] Create frontend test structure at frontend/tests/unit/dashboard/ and frontend/tests/e2e/task-crud.spec.ts
- [ ] T005 [P] Verify shadcn/ui components exist: Button, Card, Dialog, Input, Textarea in frontend/components/ui/
- [ ] T006 [P] Verify TanStack Query installed and configured in frontend/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create Task SQLModel schema in backend/app/models/task.py (id, user_id FK, title, description, is_completed, timestamps)
- [ ] T008 Create Alembic migration for tasks table with indexes (user_id, composite user_id+created_at)
- [ ] T009 [P] Create Pydantic request/response models in backend/app/models/task.py (TaskCreate, TaskUpdate, TaskResponse)
- [ ] T010 [P] Verify get_current_user dependency exists in backend/app/api/deps.py (from 001-user-auth)
- [ ] T011 [P] Create API client functions in frontend/lib/api/tasks.ts (fetchTasks, createTask, toggleTask, updateTask, deleteTask)
- [ ] T012 [P] Create TanStack Query hooks in frontend/lib/hooks/use-tasks.ts (useTasksQuery, useCreateTaskMutation, useToggleTaskMutation, useUpdateTaskMutation, useDeleteTaskMutation)
- [ ] T013 Run Alembic migration to create tasks table in database

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Tasks with Filtering (Priority: P1) 🎯 MVP

**Goal**: Display all user tasks in responsive grid with sidebar filters (All/Pending/Completed)

**Independent Test**: Log in, navigate to /dashboard, verify tasks displayed in grid with working filters

### Tests for User Story 1 (TDD - Write FIRST, ensure they FAIL)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T014 [P] [US1] Backend unit test for TaskService.get_tasks() in backend/tests/unit/test_task_service.py (user-scoped filtering, sorting by created_at desc)
- [ ] T015 [P] [US1] Backend integration test for GET /api/tasks in backend/tests/integration/test_tasks_api.py (JWT validation, returns user tasks only, empty list for no tasks)
- [ ] T016 [P] [US1] Frontend unit test for TaskCard component in frontend/tests/unit/dashboard/task-card.test.tsx (renders title, description, badge, checkbox)
- [ ] T017 [P] [US1] Frontend unit test for TaskGrid component in frontend/tests/unit/dashboard/task-grid.test.tsx (responsive grid, empty state)
- [ ] T018 [P] [US1] Frontend unit test for Sidebar component in frontend/tests/unit/dashboard/sidebar.test.tsx (filter buttons, active state)
- [ ] T019 [P] [US1] E2E test for view tasks in frontend/tests/e2e/task-crud.spec.ts (navigate to dashboard, see tasks, filter by status)

### Implementation for User Story 1

- [ ] T020 [US1] Implement TaskService.get_tasks() in backend/app/services/task_service.py (query with user_id filter, order by created_at desc)
- [ ] T021 [US1] Implement GET /api/tasks endpoint in backend/app/api/tasks.py (JWT validation, call TaskService, return TaskListResponse)
- [ ] T022 [P] [US1] Create TaskCard component in frontend/components/dashboard/task-card.tsx (checkbox, title, description truncation, status badge, hover icons)
- [ ] T023 [P] [US1] Create TaskGrid component in frontend/components/dashboard/task-grid.tsx (responsive grid layout, empty state message)
- [ ] T024 [P] [US1] Create Sidebar component in frontend/components/dashboard/sidebar.tsx (All/Pending/Completed filter buttons)
- [ ] T025 [US1] Implement dashboard page in frontend/app/dashboard/page.tsx (useTasksQuery hook, client-side filtering, TaskGrid, Sidebar layout)
- [ ] T026 [US1] Add status badge styling in TaskCard (orange for Pending, green for Completed)
- [ ] T027 [US1] Verify US1 tests pass and dashboard displays tasks correctly with filters

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Add New Task (Priority: P1)

**Goal**: Create new tasks via modal form with title and optional description

**Independent Test**: Click "+ Add Task" button, enter title and description, verify task appears in list

### Tests for User Story 2 (TDD - Write FIRST, ensure they FAIL)

- [ ] T028 [P] [US2] Backend unit test for TaskService.create_task() in backend/tests/unit/test_task_service.py (creates task with user_id, validates title, sets is_completed=false)
- [ ] T029 [P] [US2] Backend integration test for POST /api/tasks in backend/tests/integration/test_tasks_api.py (JWT validation, creates task, returns 201, validation errors)
- [ ] T030 [P] [US2] Frontend unit test for AddTaskModal component in frontend/tests/unit/dashboard/add-task-modal.test.tsx (form fields, validation, submission)
- [ ] T031 [P] [US2] E2E test for add task in frontend/tests/e2e/task-crud.spec.ts (open modal, enter data, submit, verify task appears)

### Implementation for User Story 2

- [ ] T032 [US2] Implement TaskService.create_task() in backend/app/services/task_service.py (validate input, create Task with user_id, save to DB)
- [ ] T033 [US2] Implement POST /api/tasks endpoint in backend/app/api/tasks.py (JWT validation, call TaskService, return 201 with TaskResponse)
- [ ] T034 [P] [US2] Create AddTaskModal component in frontend/components/dashboard/add-task-modal.tsx (shadcn Dialog, form with title/description inputs, validation)
- [ ] T035 [US2] Integrate useCreateTaskMutation in AddTaskModal (optimistic update, invalidate queries on success, error handling)
- [ ] T036 [US2] Add "+ Add Task" button to dashboard navbar in frontend/app/dashboard/page.tsx (opens AddTaskModal)
- [ ] T037 [US2] Add frontend validation in AddTaskModal (title required, title max 200 chars, description max 1000 chars)
- [ ] T038 [US2] Verify US2 tests pass and task creation works with validation

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Toggle Task Completion Status (Priority: P1)

**Goal**: Toggle task completion with checkbox click (instant feedback with optimistic update)

**Independent Test**: Click checkbox on pending task, verify it becomes completed with green badge

### Tests for User Story 3 (TDD - Write FIRST, ensure they FAIL)

- [ ] T039 [P] [US3] Backend unit test for TaskService.toggle_task() in backend/tests/unit/test_task_service.py (toggles is_completed, updates updated_at, user ownership check)
- [ ] T040 [P] [US3] Backend integration test for PATCH /api/tasks/{id}/toggle in backend/tests/integration/test_tasks_api.py (JWT validation, toggles status, 403 for other user's task)
- [ ] T041 [P] [US3] E2E test for toggle completion in frontend/tests/e2e/task-crud.spec.ts (click checkbox, verify badge color change, verify persistence)

### Implementation for User Story 3

- [ ] T042 [US3] Implement TaskService.toggle_task() in backend/app/services/task_service.py (get task, verify user_id, toggle is_completed, update updated_at)
- [ ] T043 [US3] Implement PATCH /api/tasks/{id}/toggle endpoint in backend/app/api/tasks.py (JWT validation, call TaskService, return updated TaskResponse)
- [ ] T044 [US3] Implement useToggleTaskMutation with optimistic update in frontend/lib/hooks/use-tasks.ts (onMutate: update cache, onError: rollback, onSettled: refetch)
- [ ] T045 [US3] Add checkbox click handler to TaskCard in frontend/components/dashboard/task-card.tsx (call toggleMutation)
- [ ] T046 [US3] Verify US3 tests pass and toggle works with instant feedback and rollback on error

**Checkpoint**: All P1 user stories (MVP) should now be independently functional

---

## Phase 6: User Story 4 - Update Existing Task (Priority: P1)

**Goal**: Edit task title and description via modal form

**Independent Test**: Hover over task, click edit icon, modify title/description, verify changes appear

### Tests for User Story 4 (TDD - Write FIRST, ensure they FAIL)

- [ ] T047 [P] [US4] Backend unit test for TaskService.update_task() in backend/tests/unit/test_task_service.py (updates title/description, validates input, user ownership check)
- [ ] T048 [P] [US4] Backend integration test for PUT /api/tasks/{id} in backend/tests/integration/test_tasks_api.py (JWT validation, updates task, validation errors, 403 for other user)
- [ ] T049 [P] [US4] Frontend unit test for EditTaskModal component in frontend/tests/unit/dashboard/edit-task-modal.test.tsx (pre-filled form, validation, submission)
- [ ] T050 [P] [US4] E2E test for edit task in frontend/tests/e2e/task-crud.spec.ts (click edit icon, modify data, save, verify changes)

### Implementation for User Story 4

- [ ] T051 [US4] Implement TaskService.update_task() in backend/app/services/task_service.py (get task, verify user_id, validate input, update fields, save)
- [ ] T052 [US4] Implement PUT /api/tasks/{id} endpoint in backend/app/api/tasks.py (JWT validation, call TaskService, return updated TaskResponse)
- [ ] T053 [P] [US4] Create EditTaskModal component in frontend/components/dashboard/edit-task-modal.tsx (shadcn Dialog, pre-filled form, validation)
- [ ] T054 [US4] Integrate useUpdateTaskMutation in EditTaskModal (optimistic update, invalidate queries, error handling)
- [ ] T055 [US4] Add edit icon to TaskCard hover state in frontend/components/dashboard/task-card.tsx (Lucide Edit icon, opens EditTaskModal)
- [ ] T056 [US4] Verify US4 tests pass and task editing works with validation

**Checkpoint**: User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Delete Task (Priority: P1)

**Goal**: Delete task permanently with confirmation dialog

**Independent Test**: Hover over task, click delete icon, confirm deletion, verify task disappears

### Tests for User Story 5 (TDD - Write FIRST, ensure they FAIL)

- [ ] T057 [P] [US5] Backend unit test for TaskService.delete_task() in backend/tests/unit/test_task_service.py (deletes task, user ownership check, 404 if not found)
- [ ] T058 [P] [US5] Backend integration test for DELETE /api/tasks/{id} in backend/tests/integration/test_tasks_api.py (JWT validation, deletes task, 403 for other user)
- [ ] T059 [P] [US5] Frontend unit test for DeleteConfirmDialog component in frontend/tests/unit/dashboard/delete-confirm-dialog.test.tsx (confirmation message, cancel/delete buttons)
- [ ] T060 [P] [US5] E2E test for delete task in frontend/tests/e2e/task-crud.spec.ts (click delete icon, confirm, verify task disappears, verify persistence)

### Implementation for User Story 5

- [ ] T061 [US5] Implement TaskService.delete_task() in backend/app/services/task_service.py (get task, verify user_id, delete from DB)
- [ ] T062 [US5] Implement DELETE /api/tasks/{id} endpoint in backend/app/api/tasks.py (JWT validation, call TaskService, return 200 with success message)
- [ ] T063 [P] [US5] Create DeleteConfirmDialog component in frontend/components/dashboard/delete-confirm-dialog.tsx (shadcn AlertDialog, confirmation message, cancel/delete buttons)
- [ ] T064 [US5] Integrate useDeleteTaskMutation in DeleteConfirmDialog (optimistic removal, invalidate queries, error handling)
- [ ] T065 [US5] Add delete icon to TaskCard hover state in frontend/components/dashboard/task-card.tsx (Lucide Trash icon, opens DeleteConfirmDialog)
- [ ] T066 [US5] Verify US5 tests pass and task deletion works with confirmation

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T067 [P] Add loading states to all mutations (create, toggle, update, delete) with shadcn Spinner or skeleton
- [ ] T068 [P] Add error toast notifications for all mutation failures using shadcn Sonner
- [ ] T069 [P] Add success toast notifications for create/update/delete operations
- [ ] T070 [P] Implement responsive design for mobile (task grid 1 column, sidebar hamburger menu or bottom nav)
- [ ] T071 [P] Add hover effects to TaskCard (elevation, border glow) in frontend/components/dashboard/task-card.tsx
- [ ] T072 [P] Ensure edit/delete icons always visible on mobile (no hover state) in TaskCard
- [ ] T073 Test user data isolation (create two users, verify no cross-user data access)
- [ ] T074 Test performance with 1000+ tasks (load time <2s, scrolling 60fps)
- [ ] T075 Run quickstart.md validation checklist (all 18 test scenarios)
- [ ] T076 Run Lighthouse audit (Performance 90+, Accessibility 95+, SEO 100)
- [ ] T077 Code cleanup and refactoring (remove console.logs, unused imports, format code)
- [ ] T078 Update documentation (API docs, component docs, README)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1, US2, US3, US4, US5 (All P1 - MVP) can proceed in parallel after Foundational
  - Or sequentially in priority order (US1 → US2 → US3 → US4 → US5)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent of US1 (different components)
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Integrates with US1 (TaskCard checkbox) but independently testable
- **User Story 4 (P1)**: Can start after Foundational (Phase 2) - Integrates with US1 (TaskCard edit icon) but independently testable
- **User Story 5 (P1)**: Can start after Foundational (Phase 2) - Integrates with US1 (TaskCard delete icon) but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD Red-Green-Refactor)
- Backend: Models → Services → API endpoints
- Frontend: Components → Hooks → Integration
- Backend tests before backend implementation
- Frontend tests before frontend implementation
- Story complete and tests passing before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T006)
- All Foundational tasks marked [P] can run in parallel (T009-T012)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel (T014-T019, T028-T031, etc.)
- Backend and frontend implementations can proceed in parallel within a story
- All Polish tasks marked [P] can run in parallel (T067-T077)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write first):
Task: "Backend unit test for TaskService.get_tasks() in backend/tests/unit/test_task_service.py"
Task: "Backend integration test for GET /api/tasks in backend/tests/integration/test_tasks_api.py"
Task: "Frontend unit test for TaskCard component in frontend/tests/unit/dashboard/task-card.test.tsx"
Task: "Frontend unit test for TaskGrid component in frontend/tests/unit/dashboard/task-grid.test.tsx"
Task: "Frontend unit test for Sidebar component in frontend/tests/unit/dashboard/sidebar.test.tsx"
Task: "E2E test for view tasks in frontend/tests/e2e/task-crud.spec.ts"

# After tests fail, launch component implementations together:
Task: "Create TaskCard component in frontend/components/dashboard/task-card.tsx"
Task: "Create TaskGrid component in frontend/components/dashboard/task-grid.tsx"
Task: "Create Sidebar component in frontend/components/dashboard/sidebar.tsx"
```

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together (TDD - write first):
Task: "Backend unit test for TaskService.create_task() in backend/tests/unit/test_task_service.py"
Task: "Backend integration test for POST /api/tasks in backend/tests/integration/test_tasks_api.py"
Task: "Frontend unit test for AddTaskModal component in frontend/tests/unit/dashboard/add-task-modal.test.tsx"
Task: "E2E test for add task in frontend/tests/e2e/task-crud.spec.ts"

# After tests fail, launch implementations together:
Task: "Implement TaskService.create_task() in backend/app/services/task_service.py"
Task: "Create AddTaskModal component in frontend/components/dashboard/add-task-modal.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1-5 - All P1)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (View Tasks)
4. Complete Phase 4: User Story 2 (Add Task)
5. Complete Phase 5: User Story 3 (Toggle Complete)
6. Complete Phase 6: User Story 4 (Update Task)
7. Complete Phase 7: User Story 5 (Delete Task)
8. **STOP and VALIDATE**: Test all 5 P1 stories independently
9. Deploy/demo if ready (MVP with complete CRUD operations!)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (can view tasks)
3. Add User Story 2 → Test independently → Deploy/Demo (can add tasks)
4. Add User Story 3 → Test independently → Deploy/Demo (can complete tasks)
5. Add User Story 4 → Test independently → Deploy/Demo (can edit tasks)
6. Add User Story 5 → Test independently → Deploy/Demo (complete CRUD - MVP!)
7. Each story adds value without breaking previous stories
8. All 5 stories are P1 (critical for MVP launch)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (View Tasks)
   - Developer B: User Story 2 (Add Task)
   - Developer C: User Story 3 (Toggle Complete)
3. After P1 stories complete:
   - Developer A: User Story 4 (Update Task)
   - Developer B: User Story 5 (Delete Task)
   - Developer C: Polish & Testing
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD cycle: Write tests first (Red) → Implement (Green) → Refactor
- Verify tests fail before implementing (Red phase)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All 5 user stories (US1-US5) are P1 (MVP - mandatory for launch)
- Full-stack feature: backend (FastAPI + SQLModel) + frontend (Next.js + TanStack Query)
- User-scoped security: JWT validation + user_id filtering on all queries
- Performance targets: view <1s, create <10s, toggle <100ms, support 1000+ tasks
- Constitution compliance: exactly 5 core operations, no scope creep
