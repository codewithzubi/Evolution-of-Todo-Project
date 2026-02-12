# Quickstart Guide: Task CRUD Operations Testing

**Feature**: 002-task-crud
**Date**: 2026-02-09
**Purpose**: Test scenarios and acceptance criteria for task CRUD implementation

## Prerequisites

- Authentication system (001-user-auth) complete and functional
- Backend server running (`uvicorn app.main:app --reload` in backend/)
- Frontend development server running (`npm run dev` in frontend/)
- Test user account created and authenticated
- Modern browser (Chrome, Firefox, Safari, or Edge)

## Test Scenarios

### Scenario 1: View Tasks with All Filter

**User Story**: View Tasks with Filtering (US1)

**Test Steps**:
1. Log in with test user credentials
2. Navigate to `/dashboard`
3. Verify "All Tasks" filter is selected by default in sidebar
4. Observe task grid in main area

**Expected Results**:
- ✅ Dashboard loads within 1 second
- ✅ All tasks (pending + completed) displayed in responsive grid
- ✅ Tasks sorted by creation date (newest first)
- ✅ Each task card shows: checkbox, title, truncated description, status badge
- ✅ Pending tasks have orange badge
- ✅ Completed tasks have green badge
- ✅ Grid is responsive: 1 column mobile, 2-3 columns desktop

