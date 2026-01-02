# Command Interface Contract

**Phase**: I
**Branch**: `001-phase-i-in-memory-cli`
**Date**: 2025-12-28

---

## Overview

This contract defines the command-line interface for Phase-I in-memory todo application. It specifies all available commands, their syntax, inputs, outputs, and validation rules.

---

## Command Syntax

### Conventions

- Commands are single POSIX-style words (lowercase)
- Optional arguments use flags with `--` prefix
- Short flags with `-` prefix supported where applicable
- Positional arguments required where applicable
- Help is available for all commands

### General Format

```
<command> [positional-args] [options]
```

---

## Commands

### create

**Purpose**: Create a new task

**Syntax**:
```
create <title> [-m|--message <description>]
```

**Arguments**:
- `<title>` (required, positional): Task title
- `-m` or `--message` `<description>` (optional): Task description

**Validation**:
- Title must not be empty
- Title must not be whitespace-only
- Title and description can contain any Unicode characters

**Output** (Success):
```
Task created with ID <id>
```

**Output** (Error):
- Title not provided: `Error: Title is required. Usage: create <title> [-m <description>]`
- Title is empty: `Error: Title cannot be empty. Usage: create <title> [-m <description>]`
- Title is whitespace: `Error: Title cannot be whitespace. Usage: create <title> [-m <description>]`

**Examples**:
```
create Buy groceries
create "Buy groceries" -m "Milk, eggs, bread"
create Call Mom --message "Wish her happy birthday"
```

---

### view

**Purpose**: View task list

**Syntax**:
```
view [--completed|--incomplete]
```

**Arguments**:
- `--completed` (optional flag): Show only completed tasks
- `--incomplete` (optional flag): Show only incomplete tasks
- Default (no flag): Show all tasks

**Validation**:
- No validation required (flags are optional)

**Output** (Success, Tasks Found):

```
[1] [COMPLETED] Buy groceries
    Milk, eggs, bread
[2] [INCOMPLETE] Call Mom
    Wish her happy birthday
[3] [INCOMPLETE] Walk dog
    Morning walk around the park
```

**Output** (Success, No Tasks):

```
No tasks found. Create your first task with 'create <title>'.
```

**Output** (Success, Filtered No Match):

```
No tasks match specified criteria.
```

**Examples**:
```
view
view --completed
view --incomplete
```

---

### update

**Purpose**: Update task details

**Syntax**:
```
update <id> [--title <title>] [--description <description>]
```

**Arguments**:
- `<id>` (required, positional): Task ID to update
- `--title` `<title>` (optional): New task title
- `--description` `<description>` (optional): New task description

**Validation**:
- Task ID must exist
- Task ID must be positive integer
- At least one of `--title` or `--description` must be provided
- If `--title` provided: must not be empty or whitespace-only

**Output** (Success):
```
Task <id> updated.
```

**Output** (Error):
- Task ID not found: `Error: Task with ID <id> not found.`
- No fields provided: `Error: At least title or description must be provided. Usage: update <id> [--title <title>] [--description <description>]`
- Title is empty: `Error: Title cannot be empty. Usage: update <id> --title <title>`
- Title is whitespace: `Error: Title cannot be whitespace. Usage: update <id> --title <title>`

**Examples**:
```
update 2 --title "Buy snacks"
update 2 --description "Chips and soda"
update 2 --title "Buy groceries and snacks" --description "Milk, eggs, chips, soda"
```

---

### delete

**Purpose**: Delete a task

**Syntax**:
```
delete <id>
```

**Arguments**:
- `<id>` (required, positional): Task ID to delete

**Validation**:
- Task ID must exist
- Task ID must be positive integer

**Output** (Success):
```
Task <id> deleted.
```

**Output** (Error):
- Task ID not found: `Error: Task with ID <id> not found.`

**Examples**:
```
delete 3
delete 5
```

---

### complete

**Purpose**: Mark a task as completed

**Syntax**:
```
complete <id>
```

**Arguments**:
- `<id>` (required, positional): Task ID to mark complete

**Validation**:
- Task ID must exist
- Task ID must be positive integer

**Output** (Success):
```
Task <id> marked as completed.
```

**Output** (Error):
- Task ID not found: `Error: Task with ID <id> not found.`

**Examples**:
```
complete 1
complete 2
```

---

### incomplete

**Purpose**: Mark a task as incomplete

**Syntax**:
```
incomplete <id>
```

**Arguments**:
- `<id>` (required, positional): Task ID to mark incomplete

**Validation**:
- Task ID must exist
- Task ID must be positive integer

