"""Command-line argument parser using argparse."""

import argparse
from typing import Optional


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="",
        description="In-memory todo command-line application",
        add_help=False
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=False,
        help="Available commands"
    )

    # create command
    create_parser = subparsers.add_parser(
        "create",
        help="Create a new task",
        add_help=False
    )
    create_parser.add_argument(
        "title",
        help="Task title (required)"
    )
    create_parser.add_argument(
        "-m", "--message",
        dest="description",
        help="Task description (optional)"
    )

    # view command
    view_parser = subparsers.add_parser(
        "view",
        help="View task list",
        add_help=False
    )
    view_group = view_parser.add_mutually_exclusive_group()
    view_group.add_argument(
        "--completed",
        action="store_true",
        help="Show only completed tasks"
    )
    view_group.add_argument(
        "--incomplete",
        action="store_true",
        help="Show only incomplete tasks"
    )

    # update command
    update_parser = subparsers.add_parser(
        "update",
        help="Update task details",
        add_help=False
    )
    update_parser.add_argument(
        "id",
        type=int,
        help="Task ID to update"
    )
    update_parser.add_argument(
        "--title",
        help="New task title"
    )
    update_parser.add_argument(
        "--description",
        help="New task description"
    )

    # delete command
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a task",
        add_help=False
    )
    delete_parser.add_argument(
        "id",
        type=int,
        help="Task ID to delete"
    )

    # complete command
    complete_parser = subparsers.add_parser(
        "complete",
        help="Mark task as completed",
        add_help=False
    )
    complete_parser.add_argument(
        "id",
        type=int,
        help="Task ID to mark complete"
    )

    # incomplete command
    incomplete_parser = subparsers.add_parser(
        "incomplete",
        help="Mark task as incomplete",
        add_help=False
    )
    incomplete_parser.add_argument(
        "id",
        type=int,
        help="Task ID to mark incomplete"
    )

    # toggle command
    toggle_parser = subparsers.add_parser(
        "toggle",
        help="Toggle task completion status",
        add_help=False
    )
    toggle_parser.add_argument(
        "id",
        type=int,
        help="Task ID to toggle"
    )

    # help command
    help_parser = subparsers.add_parser(
        "help",
        help="Display help information",
        add_help=False
    )
    help_parser.add_argument(
        "command",
        nargs="?",
        help="Command to display help for (optional)"
    )

    return parser