**Acceptance Criteria**:
- If user has 0 tasks: Empty state message "No tasks yet. Click + Add Task to get started"
- If user has 1000+ tasks: Page loads in under 2 seconds without performance issues
- Tasks are isolated to authenticated user (no other users' tasks visible)

---

### Scenario 2: Filter Tasks by Pending Status

**User Story**: View Tasks with Filtering (US1)

**Test Steps**:
1. User is on dashboard with mixed tasks (some pending, some completed)
2. Click "Pending" filter in left sidebar
3. Observe task grid updates

**Expected Results**:
- ✅ Only pending tasks (orange badge) are displayed
- ✅ Completed tasks disappear from view
- ✅ Filter switches in under 1 second (no loading spinner)
- ✅ "Pending" filter is highlighted/active in sidebar
- ✅ Task count updates if displayed

**Acceptance Criteria**:
- Filter is client-side (no API call, instant response)
- If no pending tasks: Empty state message "No pending tasks"
- Switching back to "All Tasks" shows all tasks again

---

### Scenario 3: Filter Tasks by Completed Status

**User Story**: View Tasks with Filtering (US1)

**Test Steps**:
1. User is on dashboard with mixed tasks
2. Click "Completed" filter in left sidebar
3. Observe task grid updates

**Expected Results**:
- ✅ Only completed tasks (green badge) are displayed
- ✅ Pending tasks disappear from view
- ✅ Filter switches in under 1 second
- ✅ "Completed" filter is highlighted/active in sidebar

**Acceptance Criteria**:
- If no completed tasks: Empty state message "No completed tasks"
- Completed tasks show checkboxes in checked state

---

### Scenario 4: Add New Task with Title and Description

**User Story**: Add New Task (US2)

**Test Steps**:
1. User is on dashboard
2. Click "+ Add Task" button in top navbar
3. Modal appears with form
4. Enter title: "Buy groceries"
5. Enter description: "Milk, eggs, bread, coffee"
6. Click "Create" or "Save" button

**Expected Results**:
- ✅ Modal opens immediately when button clicked
- ✅ Modal has title input field (focused automatically)
- ✅ Modal has description textarea (optional)
- ✅ Modal has "Cancel" and "Create" buttons
- ✅ After submission, modal closes
- ✅ New task appears at top of task list (newest first)
- ✅ Task has orange "Pending" badge
- ✅ Task shows entered title and description
- ✅ Total task creation time: under 10 seconds

**Acceptance Criteria**:
- Task is immediately visible (optimistic UI or fast API response)
- Task persists after page refresh
- Task is only visible to the user who created it

---

### Scenario 5: Add New Task with Title Only (No Description)

**User Story**: Add New Task (US2)

**Test Steps**:
1. Click "+ Add Task" button
2. Enter title: "Call dentist"
3. Leave description field empty
4. Click "Create" button

**Expected Results**:
- ✅ Task is created successfully
- ✅ Task appears in list with title only
- ✅ Description field shows as empty or null

**Acceptance Criteria**:
- Description is optional (no validation error)
- Task card handles missing description gracefully

---

### Scenario 6: Validation - Empty Title

**User Story**: Add New Task (US2)

**Test Steps**:
1. Click "+ Add Task" button
2. Leave title field empty
3. Click "Create" button

**Expected Results**:
- ✅ Error message appears: "Title is required"
- ✅ Modal remains open
- ✅ Task is NOT created
- ✅ Error message is user-friendly (not technical)

**Acceptance Criteria**:
- Frontend validation prevents submission
- Backend validation also enforces (if frontend bypassed)

---

### Scenario 7: Validation - Title Too Long

**User Story**: Add New Task (US2)

**Test Steps**:
1. Click "+ Add Task" button
2. Enter title with 201+ characters
3. Click "Create" button

**Expected Results**:
- ✅ Error message appears: "Title must be 200 characters or less"
- ✅ Modal remains open
- ✅ Task is NOT created

**Acceptance Criteria**:
- Character counter shows remaining characters (optional UX enhancement)
- Validation occurs on both frontend and backend

---

### Scenario 8: Toggle Task from Pending to Completed

**User Story**: Toggle Task Completion Status (US3)

**Test Steps**:
1. User is on dashboard with pending task (orange badge)
2. Click checkbox on task card
3. Observe immediate visual feedback

**Expected Results**:
- ✅ Checkbox becomes checked instantly (optimistic update)
- ✅ Badge color changes from orange to green
- ✅ Badge text changes from "Pending" to "Completed"
- ✅ If viewing "Pending" filter, task disappears from view
- ✅ If viewing "All Tasks" filter, task remains visible with updated status
- ✅ Toggle completes in under 100ms (instant feedback)

**Acceptance Criteria**:
- Change persists after page refresh
- If API call fails, UI rolls back to previous state with error message

---

### Scenario 9: Toggle Task from Completed to Pending

**User Story**: Toggle Task Completion Status (US3)

**Test Steps**:
1. User is on dashboard with completed task (green badge)
2. Click checkbox on task card
3. Observe immediate visual feedback

**Expected Results**:
- ✅ Checkbox becomes unchecked instantly
- ✅ Badge color changes from green to orange
- ✅ Badge text changes from "Completed" to "Pending"
- ✅ If viewing "Completed" filter, task disappears from view
- ✅ If viewing "All Tasks" filter, task remains visible with updated status

**Acceptance Criteria**:
- Toggle is idempotent (can toggle back and forth multiple times)
- Each toggle updates the database

---

### Scenario 10: Edit Existing Task

**User Story**: Update Existing Task (US4)

**Test Steps**:
1. User is on dashboard
2. Hover over a task card (desktop) or view task card (mobile)
3. Edit icon appears
4. Click edit icon
5. Modal appears pre-filled with current task data
6. Change title from "Buy groceries" to "Buy groceries today"
7. Change description from "Milk, eggs, bread" to "Milk, eggs, bread, coffee, bananas"
8. Click "Save" button

**Expected Results**:
- ✅ Edit icon visible on hover (desktop) or always visible (mobile)
- ✅ Modal opens with current task data pre-filled
- ✅ After saving, modal closes
- ✅ Task card updates immediately with new title and description
- ✅ Total edit time: under 15 seconds
- ✅ Status badge remains unchanged (editing doesn't affect completion status)

**Acceptance Criteria**:
- Changes persist after page refresh
- Validation rules same as creation (title required, length limits)

---

### Scenario 11: Edit Task - Validation Error

**User Story**: Update Existing Task (US4)

**Test Steps**:
1. Click edit icon on a task
2. Clear the title field (make it empty)
3. Click "Save" button

**Expected Results**:
- ✅ Error message appears: "Title is required"
- ✅ Modal remains open
- ✅ Task is NOT updated
- ✅ Original task data remains unchanged

**Acceptance Criteria**:
- Same validation rules as task creation

---

### Scenario 12: Delete Task with Confirmation

**User Story**: Delete Task (US5)

**Test Steps**:
1. User is on dashboard
2. Hover over a task card (desktop) or view task card (mobile)
3. Delete icon appears
4. Click delete icon
5. Confirmation dialog appears
6. Read confirmation message: "Are you sure you want to delete this task? This action cannot be undone."
7. Click "Delete" button

**Expected Results**:
- ✅ Delete icon visible on hover (desktop) or always visible (mobile)
- ✅ Confirmation dialog appears immediately
- ✅ Dialog has "Cancel" and "Delete" buttons
- ✅ After clicking "Delete", dialog closes
- ✅ Task disappears from task list immediately (optimistic removal)
- ✅ Total deletion time: under 5 seconds
- ✅ If user has no remaining tasks, empty state message appears

**Acceptance Criteria**:
- Deletion is permanent (task does not reappear after page refresh)
- Task is removed from database
- If API call fails, task reappears with error message

---

### Scenario 13: Cancel Task Deletion

**User Story**: Delete Task (US5)

**Test Steps**:
1. Click delete icon on a task
2. Confirmation dialog appears
3. Click "Cancel" button

**Expected Results**:
- ✅ Dialog closes
- ✅ Task remains in task list (not deleted)
- ✅ No API call made to backend

**Acceptance Criteria**:
- Cancel button prevents accidental deletion

---

### Scenario 14: Responsive Design - Mobile View

**User Story**: All user stories (responsive requirement)

**Test Steps**:
1. Open dashboard on mobile device or resize browser to mobile width (375px)
2. Observe layout and interactions

**Expected Results**:
- ✅ Task grid displays in single column
- ✅ Sidebar filters accessible (hamburger menu or bottom nav)
- ✅ "+ Add Task" button visible and accessible
- ✅ Edit and delete icons always visible (no hover state on mobile)
- ✅ Modals are full-screen or properly sized for mobile
- ✅ Touch targets meet minimum size (44x44px)
- ✅ Scrolling is smooth (60fps)

**Acceptance Criteria**:
- All CRUD operations work on mobile
- No horizontal scrolling
- Text remains readable

---

### Scenario 15: Performance - 1000+ Tasks

**User Story**: View Tasks with Filtering (US1)

**Test Steps**:
1. Create test user with 1000+ tasks (use seed script or API)
2. Log in and navigate to dashboard
3. Measure page load time
4. Scroll through task list
5. Switch between filters

**Expected Results**:
- ✅ Dashboard loads in under 2 seconds
- ✅ Scrolling is smooth (60fps, no jank)
- ✅ Filter switching is instant (<1 second)
- ✅ No browser freezing or unresponsiveness

**Acceptance Criteria**:
- Virtual scrolling implemented if needed
- Database queries optimized with indexes
- Frontend rendering optimized (memoization, virtualization)

---

### Scenario 16: Security - User Data Isolation

**User Story**: All user stories (security requirement)

**Test Steps**:
1. Create two test users: User A and User B
2. Log in as User A, create tasks
3. Log out, log in as User B
4. Navigate to dashboard
5. Attempt to access User A's tasks via API (if possible)

**Expected Results**:
- ✅ User B sees only their own tasks (not User A's tasks)
- ✅ Direct API calls to User A's task IDs return 403 Forbidden or 404 Not Found
- ✅ Zero data leakage between users

**Acceptance Criteria**:
- All database queries filter by user_id from JWT
- Backend enforces user ownership on all operations
- 100% data isolation (SC-007)

---

### Scenario 17: Error Handling - Network Failure

**User Story**: All user stories (error handling requirement)

**Test Steps**:
1. User is on dashboard
2. Disconnect network (airplane mode or DevTools offline)
3. Try to create a task
4. Try to toggle a task
5. Try to delete a task

**Expected Results**:
- ✅ User-friendly error message appears (not technical error)
- ✅ Message: "Network error. Please check your connection and try again."
- ✅ UI does not break or show blank screen
- ✅ Optimistic updates roll back if API call fails

**Acceptance Criteria**:
- Error messages are user-friendly
- UI remains functional after error
- User can retry operation after reconnecting

---

### Scenario 18: Error Handling - Task Not Found

**User Story**: Update/Delete Task (US4, US5)

**Test Steps**:
1. User opens edit modal for a task
2. In another browser tab, delete the same task
3. In first tab, try to save changes

**Expected Results**:
- ✅ Error message appears: "Task not found. It may have been deleted."
- ✅ Modal closes or shows error
- ✅ Task list refreshes to show current state

**Acceptance Criteria**:
- Concurrent edits handled gracefully
- User is informed of conflict

---

## Quick Validation Checklist

Use this checklist for rapid validation during development:

**View & Filter (US1)**:
- [ ] Dashboard loads in under 1 second
- [ ] All tasks displayed by default
- [ ] Pending filter shows only pending tasks
- [ ] Completed filter shows only completed tasks
- [ ] Empty state message when no tasks
- [ ] Responsive grid (1 col mobile, 2-3 cols desktop)

**Add Task (US2)**:
- [ ] "+ Add Task" button opens modal
- [ ] Title field is required
- [ ] Description field is optional
- [ ] Title max 200 characters
- [ ] Description max 1000 characters
- [ ] New task appears at top of list
- [ ] Task creation under 10 seconds

**Toggle Complete (US3)**:
- [ ] Checkbox toggles instantly (optimistic update)
- [ ] Badge color changes (orange ↔ green)
- [ ] Change persists after refresh
- [ ] Toggle under 100ms

**Edit Task (US4)**:
- [ ] Edit icon appears on hover (desktop)
- [ ] Modal pre-filled with current data
- [ ] Changes save and update immediately
- [ ] Validation same as creation
- [ ] Edit under 15 seconds

**Delete Task (US5)**:
- [ ] Delete icon appears on hover (desktop)
- [ ] Confirmation dialog prevents accidental deletion
- [ ] Task disappears immediately after confirmation
- [ ] Deletion is permanent
- [ ] Delete under 5 seconds

**Security & Performance**:
- [ ] User data isolation (100%)
- [ ] 1000+ tasks load in under 2 seconds
- [ ] 60fps scrolling on mobile
- [ ] Error handling for network failures
- [ ] JWT validation on all endpoints

---

## Troubleshooting

### Issue: Tasks not loading
**Solution**: Check JWT token validity, verify backend is running, check CORS configuration

### Issue: Optimistic updates not working
**Solution**: Verify TanStack Query configuration, check mutation onMutate callbacks

### Issue: Filter not switching
**Solution**: Check filter state management, verify useMemo dependencies

### Issue: Modal not opening
**Solution**: Check shadcn/ui Dialog component installation, verify state management

### Issue: Validation errors not showing
**Solution**: Check Pydantic models on backend, verify frontend validation logic

### Issue: Performance issues with many tasks
**Solution**: Implement virtual scrolling, check database indexes, profile with React DevTools

---

## Success Criteria Summary

Task CRUD is ready for production when:
- ✅ All 18 test scenarios pass
- ✅ Quick validation checklist complete
- ✅ Performance targets met (view <1s, create <10s, toggle <100ms)
- ✅ Security verified (100% data isolation)
- ✅ Error handling graceful (95% success rate)
- ✅ Responsive design works (mobile, tablet, desktop)
- ✅ Constitution compliance confirmed (5 core operations only)
