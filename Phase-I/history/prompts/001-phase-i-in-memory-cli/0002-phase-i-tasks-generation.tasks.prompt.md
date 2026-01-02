---
id: 0002
title: Phase-I tasks generation
stage: tasks
date: 2025-12-28
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-phase-i-in-memory-cli
branch: 001-phase-i-in-memory-cli
user: N/A
command: /sp.tasks
labels: [phase-i, tasks, implementation]
links:
  spec: specs/001-phase-i-in-memory-cli/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase-i-in-memory-cli/tasks.md
tests:
  - Task organization and dependency validation (no implementation tests)
---

## Prompt

/sp.tasks

You are an expert Software Architect and Spec-Driven Development planner.

I am working on **Hackathon-II: Spec-Driven Development – Evolution of Todo**.
This request is strictly for **Phase-I: Todo In-Memory Python Console App**.

Your task is to convert the approved **Phase-I plan and specifications**
into a clear, ordered list of **Spec-Kit Plus tasks**.

DO NOT write code.
ONLY produce tasks file.

---

## Phase-I CONTEXT

Phase-I Goal:
Build a **command-line Todo application** that:
- Stores tasks in memory
- Uses Python 3.13+
- Implements 5 basic features:
  Add, Delete, Update, View, Mark Complete
- Is fully Spec-Driven and implemented later via Claude Code

Manual coding is forbidden.

---

## PREREQUISITES

First, run the prerequisites check:
```bash
.specify/scripts/bash/check-prerequisites.sh --json
```

You must have the following documents available:
- plan.md (from /sp.plan)
- spec.md (from /sp.specify)
- data-model.md (data model definition)
- contracts/task-contract.md and contracts/command-contract.md (interface contracts)
- research.md (research findings)
- quickstart.md (user guide)

Read all of these documents before generating tasks.

---

## REQUIRED TASK OUTPUT

Your output MUST be a file at:

```
specs/001-phase-i-in-memory-cli/tasks.md
```

Use the tasks template at `.specify/templates/tasks-template.md` for
formatting reference.

---

## TASK ORGANIZATION

Organize tasks by **dependency order** and group by **user story priority**:

### Phase 1: Setup
Shared infrastructure and project scaffolding (blocking all other phases)

### Phase 2: Foundational
Blocking prerequisites for all user stories (Task entity, storage, validation)

### Phase 3-7: User Stories (One phase per story)
- US1 (P1): Create and View Tasks - MVP candidate
- US2 (P1): Mark Tasks as Complete
- US3 (P2): Update Task Details
- US4 (P2): Delete Tasks
- US5 (P2): View Filtered Task Lists

### Phase 8: Polish & Cross-Cutting
Error handling, edge cases, validation, acceptance

---

## TASK FORMAT

Each task MUST follow this format:

```
- [ ] [TaskID] [P?] [Story?] Description with file path
```

Where:
- `[ ]` - Checkbox (unchecked)
- `TaskID` - Sequential: T001, T002, T003, ...
- `[P]` - Parallel marker (optional, indicates task can run in parallel with others in same phase)
- `[Story?]` - Story label for user story phases: [US1], [US2], [US3], [US4], [US5]
- `Description` - Clear, actionable task description
- `file path` - Exact file path (from architecture.md or research.md)

Example:
```
- [ ] [T001] Create Task data model file with Task class
  - Path: src/models/task.py
  - Completion: Task class defined with id, title, description, completed fields
```

---

## TASK CONTENT REQUIREMENTS

### Setup Tasks (Phase 1)
- Project directory structure creation
- Core file scaffolding (main.py, models, storage, services, cli, utils)

### Foundational Tasks (Phase 2)
- Task entity definition
- In-memory storage implementation
- Validation utilities
- Task service layer (business logic)
- Command parser (argparse)
- Command handlers (stubs)
- Output formatter

### User Story Tasks (Phases 3-7)
For each user story, include tasks for:
- CLI command handler implementation
- Service layer business logic
- Storage layer data operations
- Wiring commands to parser and main loop

### Polish & Cross-Cutting Tasks (Phase 8)
- Comprehensive error handling
- Edge case handling
- Help command
- Exit handling
- Compliance validation

---

## TASK DEPENDENCIES

