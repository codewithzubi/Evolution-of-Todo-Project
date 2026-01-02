"""Main entry point for Phase-I in-memory todo CLI application."""

import sys
import os
import shlex

# Add src directory to path if not already there
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from cli.commands import (
    create_cmd,
    view_cmd,
    update_cmd,
    delete_cmd,
    complete_cmd,
    incomplete_cmd,
    toggle_cmd,
    help_cmd
)


class SimpleNamespace:
    """Simple namespace to hold parsed command and arguments."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def parse_command_line(command_input: str) -> SimpleNamespace:
    """Parse command line manually, respecting quoted arguments.

    Args:
        command_input: Raw command input string

    Returns:
        SimpleNamespace with command and arguments
    """
    # Split by quotes to preserve quoted strings
    parts = shlex.split(command_input)

    if not parts:
        return SimpleNamespace(command=None)

    command = parts[0].lower()
    args = parts[1:]

    return SimpleNamespace(command=command, args=args)


def execute_command(args: SimpleNamespace) -> None:
    """Execute command with parsed arguments.

    Args:
        args: Parsed command namespace
    """
    if args.command == "create":
        # Parse create: create <title> [-m|--message <description>]
        if not args.args:
            print("Error: Title is required. Usage: create <title> [-m <description>]")
            return

        title = args.args[0]
        description = ""

        # Find description flag
        i = 1
        while i < len(args.args):
            if args.args[i] in ("-m", "--message"):
                if i + 1 < len(args.args):
                    description = args.args[i + 1]
                    break
            i += 1

        create_cmd(SimpleNamespace(title=title, description=description))

    elif args.command == "view":
        # Parse view: view [--completed|--incomplete]
        completed = False
        incomplete = False

        for arg in args.args:
            if arg == "--completed":
                completed = True
            elif arg == "--incomplete":
                incomplete = True

        view_cmd(SimpleNamespace(completed=completed, incomplete=incomplete))

    elif args.command == "update":
        # Parse update: update <id> [--title <title>] [--description <description>]
        if not args.args or not args.args[0].isdigit():
            print("Error: Task ID is required and must be a positive integer. Usage: update <id> [--title <title>] [--description <description>]")
            return

        task_id = int(args.args[0])
        title = None
        description = None

        i = 1
        while i < len(args.args):
            if args.args[i] == "--title":
                if i + 1 < len(args.args):
                    title = args.args[i + 1]
                    i += 2
                    continue
            elif args.args[i] == "--description":
                if i + 1 < len(args.args):
                    description = args.args[i + 1]
                    i += 2
                    continue
            i += 1

        update_cmd(SimpleNamespace(id=task_id, title=title, description=description))

    elif args.command == "delete":
        # Parse delete: delete <id>
        if not args.args or not args.args[0].isdigit():
            print("Error: Task ID is required and must be a positive integer. Usage: delete <id>")
            return

        task_id = int(args.args[0])
        delete_cmd(SimpleNamespace(id=task_id))

    elif args.command == "complete":
        # Parse complete: complete <id>
        if not args.args or not args.args[0].isdigit():
            print("Error: Task ID is required and must be a positive integer. Usage: complete <id>")
            return

        task_id = int(args.args[0])
        complete_cmd(SimpleNamespace(id=task_id))

    elif args.command == "incomplete":
        # Parse incomplete: incomplete <id>
        if not args.args or not args.args[0].isdigit():
            print("Error: Task ID is required and must be a positive integer. Usage: incomplete <id>")
            return

        task_id = int(args.args[0])
        incomplete_cmd(SimpleNamespace(id=task_id))

    elif args.command == "toggle":
        # Parse toggle: toggle <id>
        if not args.args or not args.args[0].isdigit():
            print("Error: Task ID is required and must be a positive integer. Usage: toggle <id>")
            return

        task_id = int(args.args[0])
        toggle_cmd(SimpleNamespace(id=task_id))

    elif args.command == "help":
        # Parse help: help [command]
        if not args.args:
            help_cmd(SimpleNamespace(command=None))
        else:
            help_cmd(SimpleNamespace(command=args.args[0]))

    else:
        print(f"Error: Invalid command '{args.command}'. Type 'help' to see available commands.")


def print_welcome() -> None:
    """Print welcome message."""
    print("Todo Application - In-Memory CLI")
    print("Type 'help' for available commands or 'help <command>' for command-specific help.")
    print("Press Ctrl+C or send EOF to exit.")
    print()


def main() -> None:
    """Main application loop."""
    try:
        print_welcome()

        while True:
            try:
                # Read user input
                command_input = input("> ").strip()

                if not command_input:
                    continue

                # Parse and execute command
                parsed = parse_command_line(command_input)
                if parsed.command:
                    execute_command(parsed)

            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print("\n")
                break
            except EOFError:
                # Handle EOF (Ctrl+D)
                print()
                break

    finally:
        print("Goodbye!")


if __name__ == "__main__":
    main()
