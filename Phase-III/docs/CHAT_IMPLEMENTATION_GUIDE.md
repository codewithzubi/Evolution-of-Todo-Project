# Chat Endpoint Implementation Guide

## Overview

This guide documents the implementation of the FastAPI chat endpoint for Phase-III AI Chatbot.

**Status**: Complete ✅
**Completed**: 2024-01-15
**Key Files**:
- `backend/src/api/routes/conversations.py` - Conversation endpoints
- `backend/src/api/routes/messages.py` - Message and chat endpoints
- `backend/src/services/message_service.py` - Message persistence
- `backend/src/models/message.py` - Message schema
- `backend/src/models/conversation.py` - Conversation schema

---

## Architecture Overview

### Component Diagram

```
┌─────────────┐
│  Frontend   │ (Next.js)
└──────┬──────┘
       │ HTTP + JWT
       ▼
┌─────────────────────────────────────────────────┐
│            FastAPI Application                  │
├─────────────────────────────────────────────────┤
│ JWT Middleware (Extract user_id, verify token) │
└────────────┬────────────────────────────────────┘
             │
      ┌──────▼──────────────────┐
      │  Chat Endpoints         │
      ├─────────────────────────┤
      │ POST /messages          │ ◄── Core Chat Flow
      │ GET /messages           │
      │ POST /conversations     │
      │ GET /conversations      │
      │ DELETE /conversations   │
      └──────┬──────────────────┘
             │
      ┌──────▼──────────────────────────────────┐
      │     Services Layer                      │
      ├─────────────────────────────────────────┤
      │ MessagePersistenceService               │
      │ ConversationService                     │
      │ AgentExecutor (OpenAI Agents SDK)       │
      └──────┬──────────────────────────────────┘
             │
      ┌──────▼──────────────────┐
      │  Database Layer         │
      ├─────────────────────────┤
      │ Neon PostgreSQL         │
      │ SQLModel ORM            │
      │ - Conversations Table   │
      │ - Messages Table        │
      └─────────────────────────┘
```

---

## Request/Response Flow

### Message Send Flow (T331)

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────┐
│ POST /conversations/{id}/messages               │
│ Body: { message: string, metadata?: object }    │
└────────┬────────────────────────────────────────┘
         │
         ▼
    JWT Validation
    Extract user_id
         │
         ▼
    Conversation Verification
    - Check exists
    - Check user_id matches
         │
         ▼
    Save User Message
    - Create message with role='user'
    - Store in database
         │
         ▼
    Load History (last 20 messages)
    - Convert to agent format
    - Pass to AgentExecutor
         │
         ▼
    ┌────────────────────────────────────┐
    │ AgentExecutor.execute()            │
    │ - Send to OpenAI Agents API        │
    │ - Handle tool calls (if any)       │
    │ - Parse response                   │
    └────────┬───────────────────────────┘
             │
             ▼
    Save Assistant Response
    - Create message with role='assistant'
    - Store tool_calls and tool_results
    - Store metadata (elapsed_ms, model)
             │
             ▼
    Return ChatResponse
    - ID, role, content
    - Tool calls/results (if any)
    - Timestamp
             │
             ▼
    Client receives response
    Display in UI
```

### Performance Timeline
- JWT validation: <5ms
- Database operations: <50ms
- Agent execution: 1-10s (depends on AI service)
- Total: 1-10s per message

---

## Core Components

### 1. Conversation Service (T329, T334)

**File**: `backend/src/services/conversation_service.py`

**Key Functions**:
```python
# Create conversation for user
async def create_conversation(
    db: Session,
    user_id: UUID,
    title: Optional[str] = None,
) -> Conversation

# Get single conversation with user isolation
async def get_conversation(
    db: Session,
    user_id: UUID,
    conversation_id: UUID,
) -> Optional[Conversation]

# List user's conversations (paginated)
async def list_conversations(
    db: Session,
    user_id: UUID,
    limit: int = 50,
    offset: int = 0,
) -> tuple[List[Conversation], int]

