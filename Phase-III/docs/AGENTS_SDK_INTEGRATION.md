# OpenAI Agents SDK Integration Guide

**Phase-III AI Chatbot - Complete Integration Documentation**

[Task]: T316–T327, [From]: specs/004-ai-chatbot/

This document provides a comprehensive guide to the OpenAI Agents SDK integration for the Phase-III AI Todo Chatbot.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [Message Flow](#message-flow)
4. [Configuration](#configuration)
5. [API Contracts](#api-contracts)
6. [Testing Guide](#testing-guide)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

## Architecture Overview

### High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│              ChatWidget Component (floating)            │
└──────────────────────┬──────────────────────────────────┘
                       │ POST /api/v1/chat/conversations/{id}/messages
                       │ + Authorization: Bearer {JWT}
                       │
┌──────────────────────▼──────────────────────────────────┐
│                 FastAPI Backend                          │
│                                                           │
│ ┌────────────────────────────────────────────────────┐  │
│ │  Chat Endpoint Handler                             │  │
│ │  - Extract user_id from JWT                        │  │
│ │  - Load conversation history from DB               │  │
│ │  - Pass to AgentExecutor                           │  │
│ └────────────────────────────────────────────────────┘  │
│              ↓                                            │
│ ┌────────────────────────────────────────────────────┐  │
│ │  AgentExecutor                                     │  │
│ │  - Format message history (20-msg limit)           │  │
│ │  - Call OpenAI Agents API                          │  │
│ │  - Parse response (text + tool_calls)              │  │
│ │  - Execute agentic loop (if tools needed)          │  │
│ └────────────────────────────────────────────────────┘  │
│              ↓                                            │
│ ┌────────────────────────────────────────────────────┐  │
│ │  ToolInvocationBridge (for each tool_call)         │  │
│ │  - Validate user_id from JWT                       │  │
│ │  - Invoke MCP tool                                 │  │
│ │  - Format result for agent                         │  │
│ └────────────────────────────────────────────────────┘  │
│              ↓                                            │
│ ┌────────────────────────────────────────────────────┐  │
│ │  MCP Tools (5 functions)                           │  │
│ │  - add_task: Create new task                       │  │
│ │  - list_tasks: Fetch tasks with filters            │  │
│ │  - update_task: Modify task fields                 │  │
│ │  - complete_task: Mark task done                   │  │
│ │  - delete_task: Remove task                        │  │
│ └────────────────────────────────────────────────────┘  │
│              ↓                                            │
│ ┌────────────────────────────────────────────────────┐  │
│ │  Phase-II Task APIs (/api/users/{user_id}/tasks)   │  │
│ │  - Provides single source of truth for tasks       │  │
│ │  - MCP tools delegate to these endpoints           │  │
│ └────────────────────────────────────────────────────┘  │
│              ↓                                            │
│ ┌────────────────────────────────────────────────────┐  │
│ │  Database: Neon PostgreSQL                         │  │
│ │  - Conversations table (new)                       │  │
│ │  - Messages table (new)                            │  │
│ │  - Tasks table (Phase-II)                          │  │
│ │  - Users table (Phase-II)                          │  │
│ └────────────────────────────────────────────────────┘  │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Stateless Backend**: No in-memory conversation state. All state from database.
2. **User Isolation**: All queries and tool calls filtered by user_id from JWT.
3. **MCP-First Tools**: Agent calls MCP tools only; never directly accesses database.
4. **Confirmation Gates**: User confirms before write operations execute.
5. **20-Message Context**: Token window limited to last 20 messages per ADR-005.
6. **Zero Phase-II Changes**: Phase-III extends Phase-II without modifying anything.

## System Components

### 1. Chat Endpoint (to be created)

**Endpoint**: `POST /api/v1/chat/conversations/{conversation_id}/messages`

```python
# Header: Authorization: Bearer {JWT_TOKEN}

# Request body
{
  "message": "Create a task to buy groceries"
}

# Response
{
  "success": true,
  "data": {
    "message": "I'll create a task for you...",
    "tools_executed": ["add_task"],
    "reasoning": "User asked to create a task"
  }
}
```

**Implementation Location**: `backend/src/api/chat.py` (to be created with T316–T327)

### 2. AgentExecutor

**File**: `backend/src/agents/executor.py`

**Responsibility**: Orchestrate multi-turn conversation with OpenAI agents

```python
executor = AgentExecutor()

result = await executor.execute(
    user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
    user_message="Create a task",
    conversation_history=[
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"},
    ],
)

# Returns:
{
    "success": True,
    "response": "I'll create that task...",
    "tool_calls": ["add_task"],
    "reasoning": "...",
}
```

### 3. MCP Tools

**File**: `backend/src/mcp/tools.py` (already implemented in T307–T315)

Available tools:
- `add_task(user_id, title, description?, priority?, due_date?, tags?)`
- `list_tasks(user_id, status?, priority?, overdue?)`
- `update_task(user_id, task_id, title?, description?, priority?, due_date?, tags?)`
- `complete_task(user_id, task_id)`
- `delete_task(user_id, task_id)`

### 4. Conversation Models

**Files**:
- `backend/src/models/conversation.py` - Conversation entity
- `backend/src/models/message.py` - Message entity

```python
# Schema
conversations
├── id (UUID PK)
├── user_id (FK to users)
├── title (optional)
├── description (optional)
├── deleted_at (soft delete)
├── created_at
└── updated_at

messages
├── id (UUID PK)
├── conversation_id (FK)
├── user_id (FK)
├── role (user | assistant | system)
├── content (text)
├── metadata (JSON, optional)
├── created_at
└── updated_at
```

### 5. Conversation Service

**File**: `backend/src/services/conversation_service.py`

**Functions**:
- `ConversationService.create_conversation()` - Create new conversation
- `ConversationService.get_conversation()` - Retrieve with user isolation
- `ConversationService.list_conversations()` - Paginated user conversations
- `MessageService.add_message()` - Store message in database
- `MessageService.get_conversation_messages()` - Retrieve with pagination
- `MessageService.get_conversation_messages_as_dicts()` - For agent context

## Message Flow

### Complete User Message → Response Flow

```
1. User sends message via frontend chat widget
   POST /api/v1/chat/conversations/{conversation_id}/messages
   Authorization: Bearer {JWT}
   Body: {"message": "Create a task to buy groceries"}

2. Backend extracts user_id from JWT

3. Load conversation history from DB
   SELECT * FROM messages
   WHERE conversation_id = ? AND user_id = ?
   ORDER BY created_at ASC
   LIMIT 100

4. Store user message in database
   INSERT INTO messages (conversation_id, user_id, role, content)
   VALUES (?, ?, 'user', 'Create a task...')

5. Call AgentExecutor.execute()
   - Format last 20 messages for OpenAI API
   - Include system prompt
   - Call OpenAI Agents API

6. OpenAI responds:
   - "I'll help you create that. What's the title?"  (no tools)
   OR
   - Tool call: add_task({title: "Buy groceries", ...})

7. If tool calls needed:
   a. For each tool_call:
      - ToolInvocationBridge.invoke_tool()
      - Validate user_id from JWT
      - Execute MCP tool
      - Get result
      - Feed to agent for continued reasoning
   b. Repeat until agent outputs final response

8. Store assistant response in database
   INSERT INTO messages (conversation_id, user_id, role, content)
   VALUES (?, ?, 'assistant', 'Task created...')

9. Return response to frontend
   {
     "success": true,
     "data": {
       "message": "Task created successfully!",
       "tools_executed": ["add_task"],
       "reasoning": "..."
     }
   }

10. Frontend displays message and updates UI
    (UI syncs with Phase-II task list automatically)
```

### Multi-Turn Conversation Example

```
Turn 1:
User: "Create a task"
Agent: "What's the task title?"

Turn 2:
User: "Buy groceries"
Agent: "Got it. Priority: medium (default). Confirm? (yes/no)"

Turn 3:
User: "Yes"
Agent: [invokes add_task tool]
Agent: "Task 'Buy groceries' created successfully!"

Turn 4:
User: "List my tasks"
Agent: [invokes list_tasks tool]
Agent: "You have 1 task: Buy groceries (medium priority)"
```

## Configuration

### Environment Variables

Create `.env` file (or set in production):

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-...  # Get from https://platform.openai.com/api-keys
OPENAI_MODEL=gpt-4-turbo-preview  # Recommended for multi-turn reasoning

# Agent Configuration
AGENT_TIMEOUT=10  # Seconds; agent execution timeout
AGENT_MAX_MESSAGES=20  # Context window size per ADR-005

# Other (Phase-II)
DATABASE_URL=postgresql://...
JWT_SECRET=...
BETTER_AUTH_SECRET=...
```

### Settings Class

See `backend/src/config.py`:

```python
class Settings(BaseSettings):
    openai_api_key: str        # Required
    openai_model: str = "gpt-4-turbo-preview"
    agent_timeout: int = 10
    agent_max_messages: int = 20
    # ... other settings
```

## API Contracts

### Chat Message Endpoint

**Endpoint**: `POST /api/v1/chat/conversations/{conversation_id}/messages`

**Authentication**: JWT token required

**Request**:
```json
{
  "message": "Create a task to buy groceries"
}
```

**Response (Success)**:
```json
{
  "success": true,
  "data": {
    "id": "message-uuid",
    "conversation_id": "conv-uuid",
    "message": "I'll create that task for you. Title: Buy groceries. Priority: medium. Confirm?",
    "tools_executed": [],
    "reasoning": "User asked to create a task; I need clarification on priority."
  }
}
```

**Response (After Confirmation)**:
```json
{
  "success": true,
  "data": {
    "id": "message-uuid-2",
    "conversation_id": "conv-uuid",
    "message": "Task 'Buy groceries' created successfully!",
    "tools_executed": ["add_task"],
    "reasoning": "User confirmed; I invoked add_task tool."
  }
}
```

**Response (Error)**:
```json
{
  "success": false,
  "error": {
    "code": "AGENT_TIMEOUT",
    "message": "I'm taking longer than expected. Please try again."
  }
}
```

## Testing Guide

### Unit Tests

Run all agent tests:

```bash
cd backend

# All tests
pytest tests/unit/test_agents_*.py -v

# Specific test
pytest tests/unit/test_agents_executor.py::TestAgentExecutor::test_execute_with_empty_message_raises_error -v

# With coverage
pytest tests/unit/test_agents_*.py --cov=src/agents --cov-report=term-missing
```

### Integration Tests

Create `backend/tests/integration/test_chat_flow.py`:

```python
@pytest.mark.asyncio
async def test_complete_chat_flow(client, user_id):
    """Test: User sends message → Agent processes → Tool executes → Response returned"""

    # 1. Create conversation
    conv = await ConversationService.create_conversation(db, user_id)

    # 2. Send message
    result = await executor.execute(
        user_id=user_id,
        user_message="Create a task to buy groceries",
        conversation_history=[],
    )

    # 3. Verify response
    assert result["success"]
    assert "groceries" in result["response"].lower()

    # 4. Check tool was called
    if "add_task" in result["tool_calls"]:
        # Verify task was created in database
        tasks = await task_service.get_user_tasks(user_id)
        assert any(t.title == "Buy groceries" for t in tasks)
```

### Manual Testing

1. **Start backend**:
   ```bash
   cd backend
   uvicorn src.main:app --reload
   ```

2. **Test with curl**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/chat/conversations/{conv_id}/messages \
     -H "Authorization: Bearer {JWT_TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{"message": "Create a task"}'
   ```

3. **Check logs**:
   ```bash
   # Watch for agent execution logs
   tail -f logs/app.log | grep "AgentExecutor"
   ```

## Deployment

### Prerequisites

- OpenAI API key with access to Agents SDK
- Python 3.10+
- PostgreSQL 12+ (Neon serverless)
- FastAPI backend running
- Frontend deployed with chat widget

### Steps

1. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export OPENAI_API_KEY=sk-...
   export OPENAI_MODEL=gpt-4-turbo-preview
   export AGENT_TIMEOUT=10
   export AGENT_MAX_MESSAGES=20
   ```

3. **Run migrations** (for conversations/messages tables):
   ```bash
   cd backend
   alembic upgrade head
   ```

4. **Start backend**:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```

5. **Monitor**:
   ```bash
   # Check logs
   tail -f /var/log/app.log

   # Monitor errors
   grep ERROR /var/log/app.log | tail -20

   # Check OpenAI API usage
   # https://platform.openai.com/account/usage/overview
   ```

## Troubleshooting

### Agent Timeout (>10 seconds)

**Symptom**: User sees "I'm taking longer than expected..."

**Causes**:
1. OpenAI API slow response
2. MCP tool slow execution
3. Network latency
4. Too many tool calls in agentic loop

**Solutions**:
1. Increase `AGENT_TIMEOUT` (default 10s)
2. Check OpenAI API status: https://status.openai.com/
3. Optimize MCP tool performance
4. Check network latency: `ping api.openai.com`

### Cross-User Access Attempt

**Symptom**: User gets "user_id_mismatch" error

**Cause**: Tool call tried to use different user_id than JWT

**Solutions**:
1. Verify JWT token is valid
2. Check user_id extraction in middleware
3. Review tool bridge validation logic
4. Check logs for "Cross-user access attempt"

### Agent Not Calling Tools

**Symptom**: Agent responds but doesn't invoke tools

**Cause**: Agent doesn't think tools are needed

**Solutions**:
1. Review system prompt in `system_prompt.py`
2. Check tool definitions are registered
3. Verify MCP tools are accessible
4. Try explicit user confirmation ("yes" after agent asks)

### Database Query Timeout

**Symptom**: Messages load slowly from database

**Cause**: Missing indexes or too many messages

**Solutions**:
1. Verify indexes exist on (user_id, created_at)
2. Limit query to last 100 messages
3. Archive old conversations
4. Check database connection pool

### OpenAI API Rate Limit

**Symptom**: "Too many requests" error

**Cause**: Exceeded OpenAI API rate limits

**Solutions**:
1. Implement exponential backoff (built in)
2. Check rate limit plan on https://platform.openai.com/account/rate-limits
3. Queue requests if needed
4. Monitor usage: https://platform.openai.com/account/usage/overview

## References

- OpenAI Agents SDK: https://platform.openai.com/docs/api-reference/agents
- Phase-III Spec: `specs/004-ai-chatbot/spec.md`
- Phase-III Plan: `specs/004-ai-chatbot/plan.md`
- Architecture: `specs/004-ai-chatbot/ARCHITECTURE.md`
- Agent Module: `backend/src/agents/README.md`
- MCP Tools: `backend/src/mcp/`
