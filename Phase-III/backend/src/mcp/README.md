# MCP (Model Context Protocol) Server - Phase-III AI Chatbot

Stateless MCP tool implementations that wrap existing Phase-II task APIs, enabling AI agents (like OpenAI Agents SDK) to interact with tasks through natural language.

## Overview

The MCP server provides 5 task management tools:
1. **add_task** - Create new tasks
2. **list_tasks** - Query tasks with filters (status, priority, overdue)
3. **update_task** - Modify task fields
4. **complete_task** - Mark tasks as done
5. **delete_task** - Delete tasks (requires confirmation)

All tools are:
- **Stateless**: No in-memory state; each call is independent
- **User-scoped**: All operations filtered by `user_id` from JWT tokens
- **Phase-II integrated**: Call existing task APIs, no direct database access
- **Error-resilient**: Handle timeouts, unavailability, and malformed responses gracefully

## Architecture

### Tool Flow

```
AI Agent (OpenAI SDK)
    ↓
  Tool Call (JSON)
    ↓
MCPToolExecutor.execute_tool()
    ↓
Tool Implementation (add_task, list_tasks, etc.)
    ↓
_call_phase2_api()
    ↓
Phase-II API Endpoint
    ↓
Database
```

### User Isolation

Every tool receives `user_id` from JWT claims:

```python
# Example: Agent calls add_task with user_id from JWT
add_task(
    user_id=<extracted from JWT>,  # Cannot be forged
    title="Buy groceries",
    priority="high"
)

# Tool calls Phase-II API with user_id in endpoint
POST /api/v1/users/{user_id}/tasks
```

## Module Structure

```
backend/src/mcp/
├── __init__.py          # Module initialization
├── schemas.py           # Pydantic input/output schemas
├── tools.py             # Tool implementations (add_task, list_tasks, etc.)
├── server.py            # MCP server + tool executor
└── README.md            # This file
```

## Schemas (schemas.py)

### Input Schemas

- **AddTaskInput**: title, description, priority, due_date, tags, user_id
- **ListTasksInput**: status, priority, overdue, limit, offset, user_id
- **UpdateTaskInput**: task_id, title, description, priority, due_date, tags, user_id
- **CompleteTaskInput**: task_id, user_id
- **DeleteTaskInput**: task_id, user_id

### Output Schemas

- **ToolResult**: Standard wrapper (success, data, error, message)
- **ListTasksOutput**: Specialized for list_tasks (tasks, total_count, returned_count)
- **TaskOutput**: Task object (id, title, priority, completed, due_date, etc.)

## Tools (tools.py)

### add_task

Creates a new task via `POST /api/v1/users/{user_id}/tasks`.

**Parameters**:
- `user_id` (UUID, required): From JWT token
- `title` (str, required): Task title (1-255 chars)
- `description` (str, optional): Task details (max 2000 chars)
- `priority` (enum, optional): low/medium/high (default: medium)
- `due_date` (str, optional): ISO 8601 date (e.g., "2026-02-14")
- `tags` (list, optional): Task labels

**Returns**: ToolResult with task object or error message

**Example**:
```python
result = await add_task(AddTaskInput(
    user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
    title="Buy groceries",
    priority=TaskPriority.HIGH,
))
# {
#   "success": true,
#   "data": {"id": "...", "title": "Buy groceries", ...},
#   "message": "Task 'Buy groceries' created successfully!"
# }
```

### list_tasks

Lists user's tasks with optional filters via `GET /api/v1/users/{user_id}/tasks`.

**Parameters**:
- `user_id` (UUID, required): From JWT token
- `status` (enum, optional): completed/incomplete
- `priority` (enum, optional): low/medium/high
- `overdue` (bool, optional): Show only overdue incomplete tasks
- `limit` (int, optional, default 10): Max results (1-100)
- `offset` (int, optional, default 0): Pagination offset

**Returns**: ListTasksOutput with task array or error message

