# OpenAI Agents SDK - 5-Minute Quick Start

**Phase-III AI Chatbot - Get Up and Running**

[Task]: T327, [From]: specs/004-ai-chatbot/spec.md

## Prerequisites

- ✅ Python 3.10+
- ✅ OpenAI API key: https://platform.openai.com/api-keys
- ✅ Backend running (FastAPI on :8000)
- ✅ Database migrations done (`alembic upgrade head`)

## Step 1: Install OpenAI Package (1 min)

```bash
cd backend

# Add to requirements.txt (already done in T316)
# openai==1.6.1

# Install
pip install -r requirements.txt
```

## Step 2: Configure Environment Variables (1 min)

Create or update `.env`:

```bash
# Copy from .env.example
cp .env.example .env

# Edit and add OpenAI key
cat >> .env << EOF

# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
AGENT_TIMEOUT=10
AGENT_MAX_MESSAGES=20
EOF
```

## Step 3: Create Conversation Models (1 min)

Models are already created in T325:

- `backend/src/models/conversation.py` ✅
- `backend/src/models/message.py` ✅

Run database migration:

```bash
cd backend
alembic upgrade head
```

## Step 4: Test Agent Executor (1 min)

```bash
cd backend

# Run test
python -m pytest tests/unit/test_agents_executor.py::TestAgentExecutor::test_agent_executor_initialization -v

# Expected output:
# test_agent_executor_initialization PASSED
```

## Step 5: Test Complete Chat Flow (1 min)

Create test script `test_chat_flow.py`:

```python
import asyncio
from uuid import uuid4
from src.agents.executor import AgentExecutor
from src.agents.context_manager import ConversationContextManager

async def test():
    # Initialize executor
    executor = AgentExecutor()

    # Test message
    user_id = uuid4()
    result = await executor.execute(
        user_id=user_id,
        user_message="Hi, can you help me create a task?",
        conversation_history=[],
    )

    print("✅ Agent Response:")
    print(f"  Message: {result['response']}")
    print(f"  Success: {result['success']}")
    print(f"  Tools: {result.get('tool_calls', [])}")

asyncio.run(test())
```

Run it:

```bash
cd backend
python test_chat_flow.py

# Expected output:
# ✅ Agent Response:
#   Message: I'd be happy to help you create a task! What would you like to name it?
#   Success: True
#   Tools: []
```

## Testing Checklist

After completing setup:

- [ ] `OPENAI_API_KEY` is set (test with `echo $OPENAI_API_KEY`)
- [ ] `pip install openai==1.6.1` succeeds
- [ ] `pytest tests/unit/test_agents_*.py` passes (70%+ coverage)
- [ ] Agent executor initializes without errors
- [ ] Test conversation returns success response
- [ ] Tool bridge can invoke MCP tools
- [ ] User isolation prevents cross-user access (403 error)

## Running Unit Tests

```bash
cd backend

# All agent tests
pytest tests/unit/test_agents_*.py -v

# With coverage
pytest tests/unit/test_agents_*.py --cov=src/agents --cov-report=html

# Check coverage
open htmlcov/index.html
```

## Next Steps

1. **Create Chat Endpoint** (`backend/src/api/chat.py`)
   - POST /api/v1/chat/conversations/{id}/messages
   - Extract user_id from JWT
   - Load conversation history
   - Call AgentExecutor.execute()
   - Store response in database

2. **Create Chat Widget** (Frontend)
   - Floating chat bubble (bottom-right)
   - Sends messages to chat endpoint
   - Displays agent responses
   - Shows tool execution status

3. **Integration Testing**
   - Test complete message flow
   - Verify task creation via chatbot
   - Confirm conversation persistence
   - Test user isolation (cross-user access denied)

## Troubleshooting

### Import Error: "No module named 'openai'"

```bash
pip install openai==1.6.1
```

### Error: "OPENAI_API_KEY not configured"

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# If empty, add to .env
export OPENAI_API_KEY=sk-...
```

### Agent Executor Timeout

```python
# Increase timeout if needed
executor = AgentExecutor(timeout=20)  # 20 seconds
```

### Tool Invocation Fails

Check MCP tools are working:

```bash
# Test MCP tool directly
pytest tests/unit/test_mcp_tools.py -v
```

## Architecture Recap

```
User Message → Chat Endpoint → AgentExecutor → OpenAI API
                                    ↓
                            ToolInvocationBridge
                                    ↓
                              MCP Tools (5 functions)
                                    ↓
                            Phase-II Task APIs
```

## Key Files

| File | Purpose |
|------|---------|
| `src/agents/executor.py` | Main agent orchestrator |
| `src/agents/tool_bridge.py` | MCP tool invocation |
| `src/agents/context_manager.py` | Message history management |
| `src/agents/response_parser.py` | Parse OpenAI responses |
| `src/agents/system_prompt.py` | Agent behavior definition |
| `src/services/conversation_service.py` | Database persistence |
| `src/models/conversation.py` | Conversation entity |
| `src/models/message.py` | Message entity |

## Resources

- **OpenAI Docs**: https://platform.openai.com/docs/api-reference/agents
- **Phase-III Spec**: `specs/004-ai-chatbot/spec.md`
- **Full Integration Guide**: `docs/AGENTS_SDK_INTEGRATION.md`
- **Agent Module README**: `backend/src/agents/README.md`

## Support

If you encounter issues:

1. Check logs: `grep ERROR logs/app.log`
2. Review configuration: `echo $OPENAI_API_KEY`
3. Run tests: `pytest tests/unit/test_agents_*.py -v`
4. Check OpenAI status: https://status.openai.com/

---

**You're ready to go!** Run the tests and proceed to creating the chat endpoint.
