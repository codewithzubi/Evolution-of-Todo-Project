# OpenAI Agents SDK Integration

**Phase-III AI Chatbot Integration Module**

[Task]: T316–T327, [From]: specs/004-ai-chatbot/spec.md

This module integrates OpenAI Agents SDK with MCP tools to enable conversational task management via AI chatbot.

## Architecture Overview

```
User Message (from frontend)
    ↓
JWT Token Extraction (user_id)
    ↓
AgentExecutor
    ├─ Format conversation history (last 20 messages)
    ├─ Call OpenAI Agents API
    ├─ Parse response (text + tool calls)
    └─ Tool invocation loop (if tools needed)
        ├─ Extract tool call parameters
        ├─ ToolInvocationBridge
        │  └─ Invoke MCP tool (with user_id scoping)
        └─ Feed result back to agent
    ↓
Response Formatting
    ├─ response_text: Natural language response
    ├─ tool_calls: List of tools executed
    └─ reasoning: Agent's reasoning trace
    ↓
Store in database + Return to frontend
```

## Key Components

### 1. **AgentExecutor** (`executor.py`)

Orchestrates multi-turn conversation with OpenAI agents.

```python
executor = AgentExecutor(
    api_key="sk-...",
    model="gpt-4-turbo-preview",
    timeout=10,
    max_messages=20,
)

result = await executor.execute(
    user_id=uuid4(),
    user_message="Create a task to buy groceries",
    conversation_history=[...],  # From database
)
```

**Features:**
- Stateless design (no in-memory state)
- Automatic message history truncation (20-message window)
- Agentic loop with tool calling support
- Timeout handling (10s default)
- Rate limit and error recovery

**Execution Flow:**
1. Build message array from conversation history
2. Call OpenAI Agents API with available tools
3. Parse response (text + tool calls)
4. If tools needed: execute via ToolInvocationBridge
5. Feed results back to agent for continued reasoning
6. Repeat until agent outputs final response

### 2. **ToolInvocationBridge** (`tool_bridge.py`)

Bridges OpenAI tool calls to MCP tool execution.

```python
result = await ToolInvocationBridge.invoke_tool(
    tool_name="add_task",
    tool_params={"title": "Buy groceries"},
    user_id=jwt_user_id,  # From JWT token
)
```

**Features:**
- User ID injection from JWT (prevents cross-user access)
- Tool parameter validation
- MCP tool execution delegation
- Natural language formatting of results for agent

**Security:**
- Validates user_id matches JWT user
- Returns 403 if cross-user access attempted
- All tool operations scoped by user_id

### 3. **ConversationContextManager** (`context_manager.py`)

Manages message history and context windowing.

```python
manager = ConversationContextManager(max_messages=20)

# Truncate to last 20 messages for agent context
messages = manager.format_messages_for_agent(history)

# Get summary for logging
summary = manager.get_message_summary(history)
```

**Features:**
- Automatic truncation to context window (20 messages)
- Converts database messages to OpenAI API format
- Filters empty messages
- Token estimate calculation
- Role-based message counting

### 4. **ResponseParser** (`response_parser.py`)

Parses OpenAI agent responses and tool calls.

```python
parser = ResponseParser()

text, tool_calls, reasoning = parser.parse_agent_response(
    openai_response
)

# Format for frontend
formatted = parser.format_response_for_frontend(
    response_text=text,
    tool_calls=tool_calls,
    reasoning=reasoning,
)
```

**Features:**
- Handles OpenAI message objects and dictionaries
- Extracts tool calls with parameter parsing
- Recovers from invalid JSON in arguments
- Formats responses for frontend consumption
- Error response formatting with codes

### 5. **System Prompt** (`system_prompt.py`)

Defines agent behavior and safety guidelines.

```python
from src.agents.system_prompt import SYSTEM_PROMPT

# Includes:
# - Step-by-step data collection instructions
# - Confirmation gate requirements
# - Tool usage guidelines
# - Safety rules (no auto-execution, etc.)
# - Task management domain knowledge
```

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional (defaults shown)
OPENAI_MODEL=gpt-4-turbo-preview
AGENT_TIMEOUT=10              # seconds
AGENT_MAX_MESSAGES=20         # context window
```

### Settings

All configuration loaded via `src/config.py`:

```python
from src.config import settings

settings.openai_api_key      # API key
settings.openai_model         # Model name
settings.agent_timeout        # Timeout in seconds
settings.agent_max_messages   # Context window size
```

## Usage Example

```python
from src.agents.executor import AgentExecutor
from src.services.conversation_service import MessageService, ConversationService
from uuid import uuid4

# Initialize
executor = AgentExecutor()

# Get conversation history from database
conversation_id = uuid4()
user_id = uuid4()

db = get_session()
messages, total = await MessageService.get_conversation_messages(
    db=db,
    user_id=user_id,
    conversation_id=conversation_id,
    limit=100,  # Fetch up to 100; executor will truncate to 20
)