**Example**:
```python
result = await list_tasks(ListTasksInput(
    user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
    status=TaskStatus.INCOMPLETE,
    priority=TaskPriority.HIGH,
    overdue=False,
))
# {
#   "success": true,
#   "tasks": [TaskOutput(...), ...],
#   "total_count": 5,
#   "returned_count": 1,
#   "message": "Found 5 tasks, returning 1 (high priority only)"
# }
```

### update_task

Updates specific task fields via `PUT /api/v1/users/{user_id}/tasks/{task_id}`.

**Parameters**:
- `user_id` (UUID, required): From JWT token
- `task_id` (UUID, required): Task to update
- `title` (str, optional): New title
- `description` (str, optional): New description
- `priority` (enum, optional): New priority
- `due_date` (str, optional): New due date
- `tags` (list, optional): New tags

**Returns**: ToolResult with updated task object or error message

**Example**:
```python
result = await update_task(UpdateTaskInput(
    user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
    task_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
    priority=TaskPriority.HIGH,
))
# {
#   "success": true,
#   "data": {"id": "...", "priority": "high", ...},
#   "message": "Task updated successfully!"
# }
```

### complete_task

Marks a task as completed via `PATCH /api/v1/users/{user_id}/tasks/{task_id}/complete`.

**Parameters**:
- `user_id` (UUID, required): From JWT token
- `task_id` (UUID, required): Task to complete

**Returns**: ToolResult with updated task object or error message

**Example**:
```python
result = await complete_task(CompleteTaskInput(
    user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
    task_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
))
# {
#   "success": true,
#   "data": {"id": "...", "completed": true, ...},
#   "message": "Task marked as complete! Great job! 🎉"
# }
```

### delete_task

Deletes a task permanently via `DELETE /api/v1/users/{user_id}/tasks/{task_id}`.

**Parameters**:
- `user_id` (UUID, required): From JWT token
- `task_id` (UUID, required): Task to delete

**Returns**: ToolResult with success or error message

**Example**:
```python
result = await delete_task(DeleteTaskInput(
    user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
    task_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
))
# {
#   "success": true,
#   "message": "Task deleted successfully."
# }
```

## Server (server.py)

### MCPToolExecutor

Executes tools with parameter validation and error handling.

**Methods**:

```python
@staticmethod
def get_tool_definitions() -> list[Dict[str, Any]]:
    """Get OpenAI-compatible tool definitions for agents."""

@staticmethod
async def execute_tool(
    tool_name: str,
    tool_input: Dict[str, Any],
) -> Dict[str, Any]:
    """Execute a tool with parameter validation."""
```

**Usage**:
```python
from src.mcp.server import MCPToolExecutor

# Get tool definitions for OpenAI SDK
tools = MCPToolExecutor.get_tool_definitions()

# Execute a tool
result = await MCPToolExecutor.execute_tool(
    tool_name="add_task",
    tool_input={
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Buy groceries",
        "priority": "high",
    }
)
```

### Helper Functions

```python
def get_mcp_tools_for_agent() -> list[Dict[str, Any]]:
    """Get tool definitions for OpenAI Agents SDK."""

def format_tool_result_for_agent(
    tool_name: str,
    tool_result: Dict[str, Any],
) -> str:
    """Format tool result as natural language for agent."""
```

## Error Handling

Tools handle errors gracefully and return user-friendly messages:

| Error | Status | Message |
|-------|--------|---------|
| Empty title | 422 | "I need a task title to create the task." |
| Invalid priority | 422 | "Validation failed: priority" |
| Task not found | 404 | "I couldn't find that task. Did you mean a different one?" |
| User doesn't own task | 403 | "You don't have permission to [action] this task." |
| Unauthorized (no JWT) | 401 | "I'm not authorized to [action] tasks." |
| API timeout | 504 | "I encountered an error. Please try again." |
| API unavailable | 503 | "I'm having trouble connecting. Please try again." |

## User Isolation

