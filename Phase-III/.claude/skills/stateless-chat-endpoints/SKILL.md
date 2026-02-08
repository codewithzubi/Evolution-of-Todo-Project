# Stateless Chat Endpoints

## Purpose
Design and implement stateless FastAPI chat endpoints that process user messages independently, fetching full conversation context from the database on each request without maintaining server-side memory.

## Key Principles
- **Stateless Design**: Zero in-memory state; all conversation data comes from database on each request
- **Request Independence**: Every request is self-contained and produces deterministic results
- **Full Context Retrieval**: Fetch complete conversation history + messages for each request
- **Scalability**: Enable horizontal scaling without session affinity or state sharing
- **User Isolation**: Each request validates user ownership of conversation

## Core Responsibilities

### 1. Endpoint Architecture
- `POST /api/v1/conversations/{conversation_id}/messages` - Send message and get response
- `GET /api/v1/conversations/{conversation_id}` - Fetch conversation metadata
- `GET /api/v1/conversations/{conversation_id}/messages` - Fetch message history
- All endpoints require JWT authentication
- All endpoints validate user owns the conversation (403 if not)

### 2. Request Handling (Stateless Flow)
Each request execution:
1. Extract JWT token from `Authorization: Bearer` header
2. Validate token and extract `user_id`
3. Fetch conversation from DB with all messages
4. Process incoming message through AI agent
5. Store AI response in DB
6. Return response to client
7. **Release all state** — no data kept in memory between requests

### 3. Data Fetching from Database
- Query conversations table filtered by `user_id` and `conversation_id`
- Fetch all messages for conversation (consider pagination for large histories)
- Order messages by `created_at` to reconstruct chronological context
- Use efficient queries with proper indexes on `(user_id, conversation_id, created_at)`

### 4. Message Processing
- Accept user message in request body: `{ "content": "user message" }`
- Validate message content (not empty, reasonable length)
- Store user message in messages table
- Pass full conversation history to AI agent/LLM
- Generate AI response based on complete context
- Store AI response in messages table
- Return both messages in response

### 5. Response Format
```json
{
  "data": {
    "conversation_id": "uuid",
    "user_message": {
      "id": "uuid",
      "role": "user",
      "content": "user message",
      "created_at": "2024-01-01T12:00:00Z"
    },
    "assistant_message": {
      "id": "uuid",
      "role": "assistant",
      "content": "ai response",
      "created_at": "2024-01-01T12:00:01Z"
    }
  },
  "error": null
}
```

### 6. No Server-Side Memory
- No caches holding conversation state
- No session objects storing message history
- No WebSocket connections with persistent memory
- No background tasks retaining user context
- Each request is independent and can be processed by any server instance

### 7. Error Handling
- 401: Missing/invalid JWT token
- 403: User doesn't own conversation
- 404: Conversation not found
- 422: Invalid message (empty, too long, invalid format)
- 500: Server error with correlation ID (log in database with request ID)

## Implementation Workflow

1. **Database Schema Design**
   - Conversations table: id, user_id, title, created_at, updated_at
   - Messages table: id, conversation_id, user_id, role (user/assistant), content, created_at
   - Add indexes: (user_id, conversation_id), (conversation_id, created_at)

2. **Create FastAPI Endpoints**
   - `POST /api/v1/conversations` - Create new conversation
   - `GET /api/v1/conversations` - List user's conversations (with pagination)
   - `GET /api/v1/conversations/{conversation_id}` - Get conversation details
   - `GET /api/v1/conversations/{conversation_id}/messages` - Get message history
   - `POST /api/v1/conversations/{conversation_id}/messages` - Send message

3. **Implement Request Lifecycle**
   - JWT validation middleware extracts user_id
   - Each endpoint receives user_id from context
   - Fetch conversation from DB
   - Validate user owns conversation (early return if not)
   - Process request (send message, get history, etc.)
   - Commit changes to DB
   - Return response without holding state

4. **Integrate with AI Agent**
   - Pass full message history to agent
   - Agent processes context independently
   - Agent returns response (no state persistence needed)
   - Store response in DB

5. **Testing & Validation**
   - Test request independence: send same request to different server instances, verify identical results
   - Test user isolation: verify user A cannot access user B's conversations
   - Test message ordering: verify messages are retrieved in correct chronological order
   - Test pagination: verify large message histories load efficiently
   - Test error cases: invalid tokens, missing conversations, invalid messages

## Success Criteria
✅ All endpoints require JWT authentication
✅ All endpoints validate user ownership (403 if not owner)
✅ Endpoints fetch full context from DB on each request
✅ No in-memory conversation state or caches
✅ Each request is self-contained and produces deterministic results
✅ Message ordering is correct (chronological)
✅ Responses include all necessary conversation context
✅ Database queries are efficient with proper indexes
✅ Error responses follow standard format
✅ Server can be scaled horizontally without session affinity

## Related Components
- **FastAPI Backend**: Endpoint implementation
- **Neon Database**: Conversation and message persistence
- **JWT Auth**: User context extraction
- **MCP Server**: Tool invocation from agents
- **Agents SDK**: AI response generation

## Scalability Notes
- Stateless design enables horizontal scaling
- Load balancer can route requests to any instance
- Database is single point of storage and consistency
- Consider connection pooling for database efficiency
- Add caching layer (Redis) if needed for read-heavy queries, but keep it optional for MVP

## Performance Considerations
- Index conversations by (user_id, conversation_id) for fast lookup
- Index messages by (conversation_id, created_at) for chronological retrieval
- Use pagination on message history endpoint for large conversations
- Consider lazy-loading message attachments if applicable
- Monitor query latency; optimize N+1 query patterns
