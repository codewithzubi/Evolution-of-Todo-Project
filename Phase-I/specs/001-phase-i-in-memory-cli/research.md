# Phase-I Research: In-Memory Todo CLI

**Phase**: I
**Date**: 2025-12-28
**Feature**: 001-phase-i-in-memory-cli

---

## Overview

This document consolidates research findings for Phase-I implementation. Research addresses CLI patterns, in-memory data structures, and UX clarity for a command-line todo application.

Research was conducted inline during planning. No external research agents were required due to well-defined technology stack (Python 3.13+ standard library) and straightforward domain (in-memory todo application).

---

## CLI Patterns Research

### Decision: Use Python `argparse` Module for Command-Line Parsing

**Rationale**:
- `argparse` is part of Python standard library (no external dependencies)
- Provides automatic help generation and argument validation
- Supports subcommands and optional arguments natively
- Industry-standard approach for CLI applications
- Reduces manual parsing and validation code

**Alternatives Considered**:
- Manual string parsing: Too error-prone, requires more validation code, no automatic help generation
- `sys.argv` direct access: Lower-level, more manual work for help and validation
- Third-party CLI libraries (`click`, `typer`): Violate constraint to use only standard library

**Conclusion**: Python `argparse` is optimal choice for Phase-I CLI implementation.

### Command Syntax Design

**Decision**: POSIX-style single-word commands with optional flags.

**Rationale**:
- POSIX style is industry standard for CLI applications
- Efficient for power users managing many tasks
- Supports future automation or scripting if needed
- Optional flags provide flexibility without cluttering primary commands
- Consistent with `argparse` capabilities

**Alternatives Considered**:
- Multi-word commands (e.g., "add task", "delete task"): More complex parsing, less consistent, harder to remember
- Verb-noun pairs (e.g., "create task"): More verbose, less efficient for repeated use
- Numbered menu system: Easier for beginners but inefficient for power users and repeated task management

**Conclusion**: POSIX-style single-word commands with optional flags provides best balance of efficiency, consistency, and user experience.

**Final Command Set**:
- `create <title> [-m|--message <description>]`: Create new task
- `view [--completed|--incomplete]`: View task list with optional filters
- `update <id> [--title <title>] [--description <description>]`: Update task details
- `delete <id>`: Delete task by ID
- `complete <id>`: Mark task as completed
- `incomplete <id>`: Mark task as incomplete
- `toggle <id>`: Toggle task completion status
- `help [command]`: Display help (all commands or specific command)

---

## In-Memory Data Structure Research

### Decision: Use Python Dictionary with ID-Based Keys for Task Storage

**Rationale**:
- Dictionary provides O(1) lookup by task ID
- Auto-incremented ID generation is trivial with integer counter
- Direct mapping matches task access pattern (most operations by ID)
- Minimal memory overhead, efficient for up to 1000 tasks
- Python dictionary is part of standard library, no external dependencies
- Direct access patterns align with requirements (update, delete, complete by ID)

**Alternatives Considered**:
- List-based storage: O(n) lookup for operations by ID, requires iteration to find tasks, simpler for view-all operations
- Class-based storage with internal list: Encapsulation but over-engineering for simple in-memory requirements
- Third-party data structures (e.g., `collections.defaultdict`): Violate constraint to use only standard library, unnecessary complexity

**Conclusion**: Dictionary with task ID as key, task object as value provides optimal performance for Phase-I requirements.

### ID Generation Strategy

**Decision**: Integer auto-incremented starting from 1, never reused after deletion.

**Rationale**:
- Integer IDs are most user-friendly for CLI (easy to remember and type)
- Auto-increment ensures simplicity and predictability
- No renumbering after deletion maintains stability and consistency with user expectations
- Efficient to generate and validate (simple integer counter)
- Aligns with requirements (FR-002: unique auto-incremented ID starting from 1)

**Alternatives Considered**:
- UUID-based unique identifiers: Guaranteed unique, no collision risk, but not user-friendly (hard to remember, difficult to type in CLI)
- Timestamp-based identifiers: Unique and chronological, but too complex for CLI context, not user-friendly
- String-based IDs: Flexible but require validation, not type-safe

**Conclusion**: Integer auto-incremented IDs starting from 1 with no reuse after deletion provides best user experience for CLI application.

---

## UX Clarity Research

### Decision: Use Consistent Command Syntax with Help on Invalid Input

**Rationale**:
- POSIX-style single-word commands are consistent and industry-standard
- Automatic help display on invalid commands reduces user errors
- Clear error messages with actionable guidance improve user experience
- Consistent syntax reduces learning curve for users
- Command flags (--title, --description, --completed, --incomplete) provide standard option patterns

