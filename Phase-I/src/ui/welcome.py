from rich.console import Console
from rich.text import Text
from rich.align import Align
from rich.panel import Panel


def display_welcome_message():
    """
    Display the welcome message "Welcome to The Evolution of Todo" with rich styling.
    The message is centered and styled with colors and bold formatting.
    """
    console = Console()

    # Create a styled text object
    welcome_text = Text("Welcome to The Evolution of Todo", style="bold blue")
    welcome_text.stylize("bold magenta", 0, 8)  # "Welcome"
    welcome_text.stylize("bold cyan", 12, -1)   # "The Evolution of Todo"

    # Center the text using Align
    centered_text = Align.center(welcome_text)

    # Display in a panel for better visual appeal
    panel = Panel(centered_text, title="[bold green]Todo App[/bold green]", border_style="bright_blue")
    console.print(panel)

    # Add some spacing
    console.print()


if __name__ == "__main__":
    # Test the welcome message
    display_welcome_message()