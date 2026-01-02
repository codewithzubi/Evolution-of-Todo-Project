from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt


class Menu:
    """
    Main menu system for the Todo application.
    Displays numbered options for all features and handles user selection.
    """

    def __init__(self):
        self.console = Console()
        self.options = {
            1: "Add Task",
            2: "View All Tasks",
            3: "Update Task",
            4: "Delete Task",
            5: "Mark Task Complete/Incomplete",
            6: "Set/Edit Priority",
            7: "Add/Edit Tags",
            8: "Search Tasks",
            9: "Filter Tasks",
            10: "Sort Tasks",
            11: "Set Due Date",
            12: "Set Recurring Task",
            0: "Exit"
        }

    def display_menu(self):
        """Display the main menu with numbered options."""
        table = Table(title="Main Menu", show_header=True, header_style="bold magenta")
        table.add_column("Option", style="cyan", justify="center")
        table.add_column("Action", style="green")

        for option_num, option_text in self.options.items():
            table.add_row(str(option_num), option_text)

        self.console.print(table)

    def get_user_choice(self):
        """Get user's menu choice with validation."""
        while True:
            try:
                choice_str = Prompt.ask("[bold yellow]Select an option[/bold yellow]",
                                      choices=[str(k) for k in self.options.keys()])
                choice = int(choice_str)

                if choice in self.options:
                    return choice
                else:
                    self.console.print(f"[red]Invalid option. Please select from {list(self.options.keys())}[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number.[/red]")
            except KeyboardInterrupt:
                self.console.print("\n[red]Operation cancelled by user.[/red]")
                return 0  # Return 0 to exit

    def display_message(self, message: str, style: str = "green"):
        """Display a message with the specified style."""
        self.console.print(f"[{style}]{message}[/{style}]")

    def get_input(self, prompt: str) -> str:
        """Get input from the user."""
        try:
            return Prompt.ask(prompt)
        except KeyboardInterrupt:
            self.console.print("\n[red]Operation cancelled by user.[/red]")
            return ""


if __name__ == "__main__":
    # Test the menu
    menu = Menu()
    menu.display_menu()
    choice = menu.get_user_choice()
    menu.display_message(f"You selected option {choice}: {menu.options[choice]}")