# Quickstart Guide: Python Console-based Todo Application

## Overview
This guide provides quick setup and usage instructions for the Python console-based Todo application.

## Prerequisites
- Python 3.13 or higher
- UV package manager
- Rich library installed

## Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Install dependencies using UV:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install rich
   ```

3. Navigate to the source directory:
   ```bash
   cd src
   ```

## Running the Application
Execute the main application file:
```bash
python main.py
```

## Basic Usage
1. **Welcome Screen**: On startup, you'll see a colorful "Welcome to The Evolution of Todo" message
2. **Main Menu**: A numbered menu will appear with options for all features
3. **Navigation**: Enter the number corresponding to your desired action
4. **Exit**: Select option 0 to exit the application

## Available Features
- Add Task: Create new tasks with title and description
- View Tasks: Display all tasks in a professional table format
- Update Task: Modify any field of an existing task
- Delete Task: Remove a task by ID
- Mark Complete: Toggle task completion status
- Set Priority: Assign High/Medium/Low priority levels
- Add Tags: Categorize tasks with multiple tags
- Search Tasks: Find tasks by keyword
- Filter Tasks: Show tasks matching specific criteria
- Sort Tasks: Organize tasks by various attributes
- Set Due Date: Assign deadlines to tasks
- Recurring Tasks: Create tasks that repeat daily/weekly/monthly

## Example Workflow
1. Start the application: `python main.py`
2. Add a task: Select option 1, enter title and description
3. View tasks: Select option 2 to see your tasks in table format
4. Update priority: Select option for setting priority, choose task ID
5. Exit: Select option 0 when finished

## Troubleshooting
- If the application fails to start, ensure rich library is installed: `pip install rich`
- If colors don't display properly, your terminal may not support ANSI codes
- For input errors, the application will display helpful error messages and allow re-entry