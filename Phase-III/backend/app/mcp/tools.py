"""MCP Tools for AI agent - Phase-III."""
from uuid import UUID
from typing import Dict, Any, Optional
from datetime import datetime
from sqlmodel import Session, select
from app.models.task import Task


# Tool Functions

def add_task(user_id: UUID, title: str, description: Optional[str], db: Session) -> Dict[str, Any]:
    """Create a new task."""
    task = Task(user_id=user_id, title=title, description=description, is_completed=False)
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"status": "success", "task_id": str(task.id), "title": task.title}


def list_tasks(user_id: UUID, status: str = "all", db: Session = None) -> Dict[str, Any]:
    """List user's tasks by status filter."""
    query = select(Task).where(Task.user_id == user_id)

    # Handle various status parameter names (for flexibility)
    status_lower = status.lower() if status else "all"

    if status_lower in ["completed", "complete", "done"]:
        query = query.where(Task.is_completed == True)
    elif status_lower in ["pending", "incomplete", "todo", "active"]:
        query = query.where(Task.is_completed == False)
    # else: status_lower == "all" - no filter, return all tasks

    tasks = db.exec(query).all()
    return {
        "status": "success",
        "tasks": [
            {
                "id": str(t.id),
                "title": t.title,
                "completed": t.is_completed,
                "priority": t.priority if hasattr(t, 'priority') else "medium",
                "description": t.description if t.description else ""
            }
            for t in tasks
        ],
        "count": len(tasks)
    }


def toggle_task(user_id: UUID, task_id: int, db: Session) -> Dict[str, Any]:
    """Toggle task completion status (completed ↔ pending)."""
    query = select(Task).where(Task.user_id == user_id, Task.id == task_id)
    task = db.exec(query).first()

    if not task:
        return {"status": "error", "message": f"Task {task_id} not found"}

    task.is_completed = not task.is_completed
    db.add(task)
    db.commit()

    status_text = "completed" if task.is_completed else "pending"
    return {"status": "success", "task_id": task_id, "title": task.title, "completed": task.is_completed, "new_status": status_text}


def update_task(user_id: UUID, task_id: int, new_title: Optional[str], new_description: Optional[str], priority: Optional[str], due_date: Optional[str], db: Session) -> Dict[str, Any]:
    """Update task details including priority and due date."""
    query = select(Task).where(Task.user_id == user_id, Task.id == task_id)
    task = db.exec(query).first()

    if not task:
        return {"status": "error", "message": f"Task {task_id} not found"}

    if new_title:
        task.title = new_title
    if new_description is not None:
        task.description = new_description
    if priority is not None:
        if priority.lower() not in ["high", "medium", "low"]:
            return {"status": "error", "message": "Priority must be 'high', 'medium', or 'low'"}
        task.priority = priority.lower()
    if due_date is not None:
        try:
            parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            task.due_date = parsed_date
        except ValueError:
            return {"status": "error", "message": "Invalid due_date format. Use YYYY-MM-DD"}

    db.add(task)
    db.commit()

    response = {"status": "success", "task_id": task_id, "title": task.title, "priority": task.priority}
    if task.due_date:
        response["due_date"] = task.due_date.isoformat()

    return response


def delete_task(user_id: UUID, task_id: int, db: Session) -> Dict[str, Any]:
    """Delete a task."""
    query = select(Task).where(Task.user_id == user_id, Task.id == task_id)
    task = db.exec(query).first()

    if not task:
        return {"status": "error", "message": f"Task {task_id} not found"}

    title = task.title
    db.delete(task)
    db.commit()
    return {"status": "success", "task_id": task_id, "message": f"Deleted task: {title}"}


# OpenAI Function Calling Definitions

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description (optional)"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List user's tasks filtered by status. ALWAYS call this when user asks to see/show/list/view tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status: 'all' (show everything), 'pending' (incomplete tasks), 'completed' (done tasks). Default is 'all'."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "toggle_task",
            "description": "Toggle task completion status. If task is completed, mark it as pending. If task is pending, mark it as completed. Use this for 'complete', 'done', 'incomplete', 'uncomplete', 'redo' requests.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID (number shown on card, e.g., 1, 5, 7)"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update task title, description, priority, or due date",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID (number shown on card, e.g., 1, 5, 7)"},
                    "new_title": {"type": "string", "description": "New title (optional)"},
                    "new_description": {"type": "string", "description": "New description (optional)"},
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Task priority: high, medium, or low (optional)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in YYYY-MM-DD format (optional, e.g., '2026-02-28')"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task permanently",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID (number shown on card, e.g., 1, 5, 7)"}
                },
                "required": ["task_id"]
            }
        }
    }
]


# Tool Executor

def execute_tool(tool_name: str, arguments: Dict[str, Any], user_id: UUID, db: Session) -> Dict[str, Any]:
    """Execute a tool by name with given arguments."""
    if tool_name == "add_task":
        return add_task(user_id, arguments.get("title"), arguments.get("description"), db)
    elif tool_name == "list_tasks":
        return list_tasks(user_id, arguments.get("status", "all"), db)
    elif tool_name == "toggle_task":
        task_id = arguments.get("task_id")
        if task_id is None:
            return {"status": "error", "message": "task_id is required"}
        return toggle_task(user_id, int(task_id), db)
    elif tool_name == "update_task":
        task_id = arguments.get("task_id")
        if task_id is None:
            return {"status": "error", "message": "task_id is required"}
        return update_task(user_id, int(task_id), arguments.get("new_title"), arguments.get("new_description"), arguments.get("priority"), arguments.get("due_date"), db)
    elif tool_name == "delete_task":
        task_id = arguments.get("task_id")
        if task_id is None:
            return {"status": "error", "message": "task_id is required"}
        return delete_task(user_id, int(task_id), db)
    else:
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}
