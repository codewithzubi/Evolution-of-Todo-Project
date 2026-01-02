# Quickstart Guide: Phase-I In-Memory Todo CLI

**Phase**: I
**Branch**: `001-phase-i-in-memory-cli`
**Date**: 2025-12-28

---

## Overview

This guide provides quickstart instructions for Phase-I in-memory todo command-line application. The application allows users to create, view, update, delete, and manage task completion status through a simple CLI interface.

---

## Prerequisites

- Python 3.13+ installed
- Terminal or command prompt access
- Basic familiarity with command-line interfaces

---

## Getting Started

### Launch Application

Run the application from terminal:

```bash
python src/main.py
```

The application will display a welcome message and enter command loop.

### Exit Application

Press `Ctrl+C` or send end-of-file signal to exit.

---

## Commands

### Create Task

Create a new task with optional description:

```bash
create Buy groceries
create Buy groceries -m "Milk, eggs, bread"
create "Buy groceries" --message "Milk, eggs, bread"
```

**Rules**:
- Title is required
- Description is optional
- Title cannot be empty or whitespace-only

### View Tasks

View all tasks or filter by completion status:

```bash
view
view --completed
view --incomplete
```

**Output Format**:
```
[1] [INCOMPLETE] Buy groceries
    Milk, eggs, bread
[2] [COMPLETED] Call Mom
```

### Update Task

Update task title or description:

```bash
update 2 --title "Buy snacks"
update 2 --description "Chips and soda"
update 2 --title "Buy groceries and snacks" --description "Milk, eggs, chips, soda"
```

**Rules**:
- Task ID must exist
- At least one of title or description must be provided
- Title cannot be empty if provided

### Delete Task

Delete a task by its ID:

```bash
delete 3
```

**Rules**:
- Task ID must exist
- Task IDs are never reused after deletion

### Mark Task as Complete

Mark a task as completed:

```bash
complete 1
```

**Rules**:
- Task ID must exist

### Mark Task as Incomplete

Mark a task as incomplete:

```bash
incomplete 1
```

**Rules**:
- Task ID must exist

### Toggle Task Status

Toggle task completion between complete and incomplete:

```bash
toggle 1
```

**Rules**:
- Task ID must exist
- Flips current status (incomplete becomes complete, complete becomes incomplete)

### Get Help

Display all commands or help for specific command:

```bash
help
help create
help view
```

---

## Common Workflows

### Basic Task Management

```bash
# Create tasks
create Buy groceries -m "Milk, eggs, bread"
create Call Mom --message "Wish her happy birthday"
create Walk dog -m "Morning walk around park"

# View all tasks
view

# Mark task as complete
complete 1

# View remaining incomplete tasks
view --incomplete

# Update a task
update 3 --title "Walk dog in evening"

# Delete completed task
delete 1
```

### Focused Productivity

```bash
# Create multiple tasks
create Finish project report
create Prepare presentation slides
create Send weekly update email
create Schedule team meeting

# View incomplete tasks only
view --incomplete

# Complete tasks one by one
complete 1
complete 2
complete 3
complete 4

# View all completed tasks
view --completed

# Clean up completed tasks
delete 1
delete 2
delete 3
delete 4
```

---

## Task Entity

Each task contains:

- **id**: Unique integer identifier (auto-generated)
- **title**: Task title (required, non-empty)
- **description**: Additional details (optional)
- **completed**: Status (true or false)

---

## Error Handling

Common errors and their solutions:

| Error | Cause | Solution |
|--------|--------|----------|
| Title is required | create command without title | Provide title: `create Buy groceries` |
| Title cannot be empty | Empty or whitespace title | Provide valid title: `create Buy groceries` |
| Task with ID X not found | Invalid or deleted task ID | Check task list: `view` |
| At least title or description must be provided | update command with no fields | Provide field to update: `update 2 --title New Title` |

---

## Notes

- **In-Memory Storage**: All tasks are stored in memory only. Tasks are lost when application exits.
- **Task IDs**: IDs are auto-incremented integers starting from 1. IDs are never reused after deletion.
- **Single Session**: Application runs for one session only. No persistence to files or database.
- **Case Sensitivity**: Commands are case-sensitive. Use lower case (create, not Create).
- **Quotes**: Use quotes for multi-word arguments: `create "Buy groceries and snacks" -m "Milk, eggs, chips"`

---

## Examples

### Example 1: Single Task Workflow

```bash
# Launch application
python src/main.py

# Create a task
create Buy groceries -m "Milk, eggs, bread"
# Output: Task created with ID 1

# View tasks
view
# Output:
# [1] [INCOMPLETE] Buy groceries
#     Milk, eggs, bread

# Mark as complete
complete 1
# Output: Task 1 marked as completed.

# View tasks again
view
# Output:
# [1] [COMPLETED] Buy groceries
#     Milk, eggs, bread
```

### Example 2: Multiple Tasks Workflow

```bash
# Create multiple tasks
create Buy groceries -m "Milk, eggs, bread"
create Call Mom --message "Wish her happy birthday"
create Walk dog -m "Morning walk around park"
create Finish project report

# View incomplete tasks
view --incomplete
# Output:
# [1] [INCOMPLETE] Buy groceries
#     Milk, eggs, bread
# [2] [INCOMPLETE] Call Mom
#     Wish her happy birthday
# [3] [INCOMPLETE] Walk dog
#     Morning walk around park
# [4] [INCOMPLETE] Finish project report

# Complete some tasks
complete 2
complete 3

# View completed tasks
view --completed
# Output:
# [2] [COMPLETED] Call Mom
#     Wish her happy birthday
# [3] [COMPLETED] Walk dog
#     Morning walk around park

# Delete completed task
delete 2

# View all tasks
view
# Output:
# [1] [INCOMPLETE] Buy groceries
#     Milk, eggs, bread
# [3] [COMPLETED] Walk dog
#     Morning walk around park
# [4] [INCOMPLETE] Finish project report
```

---

## Troubleshooting

### Command Not Recognized

If you see "Invalid command" error:
- Check command spelling (case-sensitive)
- Type `help` to see all available commands
- Verify you are not mixing flags and positional arguments

### Task ID Not Found

If you see "Task with ID X not found" error:
- Run `view` to see all current tasks and their IDs
- Verify you are using the correct task ID
- Remember that task IDs are never reused after deletion

### Issues with Multi-Word Arguments

If arguments are not parsing correctly:
- Use quotes around multi-word values: `create "Buy groceries and snacks"`
- Use quotes around descriptions with spaces: `-m "Milk, eggs, bread"`

---

## Next Steps

After mastering basic operations:
- Explore filtering with `view --completed` and `view --incomplete`
- Use `toggle` for quick status changes
- Try the `help` command for detailed command information

For more detailed information, see:
- [spec.md](./spec.md) - Complete feature specification
- [plan.md](./plan.md) - Implementation plan and architecture
- [research.md](./research.md) - Research findings and decisions
