# Research Findings: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Date**: 2026-02-11
**Purpose**: Resolve technical unknowns and establish implementation patterns for Phase-III

## 1. OpenAI Agents SDK Integration

### Best Practices for FastAPI Integration

**Decision**: Use async FastAPI endpoints with OpenAI Agents SDK

**Findings**:
- OpenAI Agents SDK supports async/await patterns natively
- FastAPI async endpoints prevent blocking during AI service calls
- Use dependency injection for agent initialization
- Agent instance can be shared across requests (stateless)

**Implementation Pattern**:
```python
from openai import AsyncOpenAI
from fastapi import Depends

async def get_openai_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    client: AsyncOpenAI = Depends(get_openai_client),
    current_user: User = Depends(get_current_user)
):
    # Use client for agent calls
    pass
```

### Agent Configuration for Tool Calling

**Decision**: Configure agent with system prompt and MCP tools

**Findings**:
- Agent requires system prompt defining its role and capabilities
- Tools registered via MCP SDK tool definitions
- Agent automatically selects appropriate tools based on user intent
- Tool results returned to agent for response generation

**Configuration**:
```python
system_prompt = """
You are a helpful todo management assistant. You can help users:
- Create tasks (add_task)
- View their tasks (list_tasks)
- Mark tasks complete (complete_task)
- Update task details (update_task)
- Delete tasks (delete_task)

Always confirm actions with the user and provide clear, friendly responses.
Stay focused on todo management - politely decline requests outside this scope.
"""
```

### Error Handling Patterns

**Decision**: Implement retry logic with exponential backoff for transient failures

**Findings**:
- OpenAI API can return rate limit errors (429)
- Network timeouts should be handled gracefully
- Tool execution errors should be surfaced to agent
- User messages should always be saved before AI call

**Error Handling Strategy**:
- Retry on 429 (rate limit) with exponential backoff (max 3 retries)
- Timeout after 5 seconds per constitutional constraint
- Catch tool execution errors and return structured error to agent
- Save user message immediately, save assistant response only on success

### Timeout and Retry Strategies

**Decision**: 5-second timeout with 3 retry attempts for rate limits only

**Rationale**:
- Constitutional constraint: 5 seconds max for AI service calls
- Performance goal: <2 seconds response time (p95)
- Retries only for transient failures (rate limits, network errors)
- No retries for validation errors or tool execution failures

## 2. MCP SDK Implementation

### Official MCP SDK Server Setup

**Decision**: Use `mcp` Python package for MCP server implementation

**Findings**:
- Official MCP SDK: `pip install mcp`
- MCP server runs as separate process or embedded in FastAPI
- Tools defined using `@mcp.tool()` decorator
- Server exposes tools via stdio or HTTP transport

**Implementation Approach**:
- Embed MCP server in FastAPI application (not separate process)
- Use HTTP transport for tool communication
- Register tools at application startup
- Tools access database via existing service layer

### Tool Definition Patterns

**Decision**: Use Pydantic models for tool parameters and returns

**Findings**:
- MCP SDK supports Pydantic models for type safety
- Tool parameters validated automatically
- Return types documented in tool schema
- Error handling via exceptions

**Tool Definition Pattern**:
```python
from mcp import MCPServer
from pydantic import BaseModel

class AddTaskParams(BaseModel):
    user_id: str
    title: str
    description: str | None = None
    due_date: str | None = None

@mcp_server.tool()
async def add_task(params: AddTaskParams) -> dict:
    # Validate user_id matches authenticated user
    # Call existing task service
    # Return structured response
    pass
```

### User Context Passing

**Decision**: Pass user_id from JWT to all tool calls

**Findings**:
- Tools receive user_id as explicit parameter
- Agent includes user_id in all tool calls
- Tools validate user_id matches authenticated user
- Prevents cross-user data access

**Security Pattern**:
- Extract user_id from JWT in chat endpoint
- Pass user_id to agent context
- Agent includes user_id in tool parameters
- Tools verify user_id before database operations