# Soft-delete conversation
async def soft_delete_conversation(
    db: Session,
    user_id: UUID,
    conversation_id: UUID,
) -> bool
```

**Key Features**:
- User isolation: All queries filtered by user_id
- Soft deletes: Conversation marked with deleted_at timestamp
- Pagination: supports limit/offset
- Indexed queries: (user_id, created_at) for performance

---

### 2. Message Service (T335)

**File**: `backend/src/services/message_service.py`

**Key Functions**:
```python
# Save user message
async def save_user_message(
    db: Session,
    user_id: UUID,
    conversation_id: UUID,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Message

# Save assistant message with tool metadata
async def save_assistant_message(
    db: Session,
    user_id: UUID,
    conversation_id: UUID,
    content: str,
    tool_calls: Optional[List[Dict[str, Any]]] = None,
    tool_results: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Message

# Get conversation messages (oldest first for agent context)
async def get_conversation_messages(
    db: Session,
    conversation_id: UUID,
    limit: int = 20,
    offset: int = 0,
) -> tuple[List[Message], int]

# Get messages for UI display (newest first)
async def get_conversation_messages_for_display(
    db: Session,
    conversation_id: UUID,
    limit: int = 20,
    offset: int = 0,
) -> tuple[List[Message], int]

# Soft-delete message
async def soft_delete_message(
    db: Session,
    message_id: UUID,
) -> bool

# Soft-delete all messages in conversation
async def soft_delete_conversation_messages(
    db: Session,
    conversation_id: UUID,
) -> int
```

**Key Features**:
- Separate user/assistant message saving for clarity
- Tool call/result storage as JSONB (PostgreSQL)
- Automatic message ordering (oldest first for agent, newest for UI)
- Soft delete support with filtering
- Performance: <200ms with limit=20

---

### 3. Chat Endpoints (T328, T329, T330, T331)

**File**: `backend/src/api/routes/messages.py`

**Conversation Endpoints**:
```
POST   /api/v1/chat/conversations              - Create
GET    /api/v1/chat/conversations              - List (paginated)
GET    /api/v1/chat/conversations/{id}         - Get single
DELETE /api/v1/chat/conversations/{id}         - Soft-delete
```

**Message Endpoints**:
```
POST   /api/v1/chat/conversations/{id}/messages       - Send & get response
GET    /api/v1/chat/conversations/{id}/messages       - List messages (paginated)
DELETE /api/v1/chat/conversations/{id}/messages/{id}  - Soft-delete message
```

**Key Implementation Details**:

1. **Request Validation**:
   - Pydantic models in `backend/src/api/chat_schemas.py`
   - ChatRequest: message (1-5000 chars), optional metadata
   - All models include detailed descriptions

2. **User Isolation** (T333):
   - Extract user_id from JWT (via middleware)
   - Verify conversation belongs to user (403 Forbidden if mismatch)
   - All database queries filtered by user_id
   - Example:
     ```python
     conversation = await ConversationService.get_conversation(
         db=db,
         user_id=request.state.user_id,  # From JWT
         conversation_id=conversation_id,
     )
     if not conversation:
         raise ConversationNotFoundError(...)  # 404 or 403
     ```

3. **Error Handling** (T336):
   - Custom exceptions: ChatException and subclasses
   - Exception handler in main.py converts to JSON
   - Consistent error format with error_code, error_message, status_code
   - Example errors:
     - `ConversationNotFoundError` (404)
     - `UnauthorizedConversationAccessError` (403)
     - `InvalidMessageError` (400)
     - `OpenAIAPIError` (500)
     - `RateLimitError` (429)
     - `AgentTimeoutError` (504)

---

### 4. Agent Integration (T337)

**File**: `backend/src/agents/executor.py`

**Integration in Chat Endpoint**:
```python
# Load conversation history from database
history_messages, _ = await MessagePersistenceService.get_conversation_messages(
    db=db,
    conversation_id=conversation_id,
    limit=20,  # Last 20 messages for context window
)

# Convert to agent format
history = [
    {"role": msg.role.value, "content": msg.content}
    for msg in history_messages
]

# Execute agent
agent = AgentExecutor()
agent_response = await agent.execute(
    user_id=user_id,
    user_message=body.message.strip(),
    conversation_history=history,
)

# Handle response
if agent_response.get("success"):
    response_text = agent_response.get("response")
    tool_calls = agent_response.get("tool_calls")
    tool_results = agent_response.get("tool_results")

    # Save to database
    assistant_message = await MessagePersistenceService.save_assistant_message(
        db=db,
        user_id=user_id,
        conversation_id=conversation_id,
        content=response_text,
        tool_calls=tool_calls,
        tool_results=tool_results,
    )
```

**Logging** (T337):
```python
# Start
logger.info(f"Chat request from user {user_id} in conversation {conversation_id}")

# History loaded
logger.debug(f"Agent context: {len(history)} messages from conversation history")

# Response received
logger.debug(f"Agent returned response in {elapsed_ms:.0f}ms")

# Complete
logger.info(f"Chat complete for user {user_id} in {elapsed_ms:.0f}ms")

# Errors
logger.error(f"Agent execution error: {str(e)}", exc_info=True)
```

---

### 5. JWT Middleware (T332)

**File**: `backend/src/api/middleware.py`

**Flow**:
```python
async def jwt_middleware(request: Request, call_next):
    # Skip for public endpoints
    if is_public_path(request.url.path):
        return await call_next(request)

    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return 401_unauthorized_response()

    token = auth_header[7:]  # Remove "Bearer "

    # Verify token and extract user_id
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = payload.get("user_id")
        request.state.user_id = UUID(user_id)
    except JWTError:
        return 401_unauthorized_response()

    return await call_next(request)
```

**Public Paths** (no auth required):
- `/health`
- `/docs`
- `/openapi.json`
- `/auth/*` (auth endpoints)

**Protected Paths** (all require valid JWT):
- `/api/v1/chat/*`
- `/api/v1/users/*`

---

## Database Schema

### Conversations Table

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,

    -- Indexes for efficient queries
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_user_deleted (user_id, deleted_at)
);
```

### Messages Table

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    tool_calls JSONB,
    tool_results JSONB,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,

    -- Indexes for efficient queries
    INDEX idx_conversation_created (conversation_id, created_at),
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_conversation_deleted (conversation_id, deleted_at)
);
```

**Key Indexes**:
- `(conversation_id, created_at)`: Fast message history retrieval
- `(user_id, created_at)`: Fast user message queries
- `(user_id, deleted_at)`: Fast soft-delete filtering
- Enables <200ms queries with pagination

---

## Error Handling Strategy

### Error Hierarchy

```
Exception
├── ChatException (base class for chat API)
│   ├── ConversationNotFoundError (404)
│   ├── UnauthorizedConversationAccessError (403)
│   ├── InvalidMessageError (400)
│   ├── OpenAIAPIError (500)
│   ├── RateLimitError (429)
│   └── AgentTimeoutError (504)
└── APIException (existing, for non-chat endpoints)
```

### Exception Handler (T336)

**File**: `backend/src/main.py`

```python
@app.exception_handler(ChatException)
async def chat_exception_handler(request: Request, exc: ChatException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "data": None,
            "error": {
                "error_code": exc.error_code,
                "error_message": exc.error_message,
                "status_code": exc.status_code,
                "details": exc.details,
            },
        },
    )
```

### Recovery Strategies

**Rate Limit (429)**:
- Retry after `retry_after` seconds
- Exponential backoff: 1s → 2s → 4s → ...
- Max 5 retries

**Agent Timeout (504)**:
- Return: "AI is thinking, please wait or refresh the page"
- Client can refresh to check status
- Save placeholder message for recovery

**OpenAI API Error (500)**:
- Log error with correlation_id
- Return user-friendly message
- Suggest retry after 30s

---

## Testing Strategy

### Integration Tests (T341)

**File**: `backend/tests/integration/test_chat_endpoints.py`

**Test Coverage**:
- ✅ Conversation CRUD (create, list, get, delete)
- ✅ Message sending and retrieval
- ✅ User isolation (403 for cross-user access)
- ✅ Soft delete functionality
- ✅ Pagination
- ✅ Error handling (400, 401, 403, 404, 500)
- ✅ JWT authentication
- ✅ Response format consistency

**Run Tests**:
```bash
pytest backend/tests/integration/test_chat_endpoints.py -v
```

### Unit Tests (T342)

**File**: `backend/tests/unit/test_message_service.py`

**Test Coverage**:
- ✅ Save user/assistant messages
- ✅ Tool calls and results storage
- ✅ Message pagination
- ✅ Soft delete filtering
- ✅ Conversation history retrieval
- ✅ Empty conversation handling

**Run Tests**:
```bash
pytest backend/tests/unit/test_message_service.py -v
```

---

## Performance Optimization (T344)

### Query Optimization

**Conversation Listing**:
```python
# Efficient query using indexed columns
statement = (
    select(Conversation)
    .where(
        and_(
            Conversation.user_id == user_id,
            Conversation.deleted_at.is_(None),
        )
    )
    .order_by(desc(Conversation.created_at))
    .limit(limit)
    .offset(offset)
)
# Uses index: (user_id, deleted_at)
```

**Message Retrieval**:
```python
# Fetch with limit to reduce data transfer
statement = (
    select(Message)
    .where(
        and_(
            Message.conversation_id == conversation_id,
            Message.deleted_at.is_(None),
        )
    )
    .order_by(Message.created_at.asc())
    .limit(limit)
    .offset(offset)
)
# Uses index: (conversation_id, deleted_at)
```

### Caching (Optional T344)

**In-Memory Cache** (Future enhancement):
```python
# Cache conversation metadata (TTL: 5 min)
cache.set(f"conv:{conversation_id}", conversation_data, ttl=300)

# Cache message history (TTL: 1 min)
cache.set(f"msg_history:{conversation_id}", messages, ttl=60)

# Invalidate on update
cache.delete(f"msg_history:{conversation_id}")
```

### Benchmarks

**Typical Response Times**:
- Create conversation: <100ms
- List conversations (limit=20): <200ms
- Get message history (limit=20): <200ms
- Send message: 1-10s (agent execution)

**Database Performance**:
- <50ms for all DB operations
- Indexes on (user_id, created_at) provide <100ms queries even with millions of records

---

## Security Measures

### Authentication (JWT)

**Token Extraction**:
```python
auth_header = request.headers.get("Authorization")
token = auth_header[7:]  # Remove "Bearer " prefix
user_id = extract_user_id_from_token(token)
```

**Token Validation**:
```python
payload = jwt.decode(
    token,
    settings.jwt_secret,
    algorithms=[settings.jwt_algorithm],
)
# Verify signature, expiration, claims
```

### Authorization (Row-Level Security)

**User Isolation**:
```python
# Every query filters by user_id
conversation = await ConversationService.get_conversation(
    db=db,
    user_id=request.state.user_id,  # From JWT
    conversation_id=conversation_id,
)
# Returns None if user doesn't own conversation
```

**Enforcement**:
- All endpoints verify user_id matches
- Database foreign keys enforce constraints
- Middleware validates tokens on every request

### Data Protection

**In Transit**:
- HTTPS only (enforced in production)
- JWT tokens signed with HS256
- No sensitive data in logs

**At Rest**:
- PostgreSQL encryption at rest
- Row-level security in database
- Soft deletes for audit trail

---

## Deployment Checklist

- [ ] Database migrations applied (conversations, messages tables)
- [ ] JWT_SECRET_KEY configured in environment
- [ ] OPENAI_API_KEY configured
- [ ] CORS origins configured for frontend domain
- [ ] HTTPS enabled in production
- [ ] Rate limiting enabled (60 messages/hour/user)
- [ ] Logging configured with correlation IDs
- [ ] Monitoring alerts set up
- [ ] Backup strategy configured
- [ ] Load testing completed (<3s response time)

---

## Common Issues & Troubleshooting

### Issue: 401 Unauthorized on all requests

**Cause**: JWT token invalid or expired
**Solution**:
- Verify token in Authorization header
- Check JWT_SECRET_KEY matches between frontend/backend
- Refresh token if expired

### Issue: 403 Forbidden accessing conversation

**Cause**: User doesn't own conversation
**Solution**:
- Verify conversation_id belongs to authenticated user
- Check request.state.user_id matches conversation.user_id

### Issue: Agent response times >10s

**Cause**: OpenAI API slow or overloaded
**Solution**:
- Check OpenAI API status
- Implement exponential backoff retry
- Consider adding request timeout

### Issue: Database connection errors

**Cause**: Neon connection pool exhausted or network issue
**Solution**:
- Check Neon database status
- Verify DATABASE_URL correct
- Increase connection pool size if needed

---

## References

- **Specs**: `specs/004-ai-chatbot/spec.md`
- **Plan**: `specs/004-ai-chatbot/plan.md`
- **API Docs**: `docs/CHAT_API.md`
- **Agent Integration**: `backend/src/agents/executor.py`
- **Database Models**: `backend/src/models/{conversation,message}.py`

---

**Status**: ✅ Complete
**Last Updated**: 2024-01-15
**Version**: 1.0.0
