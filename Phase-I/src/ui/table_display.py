from rich.console import Console
from rich.table import Table
from rich.text import Text
from datetime import datetime
from typing import List
from ..models.task import Task


class TableDisplay:
    """
    Display tasks in a professional rich.Table format with all required columns.
    Columns: ID, Title, Description, Status, Priority, Tags, Due Date, Recurring
    """

    def __init__(self):
        self.console = Console()

    def display_tasks(self, tasks: List[Task], title: str = "Tasks"):
        """
        Display a list of tasks in a rich table format.
        """
        if not tasks:
            self.console.print(f"[yellow]No {title.lower()} found.[/yellow]")
            return

        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", justify="center")
        table.add_column("Title", style="green")
        table.add_column("Description", style="blue")
        table.add_column("Status", style="bold", justify="center")
        table.add_column("Priority", style="magenta")
        table.add_column("Tags", style="yellow")
        table.add_column("Due Date", style="red")
        table.add_column("Recurring", style="cyan")

        for task in tasks:
            # Format status with symbols and colors
            status_text = "✓" if task.completed else "✗"
            status_style = "green" if task.completed else "red"
            status = Text(status_text, style=f"bold {status_style}")

            # Format priority with colors
            priority_style = self._get_priority_style(task.priority)
            priority = Text(task.priority, style=priority_style)

            # Format tags as comma-separated string
            tags_str = ", ".join(task.tags) if task.tags else ""

            # Format due date with overdue highlighting
            due_date_str = ""
            if task.due_date:
                due_date_str = task.due_date.strftime("%Y-%m-%d")
                # Highlight overdue tasks in red
                if task.due_date < datetime.now() and not task.completed:
                    due_date_str = f"[red]{due_date_str}[/red]"

            # Format recurring information
            recurring_str = task.recurring if task.recurring else ""

            table.add_row(
                str(task.id),
                task.title,
                task.description,
                status,
                priority,
                tags_str,
                due_date_str,
                recurring_str
            )

        self.console.print(table)

    def _get_priority_style(self, priority: str) -> str:
        """
        Get the appropriate style for the priority level.
        """
        if priority == "High":
            return "bold red"
        elif priority == "Medium":
            return "bold yellow"
        elif priority == "Low":
            return "bold green"
        else:
            return "bold white"  # Default style


if __name__ == "__main__":
    # Test the table display
    from datetime import datetime, timedelta

    # Create some sample tasks
    sample_tasks = [
        Task(
            id=1,
            title="Sample Task 1",
            description="This is a sample task",
            completed=False,
            priority="High",
            tags=["work", "important"],
            due_date=datetime.now() + timedelta(days=2),
            recurring="weekly"
        ),
        Task(
            id=2,
            title="Sample Task 2",
            description="This is another sample task",
            completed=True,
            priority="Low",
            tags=["personal"],
            due_date=datetime.now() - timedelta(days=1),  # Overdue
            recurring=None
        )
    ]

    display = TableDisplay()
    display.display_tasks(sample_tasks, "Sample Tasks")