### MCP Server Lifecycle Management

**Decision**: Initialize MCP server at FastAPI startup, shutdown at exit

**Implementation**:
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize MCP server
    mcp_server = MCPServer()
    register_tools(mcp_server)
    app.state.mcp_server = mcp_server
    yield
    # Shutdown: Cleanup resources
    await mcp_server.close()

app = FastAPI(lifespan=lifespan)
```

## 3. OpenAI ChatKit Configuration

### ChatKit Integration with Next.js App Router

**Decision**: Use ChatKit as Client Component with TanStack Query for state management

**Findings**:
- ChatKit requires client-side rendering (use 'use client' directive)
- Integrates with TanStack Query for API calls
- Supports custom styling via CSS/Tailwind
- Message history managed by ChatKit internally

**Integration Pattern**:
```typescript
'use client'

import { ChatInterface } from '@openai/chatkit'
import { useMutation, useQuery } from '@tanstack/react-query'

export function ChatComponent() {
  const sendMessage = useMutation({
    mutationFn: (message: string) => apiClient.sendChatMessage(message)
  })

  return <ChatInterface onSendMessage={sendMessage.mutate} />
}
```

### Domain Allowlist Configuration

**Decision**: Configure CORS in FastAPI backend for ChatKit domains

**Findings**:
- ChatKit makes requests from browser to backend API
- CORS must allow frontend domain
- Development: `http://localhost:3000`
- Production: Actual deployment domain

**CORS Configuration**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://app.example.com"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Custom Styling with shadcn/ui

**Decision**: Apply Tailwind classes to ChatKit components for dark mode

**Findings**:
- ChatKit components accept className prop
- Use shadcn/ui color variables for consistency
- Dark mode classes applied via Tailwind
- Lucide Icons for custom buttons

**Styling Approach**:
```typescript
<ChatInterface
  className="bg-background text-foreground border-border"
  messageClassName="bg-card"
  inputClassName="bg-input"
/>
```

### Message History Rendering

**Decision**: Load last 50 messages on chat open, implement "Load More" for older messages

**Findings**:
- ChatKit supports pagination via props
- Initial load: 50 most recent messages
- "Load More" button fetches previous 50 messages
- Messages rendered in chronological order

## 4. Conversation State Management

### Optimal Database Schema

**Decision**: Use existing schema from specs/phase-iii/data-model.md

**Validation**:
- ✅ Conversation table with user_id FK
- ✅ Message table with conversation_id and user_id FKs
- ✅ Indexes on user_id, conversation_id, created_at
- ✅ Composite index (conversation_id, created_at) for efficient retrieval
- ✅ Cascade delete for messages when conversation deleted

**Schema Confirmed**: No changes needed to existing data-model.md

### Pagination Strategies

**Decision**: Offset-based pagination with created_at ordering

**Query Pattern**:
```sql
SELECT * FROM messages
WHERE conversation_id = ?
ORDER BY created_at DESC
LIMIT 50 OFFSET ?
```

**Rationale**:
- Simple to implement
- Efficient with composite index
- Sufficient for MVP (cursor-based pagination for future optimization)

### Indexing Strategies

**Decision**: Use indexes defined in data-model.md

**Indexes**:
1. `idx_conversations_user_id` - Fast user conversation lookup
2. `idx_messages_conversation_id` - Fast message retrieval by conversation
3. `idx_messages_created_at` - Chronological ordering
4. `idx_messages_conversation_created` (composite) - Optimized pagination query

**Performance Impact**: Sub-100ms query time for 50 message retrieval

### Conversation History Pruning

**Decision**: No automatic pruning in v1; manual cleanup for future consideration

**Rationale**:
- Constitutional requirement: indefinite retention in v1
- Monitor storage usage in production
- Future enhancement: archive conversations older than 90 days
- User-initiated deletion supported

## 5. Natural Language Date Parsing

### Date Parsing Library

