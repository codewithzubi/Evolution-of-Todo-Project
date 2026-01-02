"""Command handlers for CLI operations."""

import argparse
from typing import TYPE_CHECKING

from models.task import Task
from services.task_service import TaskService
from storage.in_memory_store import InMemoryTaskStore
from utils.validators import ValidationError
from cli.formatter import format_task, format_task_list

if TYPE_CHECKING:
    from argparse import Namespace


# Initialize store and service (single instance for entire session)
_store = InMemoryTaskStore()
_service = TaskService(_store)


def create_cmd(args: "Namespace") -> None:
    """Handle create command."""
    try:
        description = getattr(args, "description", "")
        title = getattr(args, "title", None)
        if title is None:
            print("Error: Title is required. Usage: create <title> [-m <description>]")
            return
        task = _service.create_task(title, description)
        print(f"Task created with ID {task.id}")
    except ValidationError as e:
        print(f"Error: {e.message}. Usage: create <title> [-m <description>]")


def view_cmd(args: "Namespace") -> None:
    """Handle view command."""
    try:
        if hasattr(args, "completed") and args.completed:
            tasks = _service.get_tasks_by_status(completed=True)
        elif hasattr(args, "incomplete") and args.incomplete:
            tasks = _service.get_tasks_by_status(completed=False)
        else:
            tasks = _service.get_all_tasks()

        if not tasks:
            if hasattr(args, "completed") and args.completed or hasattr(args, "incomplete") and args.incomplete:
                print("No tasks match specified criteria.")
            else:
                print("No tasks found. Create your first task with 'create <title>'.")
        else:
            print(format_task_list(tasks))
    except ValidationError as e:
        print(f"Error: {e.message}")


def update_cmd(args: "Namespace") -> None:
    """Handle update command."""
    try:
        task = _service.update_task(args.id, args.title, args.description)
        print(f"Task {task.id} updated.")
    except ValidationError as e:
        if "not found" in e.message:
            print(f"Error: {e.message}.")
        else:
            print(f"Error: {e.message}. Usage: update <id> [--title <title>] [--description <description>]")


def delete_cmd(args: "Namespace") -> None:
    """Handle delete command."""
    try:
        task = _service.delete_task(args.id)
        print(f"Task {task.id} deleted.")
    except ValidationError as e:
        print(f"Error: {e.message}.")


def complete_cmd(args: "Namespace") -> None:
    """Handle complete command."""
    try:
        task = _service.mark_complete(args.id)
        print(f"Task {task.id} marked as completed.")
    except ValidationError as e:
        print(f"Error: {e.message}.")


def incomplete_cmd(args: "Namespace") -> None:
    """Handle incomplete command."""
    try:
        task = _service.mark_incomplete(args.id)
        print(f"Task {task.id} marked as incomplete.")
    except ValidationError as e:
        print(f"Error: {e.message}.")


def toggle_cmd(args: "Namespace") -> None:
    """Handle toggle command."""
    try:
        task = _service.toggle_task(args.id)
        status = "COMPLETED" if task.completed else "INCOMPLETE"
        print(f"Task {task.id} toggled to {status}.")
    except ValidationError as e:
        print(f"Error: {e.message}.")


def help_cmd(args: "Namespace") -> None:
    """Handle help command."""
    if hasattr(args, "command") and args.command:
        # Command-specific help
        _show_command_help(args.command)
    else:
        # General help
        _show_general_help()


def _show_general_help() -> None:
    """Display general help message."""
    print("""Available commands:
  create <title> [-m <description>]  Create a new task
  view [--completed|--incomplete]       View task list
  update <id> [--title <title>] [--description <description>]  Update task details
  delete <id>                        Delete a task
  complete <id>                      Mark task as completed
  incomplete <id>                    Mark task as incomplete
  toggle <id>                        Toggle task completion status
  help [command]                      Display this help or command-specific help

Usage: <command> [arguments]
Type 'help <command>' for detailed information about a specific command.""")


def _show_command_help(command: str) -> None:
    """Display command-specific help.

    Args:
        command: Command name to display help for
    """
    help_messages = {
        "create": """Command: create
Description: Create a new task
Usage: create <title> [-m|--message <description>]

Arguments:
  <title>       Task title (required)
  -m, --message  Task description (optional)

Examples:
  create Buy groceries
  create "Buy groceries" -m "Milk, eggs, bread" """,

        "view": """Command: view
Description: View task list
Usage: view [--completed|--incomplete]

Arguments:
  --completed    Show only completed tasks
  --incomplete   Show only incomplete tasks

Examples:
  view
  view --completed
  view --incomplete """,

        "update": """Command: update
Description: Update task details
Usage: update <id> [--title <title>] [--description <description>]

Arguments:
  <id>             Task ID to update
  --title <title>    New task title
  --description       New task description

Examples:
  update 2 --title "Buy snacks"
  update 2 --description "Chips and soda" """,

        "delete": """Command: delete
Description: Delete a task
Usage: delete <id>

Arguments:
  <id>  Task ID to delete

Examples:
  delete 3
  delete 5 """,

        "complete": """Command: complete
Description: Mark a task as completed
Usage: complete <id>

Arguments:
  <id>  Task ID to mark complete

Examples:
  complete 1
  complete 2 """,

        "incomplete": """Command: incomplete
Description: Mark a task as incomplete
Usage: incomplete <id>

Arguments:
  <id>  Task ID to mark incomplete

Examples:
  incomplete 1
  incomplete 3 """,

        "toggle": """Command: toggle
Description: Toggle task completion status
Usage: toggle <id>

Arguments:
  <id>  Task ID to toggle

Examples:
  toggle 2
  toggle 5 """,

        "help": """Command: help
Description: Display command help
Usage: help [command]

Arguments:
  <command>  Specific command to display help for (optional)

Examples:
  help
  help create
  help view """
    }

    if command in help_messages:
        print(help_messages[command])
    else:
        print(f"Error: Invalid command '{command}'. Type 'help' to see available commands.")
