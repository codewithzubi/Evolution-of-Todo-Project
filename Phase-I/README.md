# The Evolution of Todo - Phase I

A Python console-based Todo application with rich UI, in-memory storage, and comprehensive task management features.

## Features

- **Basic Task Management**: Add, view, update, delete, and mark tasks complete/incomplete
- **Enhanced Features**: Priority levels (High/Medium/Low), tags, search, filter, and sort capabilities
- **Advanced Features**: Due dates with overdue highlighting, recurring tasks (daily/weekly/monthly)
- **Rich UI**: Colorful console output using the rich library with professional table displays
- **Menu-Driven Interface**: Numbered options for all features with intuitive navigation

## Requirements

- Python 3.13+
- UV package manager (optional, for virtual environment management)
- Rich library (installed automatically)

## Setup

1. Clone the repository
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install rich
   ```

## Usage

Run the application:
```bash
python -m src.main
```

The application will display a welcome message and a numbered menu with options for all features.

## Project Structure

```
src/
├── main.py              # Entry point and main application loop
├── models/
│   └── task.py          # Task data model definition
├── services/
│   ├── storage.py       # In-memory storage manager
│   └── task_service.py  # Task business logic
├── ui/
│   ├── welcome.py       # Welcome message display
│   ├── menu.py          # Menu system
│   └── table_display.py # Rich table display for tasks
└── utils/
    ├── validators.py    # Input validation utilities
    └── date_utils.py    # Date/time utilities
```

## Features in Detail

1. **Add Task**: Create new tasks with title and description
2. **View Tasks**: Display all tasks in a professional table format
3. **Update Task**: Modify any field of an existing task
4. **Delete Task**: Remove a task by ID (with confirmation)
5. **Mark Complete**: Toggle task completion status
6. **Set Priority**: Assign High/Medium/Low priority levels
7. **Add Tags**: Categorize tasks with multiple tags
8. **Search Tasks**: Find tasks by keyword in title or description
9. **Filter Tasks**: Show tasks matching specific criteria
10. **Sort Tasks**: Organize tasks by various attributes
11. **Set Due Date**: Assign deadlines to tasks with overdue highlighting
12. **Recurring Tasks**: Create tasks that repeat daily/weekly/monthly

## Architecture

- **In-Memory Storage**: Tasks stored in a dictionary with O(1) lookup time
- **Rich UI**: All output uses the rich library for professional styling
- **Modular Design**: Separation of concerns with distinct modules for models, services, UI, and utilities
- **Validation**: Comprehensive input validation with user-friendly error messages
- **Error Handling**: Graceful handling of invalid inputs and edge cases

## License

This project is part of a hackathon and follows the repository's licensing terms.