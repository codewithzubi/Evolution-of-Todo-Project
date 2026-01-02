#!/usr/bin/env python3
"""
Main application entry point for the Todo application.
Implements the main application loop that integrates welcome, menu, and task operations.
"""

from .ui.welcome import display_welcome_message
from .ui.menu import Menu
from .services.task_service import TaskService
from .ui.table_display import TableDisplay
from .utils.validators import validate_task_title, validate_input_not_empty
from datetime import datetime


def main():
    """Main application loop."""
    # Initialize components
    menu = Menu()
    task_service = TaskService()
    table_display = TableDisplay()

    # Display welcome message
    display_welcome_message()

    while True:
        # Display menu
        menu.display_menu()

        # Get user choice
        choice = menu.get_user_choice()

        if choice == 0:  # Exit
            menu.display_message("Thank you for using The Evolution of Todo. Goodbye!", "bold blue")
            break

        elif choice == 1:  # Add Task
            title = menu.get_input("[bold cyan]Enter task title:[/bold cyan]")
            if not validate_task_title(title):
                menu.display_message("Invalid title. Title must be non-empty and less than or equal to 200 characters.", "red")
                continue

            description = menu.get_input("[bold cyan]Enter task description (optional):[/bold cyan]")
            task = task_service.add_task(title, description)
            if task:
                menu.display_message(f"Task '{task.title}' added successfully with ID {task.id}", "green")
            else:
                menu.display_message("Failed to add task.", "red")

        elif choice == 2:  # View All Tasks
            tasks = task_service.get_all_tasks()
            table_display.display_tasks(tasks, "All Tasks")

        elif choice == 3:  # Update Task
            try:
                task_id_input = menu.get_input("[bold cyan]Enter task ID to update:[/bold cyan]")
                if not task_id_input.strip():
                    menu.display_message("Task ID cannot be empty.", "red")
                    continue

                task_id = int(task_id_input)
                task = task_service.get_task(task_id)
                if not task:
                    menu.display_message(f"Task with ID {task_id} not found.", "red")
                    continue

                menu.display_message(f"Current task: {task.title}", "yellow")
                new_title = menu.get_input(f"[bold cyan]Enter new title (current: {task.title}) or press Enter to keep:[/bold cyan]")
                new_description = menu.get_input(f"[bold cyan]Enter new description (current: {task.description}) or press Enter to keep:[/bold cyan]")

                updates = {}
                if new_title.strip():
                    updates['title'] = new_title
                if new_description.strip():
                    updates['description'] = new_description

                if updates:
                    success = task_service.update_task(task_id, **updates)
                    if success:
                        menu.display_message(f"Task {task_id} updated successfully.", "green")
                    else:
                        menu.display_message("Failed to update task.", "red")
                else:
                    menu.display_message("No updates provided.", "yellow")

            except ValueError:
                menu.display_message("Invalid task ID. Please enter a number.", "red")
            except Exception as e:
                menu.display_message(f"An error occurred while updating the task: {str(e)}", "red")

        elif choice == 4:  # Delete Task
            try:
                task_id_input = menu.get_input("[bold cyan]Enter task ID to delete:[/bold cyan]")
                if not task_id_input.strip():
                    menu.display_message("Task ID cannot be empty.", "red")
                    continue

                task_id = int(task_id_input)
                task = task_service.get_task(task_id)
                if not task:
                    menu.display_message(f"Task with ID {task_id} not found.", "red")
                    continue

                # Ask for confirmation before deletion
                confirm = menu.get_input(f"[bold yellow]Are you sure you want to delete task '{task.title}'? (y/N):[/bold yellow]").lower()
                if confirm not in ['y', 'yes']:
                    menu.display_message("Task deletion cancelled.", "yellow")
                    continue

                success = task_service.delete_task(task_id)
                if success:
                    menu.display_message(f"Task {task_id} deleted successfully.", "green")
                else:
                    menu.display_message(f"Task with ID {task_id} not found.", "red")
            except ValueError:
                menu.display_message("Invalid task ID. Please enter a number.", "red")
            except Exception as e:
                menu.display_message(f"An error occurred while deleting the task: {str(e)}", "red")

        elif choice == 5:  # Mark Task Complete/Incomplete
            try:
                task_id_input = menu.get_input("[bold cyan]Enter task ID to toggle completion status:[/bold cyan]")
                if not task_id_input.strip():
                    menu.display_message("Task ID cannot be empty.", "red")
                    continue

                task_id = int(task_id_input)
                task = task_service.get_task(task_id)
                if not task:
                    menu.display_message(f"Task with ID {task_id} not found.", "red")
                    continue

                success = task_service.toggle_task_completion(task_id)
                if success:
                    new_status = "completed" if task.completed else "incomplete"
                    menu.display_message(f"Task {task_id} marked as {new_status}.", "green")
                else:
                    menu.display_message("Failed to update task status.", "red")
            except ValueError:
                menu.display_message("Invalid task ID. Please enter a number.", "red")
            except Exception as e:
                menu.display_message(f"An error occurred while updating task status: {str(e)}", "red")

        elif choice == 6:  # Set/Edit Priority
            try:
                task_id_input = menu.get_input("[bold cyan]Enter task ID to set priority:[/bold cyan]")
                if not task_id_input.strip():
                    menu.display_message("Task ID cannot be empty.", "red")
                    continue

                task_id = int(task_id_input)
                task = task_service.get_task(task_id)
                if not task:
                    menu.display_message(f"Task with ID {task_id} not found.", "red")
                    continue

                priority = menu.get_input(f"[bold cyan]Enter priority (High/Medium/Low, current: {task.priority}):[/bold cyan]")
                priority = priority.strip().capitalize()

                if priority not in ["High", "Medium", "Low"]:
                    menu.display_message("Invalid priority. Must be High, Medium, or Low.", "red")
                    continue

                success = task_service.set_task_priority(task_id, priority)
                if success:
                    menu.display_message(f"Priority for task {task_id} set to {priority}.", "green")
                else:
                    menu.display_message("Failed to update task priority.", "red")
            except ValueError:
                menu.display_message("Invalid task ID. Please enter a number.", "red")
            except Exception as e:
                menu.display_message(f"An error occurred while setting task priority: {str(e)}", "red")

        elif choice == 7:  # Add/Edit Tags
            try:
                task_id_input = menu.get_input("[bold cyan]Enter task ID to add tags:[/bold cyan]")
                if not task_id_input.strip():
                    menu.display_message("Task ID cannot be empty.", "red")
                    continue

                task_id = int(task_id_input)
                task = task_service.get_task(task_id)
                if not task:
                    menu.display_message(f"Task with ID {task_id} not found.", "red")
                    continue

                tags_input = menu.get_input(f"[bold cyan]Enter tags (comma-separated, current: {', '.join(task.tags)}):[/bold cyan]")
                if not tags_input.strip():
                    menu.display_message("No tags provided.", "yellow")
                    continue

                tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

                success = task_service.add_task_tags(task_id, tags)
                if success:
                    menu.display_message(f"Tags added to task {task_id}.", "green")
                else:
                    menu.display_message("Failed to add tags to task.", "red")
            except ValueError:
                menu.display_message("Invalid task ID. Please enter a number.", "red")
            except Exception as e:
                menu.display_message(f"An error occurred while adding tags to task: {str(e)}", "red")

        elif choice == 8:  # Search Tasks
            keyword = menu.get_input("[bold cyan]Enter search keyword:[/bold cyan]")
            if not keyword.strip():
                menu.display_message("No keyword provided.", "yellow")
                continue

            tasks = task_service.search_tasks(keyword)
            table_display.display_tasks(tasks, f"Search Results for '{keyword}'")

        elif choice == 9:  # Filter Tasks
            filter_type = menu.get_input("[bold cyan]Filter by (status/priority/tags) or press Enter for none:[/bold cyan]").lower()

            if filter_type == "status":
                status = menu.get_input("[bold cyan]Enter status (completed/incomplete):[/bold cyan]").lower()
                if status not in ["completed", "incomplete"]:
                    menu.display_message("Invalid status. Must be 'completed' or 'incomplete'.", "red")
                    continue
                criteria = {"status": status}
            elif filter_type == "priority":
                priority = menu.get_input("[bold cyan]Enter priority (High/Medium/Low):[/bold cyan]").capitalize()
                if priority not in ["High", "Medium", "Low"]:
                    menu.display_message("Invalid priority. Must be High, Medium, or Low.", "red")
                    continue
                criteria = {"priority": priority}
            elif filter_type == "tags":
                tags_input = menu.get_input("[bold cyan]Enter tags (comma-separated):[/bold cyan]")
                tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
                criteria = {"tags": tags}
            else:
                menu.display_message("Invalid filter type.", "red")
                continue

            tasks = task_service.filter_tasks(criteria)
            table_display.display_tasks(tasks, f"Filtered Tasks by {filter_type}")

        elif choice == 10:  # Sort Tasks
            sort_by = menu.get_input("[bold cyan]Sort by (due_date/priority/title):[/bold cyan]").lower()
            if sort_by not in ["due_date", "priority", "title"]:
                menu.display_message("Invalid sort option. Must be 'due_date', 'priority', or 'title'.", "red")
                continue

            reverse = menu.get_input("[bold cyan]Reverse order? (y/n):[/bold cyan]").lower() == 'y'
            tasks = task_service.sort_tasks(sort_by, reverse)
            table_display.display_tasks(tasks, f"Tasks Sorted by {sort_by}")

        elif choice == 11:  # Set Due Date
            try:
                task_id_input = menu.get_input("[bold cyan]Enter task ID to set due date:[/bold cyan]")
                if not task_id_input.strip():
                    menu.display_message("Task ID cannot be empty.", "red")
                    continue

                task_id = int(task_id_input)
                task = task_service.get_task(task_id)
                if not task:
                    menu.display_message(f"Task with ID {task_id} not found.", "red")
                    continue

                from .utils.date_utils import parse_date
                date_str = menu.get_input("[bold cyan]Enter due date (YYYY-MM-DD or MM/DD/YYYY):[/bold cyan]")
                if not date_str.strip():
                    menu.display_message("Date cannot be empty.", "red")
                    continue

                due_date = parse_date(date_str)

                if not due_date:
                    menu.display_message("Invalid date format.", "red")
                    continue

                success = task_service.set_task_due_date(task_id, due_date)
                if success:
                    menu.display_message(f"Due date for task {task_id} set to {due_date.strftime('%Y-%m-%d')}.", "green")
                else:
                    menu.display_message("Failed to set due date.", "red")
            except ValueError:
                menu.display_message("Invalid task ID. Please enter a number.", "red")
            except Exception as e:
                menu.display_message(f"An error occurred while setting due date: {str(e)}", "red")

        elif choice == 12:  # Set Recurring Task
            try:
                task_id_input = menu.get_input("[bold cyan]Enter task ID to set recurring:[/bold cyan]")
                if not task_id_input.strip():
                    menu.display_message("Task ID cannot be empty.", "red")
                    continue

                task_id = int(task_id_input)
                task = task_service.get_task(task_id)
                if not task:
                    menu.display_message(f"Task with ID {task_id} not found.", "red")
                    continue

                frequency = menu.get_input("[bold cyan]Enter frequency (daily/weekly/monthly) or 'none' to clear:[/bold cyan]").lower().strip()

                if frequency == "none":
                    frequency = None
                elif frequency not in ["daily", "weekly", "monthly"]:
                    menu.display_message("Invalid frequency. Must be 'daily', 'weekly', 'monthly', or 'none'.", "red")
                    continue

                success = task_service.set_task_recurring(task_id, frequency)
                if success:
                    freq_display = frequency if frequency else "none"
                    menu.display_message(f"Recurring frequency for task {task_id} set to {freq_display}.", "green")
                else:
                    menu.display_message("Failed to set recurring frequency.", "red")
            except ValueError:
                menu.display_message("Invalid task ID. Please enter a number.", "red")
            except Exception as e:
                menu.display_message(f"An error occurred while setting recurring task: {str(e)}", "red")

        else:
            menu.display_message("Invalid option. Please try again.", "red")

        # Add a pause to allow user to read messages
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()