# OpenAI Agents Integration

## Purpose
Integrate OpenAI Agents SDK into the FastAPI backend to orchestrate AI agent workflows, manage message history, execute tool calls via MCP, and handle dynamic agent reasoning.

## Key Principles
- **Agent-Driven**: Use OpenAI Agents SDK to handle reasoning, planning, and tool orchestration
- **Message History**: Build chronological message array from database to provide full context
- **MCP Tool Integration**: Agents call tools defined in MCP server; backend executes and returns results
- **Tool Response Parsing**: Parse tool outputs and feed back to agent for continued reasoning
- **Agentic Loop**: Support multi-turn agent interactions with tool use until completion

## Core Responsibilities

### 1. OpenAI Agents SDK Setup
- Initialize OpenAI Agents client with API key from environment
- Configure model (use latest available, e.g., `gpt-4-turbo` or `gpt-4o`)
- Define agent instructions/system prompt for task management context
- Set up tool definitions that match MCP server tools (add, list, update, complete, delete)

### 2. Message History Management
- Query database for all messages in conversation (ordered by `created_at`)
- Transform DB messages into OpenAI message format:
  ```python
  [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    ...
  ]
  ```
- Include all previous turns (agent responses, tool calls, tool results)
- Maintain chronological order for consistent context

### 3. Tool Definition & Binding
Define all task tools for agent to call:
- **add_task**: Create task with title, description, priority
- **list_tasks**: Get user's tasks with optional filtering/pagination
- **update_task**: Modify task details
- **complete_task**: Mark task as completed
- **delete_task**: Remove/soft-delete task

Each tool definition includes:
- Name, description, parameters schema
- Input validation (required fields, types)
- Proper error messages

### 4. Agent Execution Loop
1. Build message array from DB history
2. Add user's new message to array
3. Call OpenAI Agents API with message array + tools
4. Agent responds with either:
   - **Final text response** → Store in DB and return to user
   - **Tool call request** → Execute tool, append result, continue loop
5. Repeat until agent produces final response (no more tool calls)
6. Store final assistant message in database

### 5. Tool Call Handling
When agent requests tool execution:
1. Extract tool name and parameters from agent response
2. Validate parameters against tool schema
3. Execute tool via MCP server (or local handler):
   - `add_task(title, description, priority)` → returns task_id
   - `list_tasks(filters, limit, offset)` → returns task list
   - `update_task(task_id, **updates)` → returns updated task
   - `complete_task(task_id)` → returns completed task
   - `delete_task(task_id)` → returns deletion confirmation
4. Format result as message: `{"role": "tool", "content": "..."}`
5. Append to message array
6. Continue agent loop

### 6. Error Handling
- Catch OpenAI API errors (rate limits, invalid requests)
- Catch tool execution errors (invalid parameters, not found)
- Return meaningful error messages to agent and user
- Log errors with correlation ID for debugging
- Graceful degradation: return error message instead of crashing

### 7. User Context Isolation
- Pass `user_id` to all tool calls (from JWT token)
- Tools enforce user ownership (no cross-user access)
- Agent operates only on authenticated user's data
- Store all messages with user_id in database

## Implementation Workflow

1. **Setup OpenAI Agents SDK**
   - Install: `pip install openai`
   - Import: `from openai import OpenAI` (or agents client)
   - Initialize with API key: `client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))`
   - Create agent with instructions and tool definitions

2. **Define Tool Schemas**
   - Create tool definitions matching MCP tools
   - Include name, description, and parameter schema (JSON schema)
   - Each tool receives user_id for context

3. **Implement Message Array Builder**
   ```python
   async def build_message_array(conversation_id: str, user_id: str) -> list:
       messages = await db.query(Message).filter(
           Message.conversation_id == conversation_id,
           Message.user_id == user_id
       ).order_by(Message.created_at).all()

       return [
           {"role": msg.role, "content": msg.content}
           for msg in messages
       ]
   ```

4. **Implement Agent Execution Loop**
   ```python
   async def run_agent(conversation_id: str, user_id: str, user_message: str):
       # Build history
       messages = await build_message_array(conversation_id, user_id)
       messages.append({"role": "user", "content": user_message})

       # Agent loop
       while True:
           response = client.chat.completions.create(
               model="gpt-4-turbo",
               messages=messages,
               tools=tool_definitions,
               tool_choice="auto"
           )

           if response.stop_reason == "end_turn":
               # Agent finished reasoning
               final_content = response.choices[0].message.content
               await store_message(conversation_id, user_id, "assistant", final_content)
               return final_content

           elif response.stop_reason == "tool_calls":
               # Execute tools
               for tool_call in response.tool_calls:
                   result = await execute_tool(tool_call.function.name,
                                             tool_call.function.arguments,
                                             user_id)
                   messages.append({
                       "role": "tool",
                       "content": json.dumps(result),
                       "tool_call_id": tool_call.id
                   })
   ```

5. **Wire into Chat Endpoint**
   - Accept user message in POST request
   - Store user message in DB
   - Run agent with MCP tools
   - Return assistant response to client
   - Database persists entire conversation

6. **Testing & Validation**
   - Test agent reasoning with simple messages
   - Test tool calling: verify agent invokes tools correctly
   - Test tool response parsing: verify results feed back to agent
   - Test multi-turn conversations: agent uses prior context
   - Test user isolation: agent only accesses user's tasks
   - Test error cases: invalid tool calls, missing parameters

## Success Criteria
✅ OpenAI Agents SDK initializes with API key
✅ Message array built correctly from database history
✅ Agent receives full conversation context
✅ Tool definitions match MCP tools
✅ Agent can call tools and receive results
✅ Agent loop continues until final response
✅ Tool call parameters are validated
✅ User context (user_id) enforced in all tools
✅ Final response stored in database
✅ Multi-turn conversations work correctly
✅ Error handling is graceful
✅ No data leakage between users

## Related Components
- **OpenAI API**: Provides agent reasoning via `gpt-4-turbo` or equivalent
- **MCP Server**: Defines tools that agent can invoke
- **FastAPI Backend**: Orchestrates agent execution
- **Neon Database**: Stores messages and conversation history
- **JWT Auth**: Provides user context for tool calls

## Configuration
Required environment variables:
- `OPENAI_API_KEY`: OpenAI API key for agent access
- `OPENAI_MODEL`: Model to use (default: `gpt-4-turbo`)
- `DATABASE_URL`: Neon PostgreSQL connection string
- `JWT_SECRET`: Secret for token validation

## Agent Instructions Example
```
You are a helpful task management assistant. You help users create, list, update, and manage tasks.

When a user asks to:
- Create a task: use add_task tool
- View tasks: use list_tasks tool
- Update task: use update_task tool
- Complete task: use complete_task tool
- Delete task: use delete_task tool

Always confirm actions with the user. Be concise and helpful.
```

## Performance Notes
- Message array grows with conversation length (consider pagination for very long conversations)
- Each agent call costs tokens; monitor usage
- Tool execution latency affects total response time
- Consider streaming responses for better UX
- Cache tool definitions to avoid re-parsing on each request
