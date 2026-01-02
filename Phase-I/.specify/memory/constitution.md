# Constitution for The Evolution of Todo - Phase I

## Core Principles

### Spec-Driven Development
Every feature starts with a detailed spec in Markdown, refined until Claude Code generates correct code. No manual coding allowed. This ensures that all implementation is driven by clear, testable specifications before any code is written.

### Reusable Intelligence
Design components (like task models) to be modular for future AI agent reuse. Code should be structured in a way that allows components to be easily extracted and reused in future phases or by other AI agents.

### Clean Code and Structure
Follow PEP8, proper Python project structure with /src folder. All code must adhere to Python best practices and maintainability standards to ensure long-term project health.

### User Experience
The app must be intuitive, colorful, and professional. The interface should provide a pleasant user experience with clear navigation and visual feedback.

## Technology Stack

- Python 3.13+
- UV for package management
- Libraries: Use 'rich' for colorful console output and tables, 'datetime' for dates, and any built-in modules as needed. No external databases; all in-memory.
- Claude Code and Spec-Kit Plus for generation.

## High-Level Architecture

### In-Memory Storage
Tasks stored in a list or dict in memory. No persistence between runs is required for this phase.

### CLI Interface
On launch, display a large, colorful welcome message: "Welcome to The Evolution of Todo" using rich library for styling (bold, colors, centered if possible).

### Menu-Driven Interface
After welcome, show a numbered menu of options covering all features from Basic, Intermediate, and Advanced levels. User inputs a number to select (e.g., 1: Add Task, 2: Delete Task, etc.). Include an option to exit (e.g., 0: Exit).

### Error Handling
Graceful handling for invalid inputs. The application must not crash on invalid user input and should provide helpful error messages.

### Task Model
Each task has fields like ID, title, description, status (complete/incomplete), priority (high/medium/low), tags/categories (list), due date (datetime), recurring (bool with frequency like 'daily', 'weekly').

## Feature Specifications Overview

### Basic Level
- Add Task: Prompt for title, description; auto-assign ID.
- Delete Task: By ID.
- Update Task: By ID, edit any field.
- View Task List: Display all tasks in a professional table format using rich.Table (columns: ID, Title, Description, Status, Priority, Tags, Due Date, Recurring).
- Mark as Complete: Toggle by ID.

### Intermediate Level
- Priorities & Tags/Categories: Assign/edit priorities and multiple tags.
- Search & Filter: Search by keyword; filter by status, priority, date, tags.
- Sort Tasks: By due date, priority, alphabetically.

### Advanced Level
- Recurring Tasks: Set recurring (e.g., daily/weekly); app should simulate auto-rescheduling on view/update.
- Due Dates & Time Reminders: Set due date; on view, highlight overdue tasks in red.

All features accessible via the main menu. For view, always use a beautiful, colorful table with borders, alignments, and colors for status (e.g., green for complete).

## Development Rules

- Generate code only via Claude Code from specs.
- GitHub Repo Structure: /specs (for all spec files), /src (Python code), README.md (setup), CLAUDE.md (Claude instructions).
- Testing: Include basic unit tests in specs.
- Constraints: In-memory only; no persistence between runs.

## Success Criteria

The app runs via console, shows welcome, menu, handles all features professionally, and demonstrates spec-driven process in repo. The implementation must satisfy all feature specifications outlined above and follow the architectural principles defined in this constitution.

## Governance

This constitution serves as the foundational document outlining the project's principles, architecture, rules, and high-level specs. It follows Spec-Driven Development principles: No manual code writing; all implementation will come from refining specs and using Claude Code to generate code. All changes to this constitution require explicit approval and proper versioning.

**Version**: 1.0.0 | **Ratified**: 2025-12-30 | **Last Amended**: 2025-12-30