**Alternatives Considered**:
- Multi-word commands with inconsistent naming: More complex parsing, less consistent, harder to learn
- Numbered menu-driven system: Easier for beginners but inefficient for repeated task management and power users
- Questionnaire-style interactive input: Not suitable for repeated task management, inefficient

**Conclusion**: POSIX-style commands with automatic help on invalid input provides optimal balance of discoverability and efficiency.

### Error Handling Philosophy

**Decision**: Clear, actionable error messages with command usage examples.

**Rationale**:
- CLI application must be accessible and user-friendly
- Clear messages help users correct mistakes quickly without referencing documentation
- Command usage examples reduce learning curve
- Actionable guidance (what to do next) improves user experience
- Aligns with success criteria (SC-008: 100% first-attempt success, SC-009: clear error messages)

**Alternatives Considered**:
- Minimal error messages with error codes: Concise but less helpful for novice users
- Stack traces and detailed technical errors: Technical but intimidating and unnecessary for CLI application
- Silent failures with no messages: Confusing, users unsure what went wrong

**Conclusion**: Clear, actionable error messages with command usage examples provides best user experience.

### Output Formatting

**Decision**: Structured format with status indicator, ID, title, and description.

**Rationale**:
- Structured format with clear status indicators meets requirement for visibility (SC-010)
- Separate lines for description improve readability for longer descriptions
- Meets success criteria for quick scanning
- Consistent format allows users to quickly parse task list

**Alternatives Considered**:
- Compact single-line format: More efficient for many tasks but less readable, harder to scan
- Table-based display with columns: Aligned columns but requires fixed width, harder for long descriptions, requires complex formatting code
- JSON-like structured output: Machine-readable but not user-friendly for CLI

**Conclusion**: Structured format with status indicator, ID, title, description (on separate line) provides optimal balance of readability and information density.

**Final Format Template**:
```
[<id>] <status> <title>
    <description>
```

Where:
- `<id>` is numeric task identifier
- `<status>` is `[COMPLETED]` or `[INCOMPLETE]`
- `<title>` is task title
- `<description>` is task description, displayed on separate line indented by 4 spaces (omitted if empty)

---

## Technology Stack Summary

| Component | Technology | Justification |
|-----------|------------|--------------|
| Command-Line Parsing | Python `argparse` | Standard library, automatic help, argument validation |
| Data Storage | Python `dict` | O(1) lookup, efficient for ID-based access |
| Type Hints | Python `typing` module | Improve code clarity, enable better IDE support |
| Output Formatting | Python f-strings or format() | Standard string formatting, readability |
| Input/Output | Python `sys` module | Standard library, stdin/stdout access |

All components use Python standard library only. No external dependencies required. This meets Phase-I constraint of minimal complexity and no external dependencies.

---

## Performance Considerations

### Expected Task Volume

- Target: Up to 1000 tasks per session (from specification SC-007)
- Dictionary-based storage: O(1) lookups for all operations by ID
- View all operations: O(n) iteration over dictionary values
- Performance expectation: All operations complete under 5 seconds (from specification SC-001, SC-003, SC-004, SC-005)

### Memory Efficiency

- Python dictionary overhead: Minimal for up to 1000 small objects
- Task object size: Estimated under 200 bytes per task (id, title, description, completed)
- Total memory for 1000 tasks: Under 200 KB (negligible for modern systems)
- No memory growth concerns for Phase-I scope

---

## Future Evolution Considerations

### Phase-II: File Persistence

Research findings support smooth transition:
- Dictionary-based storage can be serialized to JSON or other formats
- Task data model abstract design allows extraction to separate file storage layer
- Service layer interface separates business logic from storage implementation

### Phase-III: REST API

Research findings support service layer extraction:
- Service layer (business logic) can be reused for API endpoints
- Command interface becomes one presentation layer among potentially multiple (CLI, API)
- Data model remains consistent across all presentation layers

### Phase-IV: Event-Driven

Research findings support event sourcing:
- Stateless execution principle established (in-memory state managed explicitly)
- Clear service interfaces enable event publication hooks
- Data model serialization supports event payload generation

---

## Conclusion

Research findings provide clear direction for Phase-I implementation:

1. **CLI Implementation**: Use Python `argparse` with POSIX-style commands
2. **Data Storage**: Use Python dictionary with ID-based keys
3. **ID Generation**: Integer auto-incremented starting from 1, no reuse after deletion
4. **UX Design**: Consistent command syntax, automatic help on invalid input
5. **Error Handling**: Clear, actionable messages with command usage examples
6. **Output Formatting**: Structured format with status indicators
7. **Technology Stack**: Python standard library only, no external dependencies

All decisions align with Phase-I constraints (in-memory, CLI only, Python 3.13+) and support evolution to Phases II-V.