messages_as_dicts = [
    {"role": msg.role, "content": msg.content}
    for msg in messages
]

# Execute agent
result = await executor.execute(
    user_id=user_id,
    user_message="Create a task to buy groceries",
    conversation_history=messages_as_dicts,
)

# Store response
if result["success"]:
    await MessageService.add_message(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content=result["response"],
        metadata={
            "tool_calls": result["tool_calls"],
            "reasoning": result.get("reasoning"),
        },
    )
```

## Testing

### Unit Tests

Run tests with pytest:

```bash
# All agent tests
pytest backend/tests/unit/test_agents_*.py

# Specific test class
pytest backend/tests/unit/test_agents_executor.py::TestAgentExecutor

# With coverage
pytest --cov=backend/src/agents backend/tests/unit/test_agents_*.py
```

### Test Files

- `test_agents_executor.py` - AgentExecutor tests (10+ tests)
- `test_tool_bridge.py` - ToolInvocationBridge tests (10+ tests)
- `test_context_manager.py` - ConversationContextManager tests (5+ tests)
- `test_response_parser.py` - ResponseParser tests (5+ tests)

### Coverage Target

Minimum **70% line coverage** across all agent modules.

## Error Handling

### Agent Execution Errors

| Error Code | Cause | Recovery |
|-----------|-------|----------|
| `AGENT_TIMEOUT` | API took >10 seconds | Retry after delay |
| `RATE_LIMIT_ERROR` | OpenAI 429 response | Exponential backoff |
| `VALIDATION_ERROR` | Invalid parameters | Check input format |
| `INTERNAL_ERROR` | Unexpected exception | Log and retry |

### Tool Invocation Errors

| Error | Cause | Response |
|-------|-------|----------|
| `user_id_mismatch` | Cross-user access attempt | 403 Forbidden |
| `tool_validation_error` | Invalid tool parameters | Return friendly message |
| `tool_execution_error` | MCP tool failed | Return error + recovery suggestion |

### Example Error Response

```json
{
  "success": false,
  "response": "I'm taking longer than expected. Please try again in a moment.",
  "error": "agent_timeout",
  "error_code": "AGENT_TIMEOUT",
  "tool_calls": []
}
```

## Performance Considerations

### Context Window Limit

- **Message Limit**: 20 messages per ADR-005
- **Token Estimate**: ~2-3K tokens for typical conversation
- **Reasoning**: Keeps API calls fast and costs reasonable

### Agent Timeout

- **Default**: 10 seconds
- **Includes**: API call + tool execution + reasoning
- **Fallback**: Return "AI is thinking..." message

### Database Queries

- **Conversation Retrieval**: `O(1)` with user_id + conversation_id indexes
- **Message Retrieval**: `O(log n)` with (conversation_id, created_at) index
- **Typical Latency**: <200ms for 100-message conversation

## Security & User Isolation

### JWT Token Extraction

```python
# In FastAPI middleware/dependency
user_id = jwt.decode(token, settings.jwt_secret)["user_id"]

# Passed to executor
result = await executor.execute(
    user_id=user_id,  # From JWT
    user_message=message,
    conversation_history=history,
)
```

### User Scoping

- **All tool calls**: Include user_id from JWT
- **All queries**: Filter by user_id (`WHERE user_id = :user_id`)
- **Cross-user access**: Returns 403 Forbidden (not 404)

### No Hardcoded Secrets

- API key in `.env` or environment variable
- Never logged or transmitted in plain text
- Rotated regularly in production

## Logging

### Log Levels

```python
import logging

logger = logging.getLogger("src.agents")

# Info: Agent execution start/end, tool calls
logger.info(f"Executing agent for user {user_id}")

# Debug: Message formatting, parameter validation
logger.debug(f"Formatted {len(messages)} messages for agent")

# Warning: Cross-user attempts, rate limits, truncation
logger.warning(f"Conversation truncated from {total} to {window} messages")

# Error: API failures, validation errors, exceptions
logger.error(f"Agent execution failed: {e}", exc_info=True)
```

### Correlation IDs

For distributed tracing:

```python
correlation_id = request.headers.get("X-Correlation-ID", uuid4())
logger.info(f"Agent execution [correlation_id={correlation_id}]")
```

## Future Enhancements

- [ ] Message summarization for very long conversations
- [ ] Fine-tuned models for task management domain
- [ ] Multi-language support via system prompt customization
- [ ] Streaming responses for better UX
- [ ] Conversation branching/forking
- [ ] User preferences in system prompt

## References

- OpenAI Agents SDK: https://platform.openai.com/docs/api-reference/agents
- MCP Server: `backend/src/mcp/`
- Conversation Models: `backend/src/models/conversation.py`, `message.py`
- System Prompt: `system_prompt.py`
