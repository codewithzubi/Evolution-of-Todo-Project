# Chat API Documentation

## Overview

The Chat API provides endpoints for managing conversations and messages with AI agents. The API uses JWT-based authentication and enforces user isolation at the database level.

**Base URL**: `/api/v1/chat`
**Authentication**: JWT Bearer token in `Authorization` header
**Response Format**: JSON with standard envelope: `{ "data": {...}, "error": null }`

---

## Authentication

All endpoints (except public ones like `/health`) require a valid JWT token in the `Authorization` header.

### Header Format
```
Authorization: Bearer <jwt_token>
```

### Token Claims
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "exp": 1640995200,
  "sub": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Authentication Errors
- **401 Unauthorized**: Missing or invalid token
  ```json
  {
    "data": null,
    "error": {
      "error_code": "UNAUTHORIZED",
      "error_message": "Missing Authorization header",
      "status_code": 401
    }
  }
  ```

---

## Endpoints

### 1. Create Conversation

Create a new conversation session.

**Endpoint**: `POST /api/v1/chat/conversations`

**Authentication**: Required (JWT)

**Request Body**:
```json
{
  "title": "Project Discussion (optional)"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Project Discussion",
    "message_count": 0,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "error": null
}
```

**Errors**:
- `401 Unauthorized`: Missing or invalid JWT token
- `422 Unprocessable Entity`: Invalid request body

**Example (cURL)**:
```bash
curl -X POST http://localhost:8000/api/v1/chat/conversations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Chat"}'
```

**Example (Python)**:
```python
import requests

headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "http://localhost:8000/api/v1/chat/conversations",
    json={"title": "My Chat"},
    headers=headers,
)
```

**Example (JavaScript)**:
```javascript
const response = await fetch('/api/v1/chat/conversations', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ title: 'My Chat' }),
});
```

---

### 2. List Conversations

Retrieve all conversations for the authenticated user (paginated).

**Endpoint**: `GET /api/v1/chat/conversations`

**Authentication**: Required (JWT)

**Query Parameters**:
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `limit` | int | 20 | 1-100 | Max results per page |
| `offset` | int | 0 | ≥0 | Pagination offset |

**Response** (200 OK):
```json
{
  "data": {
    "conversations": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "Project Discussion",
        "message_count": 5,
        "last_message_at": "2024-01-15T11:00:00Z",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T11:00:00Z"
      }
    ],
    "total": 1,
    "limit": 20,
    "offset": 0
  },
  "error": null
}
```

**Example (cURL)**:
```bash
curl -X GET "http://localhost:8000/api/v1/chat/conversations?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### 3. Get Conversation

Retrieve a specific conversation by ID.

**Endpoint**: `GET /api/v1/chat/conversations/{conversation_id}`

**Authentication**: Required (JWT)

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `conversation_id` | UUID | Conversation ID |

**Response** (200 OK):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Project Discussion",
    "message_count": 5,
    "last_message_at": "2024-01-15T11:00:00Z",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
  },
  "error": null
}
```

**Errors**:
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User doesn't own this conversation
- `404 Not Found`: Conversation not found

---

### 4. Delete Conversation

Soft-delete a conversation (cascades to all messages).

**Endpoint**: `DELETE /api/v1/chat/conversations/{conversation_id}`

**Authentication**: Required (JWT)

**Response** (204 No Content): Empty body

**Errors**:
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User doesn't own this conversation
- `404 Not Found`: Conversation not found

**Example (cURL)**:
```bash
curl -X DELETE http://localhost:8000/api/v1/chat/conversations/{conversation_id} \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### 5. Get Messages

Retrieve message history from a conversation (paginated, newest first).

**Endpoint**: `GET /api/v1/chat/conversations/{conversation_id}/messages`

**Authentication**: Required (JWT)

**Query Parameters**:
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `limit` | int | 20 | 1-100 | Max results per page |
| `offset` | int | 0 | ≥0 | Pagination offset |

**Response** (200 OK):
```json
{
  "data": {
    "messages": [
      {
        "id": "msg-001",
        "conversation_id": "conv-001",
        "role": "user",
        "content": "Hello, can you help?",
        "tool_calls": null,
        "tool_results": null,
        "created_at": "2024-01-15T10:30:00Z"
      },
      {
        "id": "msg-002",
        "conversation_id": "conv-001",
        "role": "assistant",
        "content": "Of course! How can I help?",
        "tool_calls": null,
        "tool_results": null,
        "created_at": "2024-01-15T10:31:00Z"
      }
    ],
    "total": 2,
    "limit": 20,
    "offset": 0
  },
  "error": null
}
```

**Message Roles**:
- `user`: Message from the user
- `assistant`: Message from the AI assistant
- `system`: System messages (rare)

**Tool Calls & Results**:
If the assistant invoked tools:
```json
{
  "id": "msg-003",
  "role": "assistant",
  "content": "Let me search for that.",
  "tool_calls": [
    {
      "id": "call_001",
      "type": "function",
      "function": {
        "name": "web_search",
        "arguments": "{\"query\": \"best programming languages\"}"
      }
    }
  ],
  "tool_results": {
    "web_search": ["Result 1", "Result 2", ...]
  }
}
```

---

### 6. Send Message

Send a message and get AI response.

**Endpoint**: `POST /api/v1/chat/conversations/{conversation_id}/messages`

**Authentication**: Required (JWT)

**Request Body**:
```json
{
  "message": "What is the capital of France?",
  "metadata": {
    "context": "value (optional)"
  }
}
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "msg-003",
    "role": "assistant",
    "content": "The capital of France is Paris...",
    "tool_calls": null,
    "tool_results": null,
    "created_at": "2024-01-15T10:32:00Z"
  },
  "error": null
}
```

**Errors**:
- `400 Bad Request`: Empty or oversized message
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User doesn't own conversation
- `404 Not Found`: Conversation not found
- `500 Internal Server Error`: AI service error
- `503 Service Unavailable`: Rate limit exceeded
- `504 Gateway Timeout`: Agent execution timeout

**Example (cURL)**:
```bash
curl -X POST http://localhost:8000/api/v1/chat/conversations/{conversation_id}/messages \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, AI!",
    "metadata": {"source": "web"}
  }'