Every tool enforces user isolation:

1. **JWT Extraction**: `user_id` extracted from JWT token by caller (chat endpoint)
2. **Parameter Injection**: `user_id` passed to tool (cannot be forged by user input)
3. **API Call Scoping**: Tool calls Phase-II endpoint with `user_id` in path:
   ```
   POST /api/v1/users/{user_id}/tasks
   ```
4. **Error Handling**: Phase-II API returns 403 Forbidden if `user_id` doesn't match resource ownership

**Guarantee**: User A cannot access, modify, or delete User B's tasks through MCP tools.

## Phase-II API Integration

Tools call these existing Phase-II endpoints:

| Tool | Method | Endpoint | Auth |
|------|--------|----------|------|
| add_task | POST | `/api/v1/users/{user_id}/tasks` | JWT |
| list_tasks | GET | `/api/v1/users/{user_id}/tasks` | JWT |
| update_task | PUT | `/api/v1/users/{user_id}/tasks/{task_id}` | JWT |
| complete_task | PATCH | `/api/v1/users/{user_id}/tasks/{task_id}/complete` | JWT |
| delete_task | DELETE | `/api/v1/users/{user_id}/tasks/{task_id}` | JWT |

**Note**: No modifications to Phase-II code. Tools are backward-compatible with existing endpoints.

## Testing

Unit tests in `backend/tests/unit/test_mcp_tools.py`:

- ✅ Tool success cases (create, list, update, complete, delete)
- ✅ Parameter validation (empty title, invalid priority)
- ✅ Error handling (401, 403, 404, 422, 500, 503, 504)
- ✅ User isolation (User B cannot access User A's data)
- ✅ API resilience (timeouts, unavailability)

**Run tests**:
```bash
pytest backend/tests/unit/test_mcp_tools.py -v
```

## Configuration

### Environment Variables

```bash
# Phase-II Backend URL (for MCP tools to call)
PHASE2_API_URL=http://localhost:8000

# OpenAI Configuration (for future AI agent)
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# JWT Secret (shared with Phase-II)
JWT_SECRET=your_super_secret_jwt_key_change_this_in_production
```

### Configuration Loading

Settings automatically loaded from `config.py`:

```python
from src.config import settings

phase2_url = settings.phase2_api_url
openai_key = settings.openai_api_key
jwt_secret = settings.jwt_secret
```

## Future Enhancements

1. **Conversation Storage**: Persist conversation history in database
2. **Agent Integration**: Bind tools to OpenAI Agents SDK for multi-turn reasoning
3. **Chat Endpoint**: Expose `/api/v1/chat/conversations/{id}/messages` for frontend
4. **Rate Limiting**: Add request throttling to prevent abuse
5. **Caching**: Cache list_tasks results for improved performance
6. **Analytics**: Track tool usage and performance metrics

## Security Considerations

- ✅ No hardcoded secrets (all from environment variables)
- ✅ JWT validation on every request (in chat endpoint)
- ✅ User ID scoping (tools receive user_id from JWT, cannot be overridden)
- ✅ Parameter validation (Pydantic schemas enforce constraints)
- ✅ Error safety (no sensitive details in error messages)
- ✅ Timeout protection (10-second timeout on Phase-II API calls)
- ✅ Graceful degradation (friendly errors when Phase-II unavailable)

## References

- **Spec**: `specs/004-ai-chatbot/spec.md`
- **Architecture**: `specs/004-ai-chatbot/ARCHITECTURE.md`
- **Plan**: `specs/004-ai-chatbot/plan.md`
- **Tasks**: `specs/004-ai-chatbot/tasks.md` (T307-T315)

## Support

For questions or issues:
1. Check unit tests in `backend/tests/unit/test_mcp_tools.py`
2. Review tool docstrings in `backend/src/mcp/tools.py`
3. Consult ARCHITECTURE.md for design details
4. Check Phase-II API contracts in `/api/v1/users/{user_id}/tasks*`