**Decision**: Use `dateparser` Python library for natural language date parsing

**Installation**: `pip install dateparser`

**Capabilities**:
- Parses relative dates: "tomorrow", "next Friday", "in 2 hours"
- Handles multiple formats: "2026-02-15", "Feb 15", "15/02/2026"
- Timezone support
- Locale support (English only for MVP)

**Usage Example**:
```python
import dateparser

date_str = "tomorrow"
parsed_date = dateparser.parse(date_str, settings={'TIMEZONE': 'UTC'})
# Returns datetime object
```

### Timezone Handling

**Decision**: Use UTC for all stored dates, parse user input as server timezone

**Rationale**:
- Database stores all timestamps in UTC
- Server timezone used as default for parsing
- User timezone support deferred to future enhancement
- Explicit dates (ISO format) parsed as-is

### Ambiguity Resolution

**Decision**: Agent asks clarifying questions for ambiguous dates

**Examples**:
- "next week" → Agent asks "Which day next week?"
- "Monday" → Agent confirms "This coming Monday (Feb 17)?"
- Invalid dates → Agent asks user to specify date

**Implementation**: Agent system prompt includes date clarification instructions

## 6. Performance Optimization

### Caching Strategies

**Decision**: No caching in v1; database queries sufficient for performance goals

**Rationale**:
- Performance goal: <2s response time
- Database queries: <100ms with proper indexes
- AI service call: 1-2s (dominant factor)
- Caching adds complexity without significant benefit for MVP

**Future Consideration**: Redis cache for frequently accessed conversations

### Database Query Optimization

**Decision**: Use composite indexes and limit result sets

**Optimizations**:
1. Composite index (conversation_id, created_at) for message retrieval
2. LIMIT 50 on all message queries
3. Connection pooling (SQLModel default)
4. Async database operations (SQLModel async support)

**Expected Performance**: <100ms for message retrieval queries

### AI Response Streaming

**Decision**: Not implemented in v1; complete response only

**Rationale**:
- Constitutional requirement: complete response only (out of scope)
- Streaming adds frontend complexity
- Performance goal met without streaming
- Future enhancement for better UX

### Rate Limiting

**Decision**: Implement rate limiting at API gateway level (future enhancement)

**Recommendation for v1**:
- No rate limiting in application code
- Monitor usage in production
- Implement if abuse detected

**Future Implementation**: 60 requests per minute per user (per spec)

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| OpenAI Integration | Async FastAPI with dependency injection | Non-blocking I/O, clean architecture |
| MCP Server | Embedded in FastAPI, HTTP transport | Simplified deployment, no separate process |
| Tool Definitions | Pydantic models with user_id validation | Type safety, security enforcement |
| ChatKit Integration | Client Component with TanStack Query | Next.js App Router compatibility |
| CORS Configuration | Allow localhost + production domain | Security, ChatKit compatibility |
| Database Schema | Use existing data-model.md | Already optimal, no changes needed |
| Pagination | Offset-based with 50 message limit | Simple, efficient with indexes |
| Date Parsing | dateparser library with UTC storage | Robust parsing, timezone consistency |
| Caching | No caching in v1 | Unnecessary complexity for MVP |
| Rate Limiting | Deferred to future | Monitor first, implement if needed |

## Unknowns Resolved

✅ **OpenAI API Key Management**: Store in environment variable, rotate via deployment config
✅ **MCP Tool Error Handling**: Return structured error dict to agent, agent generates user-friendly message
✅ **Conversation Context Window**: 50 messages (balances context vs token limits)
✅ **ChatKit Deployment**: Configure CORS for production domain in FastAPI
✅ **Database Migration**: Alembic migration with rollback script, test in staging first

## Next Steps

1. Create API contracts in `contracts/` directory
2. Create quickstart.md for developer onboarding
3. Update agent context (CLAUDE.md) with Phase-III technologies
4. Proceed to `/sp.tasks` for implementation task generation
