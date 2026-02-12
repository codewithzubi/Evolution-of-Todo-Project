# Chat Endpoint Specification

## Endpoint

**Method**: `POST`
**Path**: `/api/{user_id}/chat`
**Authentication**: Required (JWT Bearer token)

## Purpose

Primary endpoint for conversational task management. Accepts natural language messages, processes them through the AI agent with MCP tools, and returns conversational responses.

## Request

### Path Parameters

- `user_id` (string, required): The authenticated user's ID (must match JWT token)

### Request Body

```json
{
  "message": "string (required)",
  "conversation_id": "string (optional)"
}
```

**Fields**:
- `message`: User's natural language input (1-2000 characters)
- `conversation_id`: UUID of existing conversation thread (omit for new conversation)

### Headers

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

## Response

### Success Response (200 OK)

```json
{
  "success": true,
  "conversation_id": "uuid",
  "response": "string",
  "timestamp": "ISO 8601 timestamp",
  "tools_used": ["tool_name1", "tool_name2"],
  "context": {
    "tasks_affected": 1,
    "operation": "create|read|update|delete|complete"
  }
}
```

**Fields**:
- `conversation_id`: UUID for this conversation thread (use in subsequent requests)
- `response`: AI-generated natural language response
- `timestamp`: When the response was generated
- `tools_used`: Array of MCP tools invoked during processing
- `context`: Metadata about operations performed

### Error Responses

**400 Bad Request**:
```json
{
  "success": false,
  "error": "validation_error",
  "message": "Message is required and must be 1-2000 characters"
}
```

**401 Unauthorized**:
```json
{
  "success": false,
  "error": "unauthorized",
  "message": "Invalid or expired token"
}
```

**403 Forbidden**:
```json
{
  "success": false,
  "error": "forbidden",
  "message": "User ID in path does not match authenticated user"
}
```

**500 Internal Server Error**:
```json
{
  "success": false,
  "error": "internal_error",
  "message": "An error occurred processing your request"
}
```

## Processing Flow

### 1. Request Validation
- Verify JWT token is valid and not expired
- Confirm `user_id` in path matches token
- Validate message length and format
- Check conversation_id exists if provided

### 2. Fetch Conversation History
- If `conversation_id` provided:
  - Retrieve all messages from database for this conversation
  - Verify conversation belongs to authenticated user
  - Load messages in chronological order
- If no `conversation_id`:
  - Create new conversation record
  - Initialize empty history

### 3. Run AI Agent
- Construct prompt with:
  - System instructions (task management capabilities)
  - Conversation history (if any)
  - Current user message
  - Available MCP tools
- Invoke AI agent with tool-calling enabled
- Agent processes message and calls appropriate tools
- Agent generates natural language response

### 4. Save Message and Response
- Store user message in database:
  - `conversation_id`
  - `role`: "user"
  - `content`: user's message
  - `timestamp`
- Store AI response in database:
  - `conversation_id`
  - `role`: "assistant"
  - `content`: AI's response
  - `tools_used`: JSON array of tools called
  - `timestamp`

### 5. Return Response
- Send AI response to client
- Include conversation_id for continuity
- Include metadata about operations performed

## Example Interactions

### Example 1: New Conversation - Create Task

**Request**:
```http
POST /api/user-123/chat
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "message": "Add a task to buy groceries tomorrow"
}
```

**Response**:
```json
{
  "success": true,
  "conversation_id": "conv-abc-123",
  "response": "I've created a task for you: 'buy groceries' with a due date of February 12, 2026. Is there anything else you'd like me to help with?",
  "timestamp": "2026-02-11T22:00:00Z",
  "tools_used": ["add_task"],
  "context": {
    "tasks_affected": 1,
    "operation": "create"
  }
}
```

### Example 2: Continuing Conversation - List Tasks

**Request**:
```http
POST /api/user-123/chat
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "message": "What tasks do I have?",
  "conversation_id": "conv-abc-123"
}
```

**Response**:
```json
{
  "success": true,
  "conversation_id": "conv-abc-123",
  "response": "You have 3 tasks:\n1. Buy groceries (due tomorrow)\n2. Finish report (due Friday)\n3. Call dentist (no due date)\n\nWould you like to mark any of these as complete?",
  "timestamp": "2026-02-11T22:01:00Z",
  "tools_used": ["list_tasks"],
  "context": {
    "tasks_affected": 3,
    "operation": "read"
  }
}
```

### Example 3: Complete Task

**Request**:
```http
POST /api/user-123/chat
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "message": "I finished buying groceries",
  "conversation_id": "conv-abc-123"
}
```

**Response**:
```json
{
  "success": true,
  "conversation_id": "conv-abc-123",
  "response": "Great! I've marked 'buy groceries' as complete. You now have 2 remaining tasks. Need help with anything else?",
  "timestamp": "2026-02-11T22:05:00Z",
  "tools_used": ["complete_task"],
  "context": {
    "tasks_affected": 1,
    "operation": "complete"
  }
}
```

## Performance Considerations

- **Timeout**: Requests timeout after 30 seconds
- **Rate Limiting**: 60 requests per minute per user
- **History Limit**: Load last 50 messages for context (pagination for older messages)
- **Message Size**: Maximum 2000 characters per message
- **Concurrent Requests**: Queue requests per conversation to prevent race conditions

## Database Schema Requirements

### conversations table
```sql
- id (uuid, primary key)
- user_id (string, foreign key)
- created_at (timestamp)
- updated_at (timestamp)
```

### messages table
```sql
- id (uuid, primary key)
- conversation_id (uuid, foreign key)
- role (enum: 'user' | 'assistant')
- content (text)
- tools_used (jsonb, nullable)
- timestamp (timestamp)
```

## Security Considerations

- JWT token validated on every request
- User can only access their own conversations
- Conversation ownership verified before loading history
- All database queries use parameterized statements
- Message content sanitized before storage
- Tool calls logged for audit trail