**Output** (Success):
```
Task <id> marked as incomplete.
```

**Output** (Error):
- Task ID not found: `Error: Task with ID <id> not found.`

**Examples**:
```
incomplete 1
incomplete 3
```

---

### toggle

**Purpose**: Toggle task completion status

**Syntax**:
```
toggle <id>
```

**Arguments**:
- `<id>` (required, positional): Task ID to toggle

**Validation**:
- Task ID must exist
- Task ID must be positive integer

**Output** (Success):
```
Task <id> toggled to <new-status>.
```

**Output** (Error):
- Task ID not found: `Error: Task with ID <id> not found.`

**Examples**:
```
toggle 2
toggle 5
```

---

### help

**Purpose**: Display command help

**Syntax** (General Help):
```
help
```

**Syntax** (Command-Specific Help):
```
help <command>
```

**Arguments**:
- `<command>` (optional): Specific command to display help for

**Validation**:
- If `<command>` provided: must be valid command name

**Output** (General Help):

```
Available commands:
  create <title> [-m <description>]  Create a new task
  view [--completed|--incomplete]       View task list
  update <id> [--title <title>] [--description <description>]  Update task details
  delete <id>                        Delete a task
  complete <id>                      Mark task as completed
  incomplete <id>                    Mark task as incomplete
  toggle <id>                        Toggle task completion status
  help [command]                      Display this help or command-specific help

Usage: <command> [arguments]
Type 'help <command>' for detailed information about a specific command.
```

**Output** (Command-Specific Help):

```
Command: create
Description: Create a new task
Usage: create <title> [-m|--message <description>]

Arguments:
  <title>       Task title (required)
  -m, --message  Task description (optional)

Examples:
  create Buy groceries
  create "Buy groceries" -m "Milk, eggs, bread"
```

**Output** (Error):
- Invalid command name: `Error: Invalid command '<command>'. Type 'help' to see available commands.`

**Examples**:
```
help
help create
help view
```

---

## Error Messages

### Error Taxonomy

| Error Type | Example Message | Context |
|-------------|-----------------|---------|
| Required Field | `Error: Title is required. Usage: create <title> [-m <description>]` | Missing required argument |
| Invalid Value | `Error: Title cannot be empty.` | Invalid field value |
| Not Found | `Error: Task with ID <id> not found.` | ID does not exist |
| Invalid Command | `Error: Invalid command '<command>'. Type 'help' to see available commands.` | Unknown command |

### Error Message Format

All error messages follow format:

```
Error: <description>
Usage: <command-syntax>
```

or

```
Error: <description>
```

---

## Task Display Format

### Format Template

```
[<id>] <status> <title>
    <description>
```

### Format Rules

- `<id>`: Task ID as integer
- `<status>`: `[COMPLETED]` or `[INCOMPLETE]` (brackets and uppercase)
- `<title>`: Task title
- `<description>`: Task description, omitted if empty
- Description line indented by 4 spaces
- Exactly one blank line between tasks

### Examples

#### Task with Description

```
[1] [INCOMPLETE] Buy groceries
    Milk, eggs, bread
```

#### Task without Description

```
[2] [COMPLETED] Call Mom
```

---

## Exit Behavior

### Exit Commands

No explicit exit command. Application exits on:
- End-of-input (EOF)
- Keyboard interrupt (Ctrl+C)

### Exit Message

```
Goodbye!
```

---

## Constraints

### Input Constraints

- All input is via stdin
- Commands are case-sensitive (lowercase)
- Quotes handle multi-word arguments
- Whitespace in arguments is preserved within quotes

### Output Constraints

- All output to stdout
- Error messages to stderr (implementation decision)
- Output language: English only

---

## Performance Expectations

- Command parsing: Under 100ms
- Task operations (create, update, delete, complete, toggle): Under 5 seconds
- View operations (all tasks): Under 1 second for up to 1000 tasks
- Help display: Under 200ms

---

## Future Evolution Considerations

### Phase-II: File Persistence

Command interface remains unchanged:
- All command syntax identical
- Output format identical
- Error messages identical
- Only underlying storage implementation changes

### Phase-III: REST API

Command interface becomes alternative presentation layer:
- Commands may expose as API endpoints
- Input/output format adapts to JSON for API
- Validation rules identical

---

## Compliance

### Specification Alignment

- FR-019 to FR-029: All 8 commands specified with correct syntax
- SC-011: Help command allows learning all commands in under 10 seconds

### Constitutional Alignment

- CLI command structure reusable across phases
- Error messages clear and actionable
- Command patterns follow consistent conventions