```

**Example (Python)**:
```python
response = requests.post(
    f"http://localhost:8000/api/v1/chat/conversations/{conv_id}/messages",
    json={"message": "Hello!"},
    headers={"Authorization": f"Bearer {token}"},
)
result = response.json()
print(result["data"]["content"])
```

**Example (JavaScript)**:
```javascript
const response = await fetch(
  `/api/v1/chat/conversations/${conversationId}/messages`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: 'Hello!',
      metadata: { source: 'web' },
    }),
  }
);
const result = await response.json();
console.log(result.data.content);
```

---

### 7. Delete Message

Soft-delete a message from a conversation.

**Endpoint**: `DELETE /api/v1/chat/conversations/{conversation_id}/messages/{message_id}`

**Authentication**: Required (JWT)

**Response** (204 No Content): Empty body

**Errors**:
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User doesn't own message
- `404 Not Found`: Conversation or message not found

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "data": null,
  "error": {
    "error_code": "CONVERSATION_NOT_FOUND",
    "error_message": "Conversation not found",
    "status_code": 404,
    "details": {
      "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  }
}
```

### Common Error Codes

| Code | Status | Description | Recovery |
|------|--------|-------------|----------|
| `UNAUTHORIZED` | 401 | Missing/invalid JWT | Refresh token |
| `CONVERSATION_NOT_FOUND` | 404 | Conversation doesn't exist | Create new conversation |
| `UNAUTHORIZED_CONVERSATION_ACCESS` | 403 | User doesn't own conversation | Use correct conversation ID |
| `INVALID_MESSAGE` | 400 | Message is empty or too long | Trim message to <5000 chars |
| `OPENAI_API_ERROR` | 500 | AI service failed | Retry after 30s |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Wait before retrying |
| `AGENT_TIMEOUT` | 504 | AI took too long | Refresh page to check status |

### Handling Rate Limits

If you receive a 429 response:

```json
{
  "data": null,
  "error": {
    "error_code": "RATE_LIMIT_EXCEEDED",
    "error_message": "Too many requests. Please try again later.",
    "status_code": 429,
    "details": {
      "retry_after": 60
    }
  }
}
```

**Retry Strategy**:
- Wait `retry_after` seconds
- Use exponential backoff: 1s → 2s → 4s → ...
- Maximum 5 retries

**Rate Limit**: 60 messages per hour per user

---

## Security Considerations

### User Isolation
- All operations are scoped to the authenticated user
- Cross-user access attempts return 403 Forbidden
- Row-level security enforced at the database level

### Token Security
- Tokens are JWT-signed with HS256
- Tokens expire after configured duration
- Store tokens securely (httpOnly cookies recommended)
- Never log tokens in client-side code

### Data Protection
- All messages stored encrypted in transit (HTTPS)
- Database uses row-level security
- Soft deletes preserve audit trail
- No user data leakage between requests

---

## Performance

### Typical Response Times
- Create conversation: <100ms
- List conversations: <200ms (with pagination)
- Get message history: <200ms (with limit=20)
- Send message: 1-10 seconds (depends on AI service)

### Optimization Tips
- Use pagination (limit=20) for message history
- Cache conversation list locally
- Implement optimistic updates in UI
- Batch requests where possible

---

## Examples

### Full Conversation Flow

```python
import requests

# 1. Create conversation
token = "your_jwt_token"
headers = {"Authorization": f"Bearer {token}"}

# Create conversation
conv_resp = requests.post(
    "http://localhost:8000/api/v1/chat/conversations",
    json={"title": "Tech Support"},
    headers=headers,
)
conv_id = conv_resp.json()["data"]["id"]

# 2. Send message
msg_resp = requests.post(
    f"http://localhost:8000/api/v1/chat/conversations/{conv_id}/messages",
    json={"message": "How do I reset my password?"},
    headers=headers,
)
ai_response = msg_resp.json()["data"]["content"]
print(f"AI: {ai_response}")

# 3. Get history
hist_resp = requests.get(
    f"http://localhost:8000/api/v1/chat/conversations/{conv_id}/messages",
    headers=headers,
)
messages = hist_resp.json()["data"]["messages"]
for msg in messages:
    print(f"{msg['role']}: {msg['content']}")

# 4. Delete conversation
delete_resp = requests.delete(
    f"http://localhost:8000/api/v1/chat/conversations/{conv_id}",
    headers=headers,
)
assert delete_resp.status_code == 204
```

---

## FAQ

**Q: Can I modify a message after sending?**
A: No. Messages are immutable. Use soft-delete to hide them.

**Q: How long are conversations stored?**
A: Indefinitely, unless explicitly deleted with soft-delete.

**Q: Can I see other users' conversations?**
A: No. User isolation is enforced at all levels.

**Q: What's the maximum message length?**
A: 5000 characters per message.

**Q: How fast is the AI response?**
A: Typically 1-10 seconds depending on the query and AI service load.

---

## Support

For issues or questions:
- Check the error code and recovery suggestion
- Review logs with correlation IDs
- Contact support with request IDs for debugging

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0