Identify and document:
1. **Critical path**: Tasks that must execute sequentially
2. **Parallel execution groups**: Tasks that can run simultaneously

---

## COMPLETION CHECKLIST

Include a checklist to verify Phase-I implementation is complete when all tasks are done.

---

## ACCEPTANCE CRITERIA MAPPING

Map tasks to user stories and their acceptance criteria from spec.md.

---

## COMPLIANCE

### Specification Alignment

- FR-001 to FR-029: All functional requirements covered by tasks
- SC-001 to SC-011: All success criteria validated through tasks

### Constitutional Alignment

- Manual coding forbidden: All tasks designed for Claude Code implementation
- Spec-driven development: All tasks derived from specifications and contracts
- AI-native engineering: Tasks leverage Python standard library, no external dependencies
- Phase sequential completion: All tasks strictly Phase-I scope, no future-phase leakage

---

## FINAL OUTPUT

Return ONLY the complete **Phase-I `/sp.tasks` output**.
No explanations. No summaries. No extra commentary.

---

## Response snapshot

Successfully generated Phase-I tasks.md file with 42 dependency-ordered implementation tasks:

**Phase 1: Setup** (4 tasks)
- T001: Create project directory structure under /src
- T002: Create Task data model file
- T003: Create in-memory storage module
- T004: Create main application entry point

**Phase 2: Foundational** (5 tasks)
- T005: Implement task validation utilities
- T006: Implement task service layer
- T007: Implement argparse-based command parser
- T008: Create command handlers module
- T009: Create output formatter module

**Phase 3: User Story 1 - Create and View Tasks (P1)** (6 tasks)
- T010-T015: Implement create and view commands, service methods, storage operations

**Phase 4: User Story 2 - Mark Tasks as Complete (P1)** (6 tasks)
- T016-T021: Implement complete, incomplete commands, service methods, storage update

**Phase 5: User Story 3 - Update Task Details (P2)** (4 tasks)
- T022-T025: Implement update command, service method, parser wiring, validation

**Phase 6: User Story 4 - Delete Tasks (P2)** (4 tasks)
- T026-T029: Implement delete command, service method, storage deletion

**Phase 7: User Story 5 - View Filtered Task Lists (P2)** (5 tasks)
- T030-T034: Implement toggle command, filtered view, service methods, parser wiring

**Phase 8: Polish & Cross-Cutting** (8 tasks)
- T035-T042: Error handling, help command, edge cases, exit handling, compliance

**Task Organization**:
- 42 total tasks organized by dependency order
- Parallel execution groups identified for optimization
- Critical path defined: T001 → T002 → T005 → T006 → T007 → T008 → T009 → T015 → T021 → T025 → T029 → T034 → T042
- Each task includes completion criteria and exact file path

**Compliance Validation**:
- All 29 functional requirements (FR-001 to FR-029) covered by tasks
- All 11 success criteria (SC-001 to SC-011) validated in Phase 8 tasks
- Constitution alignment verified: manual coding forbidden, spec-driven, AI-native, phase sequential completion

---

## Outcome

- Impact: Complete Phase-I tasks.md generated with 42 dependency-ordered implementation tasks covering all user stories, acceptance criteria, and compliance requirements. Tasks organized by user story priority (P1 first, then P2) with clear parallel execution groups and critical path identification.
- Tests: Task organization and dependency validation (no implementation tests)
- Files: Created 1 file:
  - specs/001-phase-i-in-memory-cli/tasks.md (350+ lines with 42 tasks, 8 phases, dependencies, completion checklist)
- Next prompts: Execute `/sp.implement` to begin implementation via Claude Code, or run `/sp.analyze` for cross-artifact consistency analysis
- Reflection: Tasks generation completed successfully. All tasks derive from approved specifications and contracts. Task organization respects user story priorities (US1, US2 as P1; US3, US4, US5 as P2). Critical path identified for sequential execution with parallel groups identified for optimization. Constitution compliance validated: all tasks designed for Claude Code implementation with no manual coding, strict Phase-I scope, and no future-phase leakage.

---

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All FR and SC requirements mapped to tasks, constitution compliance verified
- Prompt variant (if applicable): initial
- Next experiment (smallest change to try): None required - tasks are complete and ready for implementation phase
