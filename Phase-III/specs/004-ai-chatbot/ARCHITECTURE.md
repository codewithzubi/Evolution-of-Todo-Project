# Phase-III AI Todo Chatbot - Architecture & Implementation Plan

**Document Version**: 1.0
**Created**: 2026-02-07
**Status**: Ready for Review
**Specification Reference**: `specs/004-ai-chatbot/spec.md`

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [System Components](#system-components)
4. [Phase-by-Phase Implementation](#phase-by-phase-implementation)
5. [Technical Specifications](#technical-specifications)
6. [Integration with Phase-II](#integration-with-phase-ii)
7. [Security & Isolation](#security--isolation)
8. [Testing Strategy](#testing-strategy)
9. [Risk Analysis & Mitigation](#risk-analysis--mitigation)
10. [Effort Estimation](#effort-estimation)

---

## Executive Summary

Phase-III AI Todo Chatbot transforms the existing Phase-II task management system by adding conversational AI capabilities via OpenAI Agents SDK. The architecture maintains strict stateless design principles while persisting conversation history in the database.

**Key Design Principles**:
- **Stateless Backend**: No in-memory conversation state; all data persists to database
- **MCP-First Architecture**: AI never directly queries the database; all task operations flow through MCP tools
- **Zero Phase-II Changes**: Reuses existing `/api/{user_id}/tasks/*` endpoints; no modifications
- **JWT-Scoped Isolation**: All operations filtered by authenticated user_id; 403 Forbidden on cross-user access
- **Confirmation Gates**: Destructive operations require explicit user confirmation before execution

**Success Metrics**:
- Task creation speed: <90 seconds (5-6 turn dialogue)
- Chat response time: 2-3 seconds (p95)
- Conversation persistence: 100% message recovery across refresh/restart
- Test coverage: 70% minimum for Phase-III code
- Zero Phase-II regression: All existing tests pass

---

## Architecture Overview

### System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js 16+)                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Phase-II UI (Tasks Page)           ChatKit Widget (Bottom-R)  │ │
│  │  - Task List                        - Chat Input Field        │ │
│  │  - Create/Edit Modals               - Message History         │ │
│  │  - Auth (Better Auth)               - Float Animation         │ │
│  └────────────────────────────────────────────────────────────────┘ │
│         │                                      │                     │
│         │ (Phase-II endpoints)                │ (Phase-III)         │
│         ↓                                      ↓                     │
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI - Python)                        │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ JWT Middleware → User ID Extraction                           │ │
│  │ ┌────────────────────────────────────────────────────────────┐│ │
│  │ │ Phase-III Chat Endpoint: POST /api/v1/chat/conversations/ ││ │
│  │ │ - JWT Validation                                           ││ │
│  │ │ - Load conversation history from DB                        ││ │
│  │ │ - Invoke OpenAI Agents SDK                                 ││ │
│  │ │ - MCP Tool Execution (add, list, update, complete, delete)││ │
│  │ │ - Persist messages to DB                                   ││ │
│  │ └────────────────────────────────────────────────────────────┘│ │
│  │ ┌────────────────────────────────────────────────────────────┐│ │
│  │ │ MCP Server (Stateless Tools)                               ││ │
│  │ │ - add_task(user_id, title, description, priority, due_date)││ │
│  │ │ - list_tasks(user_id, filters)                             ││ │
│  │ │ - update_task(user_id, task_id, fields)                    ││ │
│  │ │ - complete_task(user_id, task_id)                          ││ │
│  │ │ - delete_task(user_id, task_id)                            ││ │
│  │ └─ CALLS PHASE-II ENDPOINTS ──→ /api/{user_id}/tasks/*────────┘│ │
│  │ ┌────────────────────────────────────────────────────────────┐│ │
│  │ │ Phase-II APIs (UNCHANGED)                                  ││ │
│  │ │ - POST /{user_id}/tasks (create)                           ││ │
│  │ │ - GET /{user_id}/tasks (list)                              ││ │
│  │ │ - PUT /{user_id}/tasks/{id} (update)                       ││ │
│  │ │ - PATCH /{user_id}/tasks/{id}/complete (complete)          ││ │
│  │ │ - DELETE /{user_id}/tasks/{id} (delete)                    ││ │
│  │ └────────────────────────────────────────────────────────────┘│ │
│  └────────────────────────────────────────────────────────────────┘ │
│                               ↓                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Database Layer (Neon PostgreSQL via SQLAlchemy Async)         │ │
│  │ ┌──────────────────┐  ┌──────────────────┐                    │ │
│  │ │ conversations    │  │ messages         │  (Phase-III)       │ │
│  │ │ - id (UUID)      │  │ - id (UUID)      │                    │ │
│  │ │ - user_id        │  │ - conversation_id│                    │ │
│  │ │ - title          │  │ - user_id        │                    │ │
│  │ │ - created_at     │  │ - role (enum)    │                    │ │
│  │ │ - updated_at     │  │ - content        │                    │ │
│  │ │ - deleted_at     │  │ - metadata (JSON)│                    │ │
│  │ │ (soft delete)    │  │ - created_at     │                    │ │
│  │ └──────────────────┘  └──────────────────┘                    │ │
│  │ ┌──────────────────┐  ┌──────────────────┐                    │ │
│  │ │ users            │  │ tasks            │  (Phase-II - KEEP) │ │
│  │ │ - id             │  │ - id             │                    │ │
│  │ │ - email          │  │ - user_id        │                    │ │
│  │ │ - password_hash  │  │ - title          │                    │ │
│  │ │ - created_at     │  │ - description    │                    │ │
│  │ └──────────────────┘  │ - due_date       │                    │ │
│  │                       │ - completed      │                    │ │
│  │                       │ - priority       │                    │ │
│  │                       │ - tags           │                    │ │
│  │                       └──────────────────┘                    │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│                       EXTERNAL SERVICES                              │
│  ┌────────────────────────┐  ┌───────────────────────────────────┐ │
│  │ OpenAI Agents SDK      │  │ Neon PostgreSQL                   │ │
│  │ - GPT-4 Model          │  │ - Conversation History            │ │
│  │ - Tool Execution       │  │ - Message Persistence             │ │
│  │ - Token Management     │  │ - User Isolation                  │ │
│  └────────────────────────┘  └───────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Information Flow: User Message to AI Response

```
1. USER MESSAGE
   ↓
2. Frontend: POST /api/v1/chat/conversations/{conversation_id}/messages
   Headers: Authorization: Bearer {JWT_TOKEN}
   Body: { "content": "Create a task to buy groceries" }
   ↓
3. Backend: JWT Validation
   - Extract user_id from JWT claims
   - Verify user owns the conversation (403 if not)
   ↓
4. Database: Load Conversation History
   - Query messages table WHERE conversation_id AND user_id
   - Select last 20 messages (token window management)
   ↓
5. OpenAI Agents SDK Initialization
   - Create agent with system prompt (task management expert)
   - Pass conversation history as context
   - Define MCP tools available to agent
   ↓
6. Agent Reasoning
   - AI analyzes user message
   - Determines intent (create/list/update/complete/delete)
   - Generates clarifying questions or tool call
   - For create: asks title → description → priority → due_date → confirmation
   ↓
7. MCP Tool Invocation (if needed)
   - Agent decides to call tool (e.g., add_task)
   - Tool call includes user_id (from JWT) for scoping
   - MCP handler validates parameters
   ↓
8. Phase-II API Call (via MCP Tool)
   - Tool calls: POST /api/{user_id}/tasks
   - Passes structured task data
   - Phase-II service creates task in database
   ↓
9. Response Processing
   - Tool returns success/error
   - Agent generates natural language response
   ↓
10. Message Persistence
    - Store user message in messages table
    - Store assistant response in messages table
    - Metadata includes tool call details
    ↓
11. Response to Frontend
    {
      "data": {
        "conversation_id": "uuid",
        "user_message": "Create a task...",
        "assistant_message": "Great! I've created...",
        "task_created": { id, title, ... }
      },
      "error": null
    }
    ↓
12. Frontend UI Update
    - Display assistant response in chat
    - If task was created, show confirmation
    - Task appears in Phase-II task list immediately (no refresh needed)
```

---

## System Components

### 1. OpenAI Agents SDK Integration

**Purpose**: Multi-turn AI reasoning with tool execution capability

**Configuration**:
```python
# backend/src/agents/chatbot_agent.py (pseudo-code)

from openai import OpenAI
from openai.lib.agents import Agent

class ChatbotAgent:
    def __init__(self, user_id: UUID, conversation_history: List[Message]):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.user_id = user_id
        self.conversation_history = conversation_history
        self.mcp_tools = self._define_tools()

    def _define_tools(self) -> List[Tool]:
        """Define MCP tools available to agent"""
        return [
            self._create_add_task_tool(),
            self._create_list_tasks_tool(),
            self._create_update_task_tool(),
            self._create_complete_task_tool(),
            self._create_delete_task_tool(),
        ]

    async def process_message(self, user_message: str) -> str:
        """Process user message and return agent response"""
        # Build message list with conversation history
        messages = self._build_message_list(user_message)

        # Initialize agent
        agent = Agent(
            client=self.client,
            model="gpt-4",
            tools=self.mcp_tools,
            system_prompt=self._get_system_prompt(),
            instructions=self._get_instructions(),
        )

        # Run agent (handles tool execution loop internally)
        response = await agent.run(messages)
        return response.content

    def _get_system_prompt(self) -> str:
        """System prompt: agent is task management expert"""
        return """You are a helpful task management assistant. Your role is to:
        1. Help users create, list, update, complete, and delete tasks
        2. Ask clarifying questions when information is missing
        3. Summarize task details before creating/updating
        4. Request explicit confirmation before destructive operations (delete)
        5. Be conversational and supportive
        6. Handle edge cases gracefully (non-existent tasks, ambiguous references)

        Always use natural language; guide users through multi-step workflows.
        Never execute destructive operations without explicit user confirmation."""

    def _get_instructions(self) -> str:
        """Tool execution instructions for agent"""
        return """When creating a task:
        1. Ask for title (required)
        2. Ask for description (optional, can suggest based on context)
        3. Ask for priority (low/medium/high, default medium)
        4. Ask for due date (optional, natural language format)
        5. Summarize collected details
        6. Request confirmation ("yes" or "confirm")
        7. Only then call add_task tool

        When listing tasks: call list_tasks with filters based on user's intent

        When updating tasks: confirm which task and what field before updating

        When completing tasks: optionally offer encouragement

        When deleting tasks: ALWAYS ask explicit confirmation first (non-negotiable)"""
```

**Key Responsibilities**:
- Initialize Agent with conversation history and MCP tools
- Manage multi-turn dialogue (asking clarifying questions)
- Call MCP tools when user confirms intent
- Generate natural language responses
- Handle tool errors gracefully

**Dependencies**:
- OpenAI SDK (`openai>=1.3.0`)
- MCP tool definitions (see section 2)
- Conversation history from database

### 2. MCP Server & Tool Definitions

**Purpose**: Stateless interface between AI agent and task management APIs

**Tool Specifications**:

#### Tool: `add_task`
```python
{
    "name": "add_task",
    "description": "Create a new task with title, optional description, priority, and due date",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "format": "uuid", "description": "User ID (auto-injected from JWT)"},
            "title": {"type": "string", "minLength": 1, "maxLength": 255, "description": "Task title"},
            "description": {"type": "string", "maxLength": 2000, "description": "Task description"},
            "priority": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"},
            "due_date": {"type": "string", "format": "date-time", "description": "ISO 8601 due date"}
        },
        "required": ["user_id", "title"]
    },
    "returns": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "task_id": {"type": "string", "format": "uuid"},
            "title": {"type": "string"},
            "message": {"type": "string"}
        }
    }
}
```

**Implementation**:
```python
# backend/src/mcp_server/tools/add_task.py (pseudo-code)

async def add_task(
    user_id: UUID,
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    due_date: Optional[datetime] = None,
) -> Dict:
    """Call Phase-II task creation endpoint"""

    # Validate parameters
    if not title or len(title) < 1 or len(title) > 255:
        return {"success": False, "error": "Title must be 1-255 characters"}

    # Call Phase-II API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:8000/api/{user_id}/tasks",
            json={
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": due_date,
            },
            headers={"Authorization": f"Bearer {get_service_token(user_id)}"},
        )

    if response.status_code == 201:
        task = response.json()["data"]
        return {
            "success": True,
            "task_id": task["id"],
            "title": task["title"],
            "message": f"Task '{title}' created successfully!"
        }
    else:
        return {
            "success": False,
            "error": f"Failed to create task: {response.text}"
        }
```

#### Tool: `list_tasks`
```python
{
    "name": "list_tasks",
    "description": "List user's tasks with optional filters (status, priority, due date)",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "format": "uuid", "description": "User ID"},
            "status": {"type": "string", "enum": ["completed", "incomplete"], "description": "Filter by status"},
            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Filter by priority"},
            "overdue": {"type": "boolean", "description": "Show only overdue tasks"},
            "limit": {"type": "integer", "default": 10, "minimum": 1, "maximum": 100}
        },
        "required": ["user_id"]
    },
    "returns": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "priority": {"type": "string"},
                "completed": {"type": "boolean"},
                "due_date": {"type": "string"}
            }
        }
    }
}
```

**Implementation**:
```python
# backend/src/mcp_server/tools/list_tasks.py (pseudo-code)

async def list_tasks(
    user_id: UUID,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    overdue: bool = False,
    limit: int = 10,
) -> List[Dict]:
    """List user's tasks with optional filtering"""

    # Build query parameters
    params = {"limit": limit}

    # Fetch from Phase-II API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/api/{user_id}/tasks",
            params=params,
            headers={"Authorization": f"Bearer {get_service_token(user_id)}"},
        )

    if response.status_code != 200:
        return []

    tasks = response.json()["data"]["items"]

    # Apply client-side filtering (agent can understand intent better)
    filtered = tasks

    if status == "completed":
        filtered = [t for t in filtered if t["completed"]]
    elif status == "incomplete":
        filtered = [t for t in filtered if not t["completed"]]

    if priority:
        filtered = [t for t in filtered if t["priority"] == priority]

    if overdue:
        now = datetime.utcnow()
        filtered = [t for t in filtered if t["due_date"] and t["due_date"] < now and not t["completed"]]

    return filtered
```

#### Tool: `update_task`
```python
{
    "name": "update_task",
    "description": "Update task fields (title, description, priority, due_date)",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "format": "uuid"},
            "task_id": {"type": "string", "format": "uuid"},
            "title": {"type": "string", "minLength": 1, "maxLength": 255},
            "description": {"type": "string", "maxLength": 2000},
            "priority": {"type": "string", "enum": ["low", "medium", "high"]},
            "due_date": {"type": "string", "format": "date-time"}
        },
        "required": ["user_id", "task_id"]
    },
    "returns": {"type": "object"}
}
```

**Implementation**: Similar to add_task; calls PATCH endpoint with specified fields only

#### Tool: `complete_task`
```python
{
    "name": "complete_task",
    "description": "Mark a task as complete",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "format": "uuid"},
            "task_id": {"type": "string", "format": "uuid"}
        },
        "required": ["user_id", "task_id"]
    },
    "returns": {"type": "object"}
}
```

**Implementation**: Calls PATCH `/{user_id}/tasks/{task_id}/complete` with `{"completed": true}`

#### Tool: `delete_task`
```python
{
    "name": "delete_task",
    "description": "Delete a task permanently (requires explicit confirmation)",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "format": "uuid"},
            "task_id": {"type": "string", "format": "uuid"}
        },
        "required": ["user_id", "task_id"]
    },
    "returns": {"type": "object"}
}
```

**Implementation**: Calls DELETE `/{user_id}/tasks/{task_id}`

### 3. Chat Endpoint

**FastAPI Endpoint**: `POST /api/v1/chat/conversations/{conversation_id}/messages`

**Request Schema**:
```python
class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="User message")
    metadata: Optional[Dict] = None  # Optional client metadata

class ChatMessageResponse(BaseModel):
    conversation_id: UUID
    user_message: str
    assistant_message: str
    tool_calls: Optional[List[Dict]]  # For debugging
    created_at: datetime
```

**Implementation (pseudo-code)**:
```python
# backend/src/api/chat.py

@router.post(
    "/v1/chat/conversations/{conversation_id}/messages",
    status_code=200,
    response_model=SuccessResponse[ChatMessageResponse],
)
async def send_chat_message(
    conversation_id: UUID,
    request_body: ChatMessageRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> SuccessResponse:
    """Process user message and return AI response"""

    # 1. JWT Validation
    jwt_user_id: UUID = request.state.user_id
    if not jwt_user_id:
        raise UnauthorizedException("Missing JWT token")

    # 2. Verify user owns conversation (403 if not)
    conversation = await session.get(Conversation, conversation_id)
    if not conversation:
        raise NotFoundException("Conversation not found")
    if conversation.user_id != jwt_user_id:
        raise ForbiddenException("You do not have permission to access this conversation")

    # 3. Store user message in database
    user_message = Message(
        id=uuid4(),
        conversation_id=conversation_id,
        user_id=jwt_user_id,
        role="user",
        content=request_body.content,
        created_at=datetime.utcnow(),
    )
    session.add(user_message)
    await session.commit()

    # 4. Load conversation history (last 20 messages for token window)
    history = await session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(20)
    )
    history = list(reversed(history.all()))  # Reverse to chronological order

    # 5. Initialize agent
    agent = ChatbotAgent(user_id=jwt_user_id, conversation_history=history)

    # 6. Process message (agent handles tool execution)
    try:
        assistant_response = await agent.process_message(request_body.content)
    except Exception as e:
        logger.error(f"Agent error: {e}")
        assistant_response = "I encountered an error. Please try again."

    # 7. Store assistant message
    assistant_message = Message(
        id=uuid4(),
        conversation_id=conversation_id,
        user_id=jwt_user_id,
        role="assistant",
        content=assistant_response,
        created_at=datetime.utcnow(),
        metadata={
            "model": "gpt-4",
            "tool_calls": [],  # Populated by agent
        }
    )
    session.add(assistant_message)
    await session.commit()

    # 8. Update conversation updated_at
    conversation.updated_at = datetime.utcnow()
    await session.commit()

    # 9. Return response
    return SuccessResponse(
        data=ChatMessageResponse(
            conversation_id=conversation_id,
            user_message=request_body.content,
            assistant_message=assistant_response,
            created_at=assistant_message.created_at,
        ),
        error=None,
    )
```

### 4. Database Schema

**New Tables for Phase-III**:

```sql
-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,
    INDEX idx_conversations_user_id (user_id),
    INDEX idx_conversations_created_at (created_at),
    INDEX idx_conversations_user_created (user_id, created_at)
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_messages_conversation (conversation_id),
    INDEX idx_messages_user (user_id),
    INDEX idx_messages_created (created_at),
    INDEX idx_messages_conversation_created (conversation_id, created_at),
    INDEX idx_messages_user_conversation (user_id, conversation_id)
);
```

**SQLModel Classes**:

```python
# backend/src/models/conversation.py

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None


# backend/src/models/message.py

from enum import Enum
from typing import Optional, Dict, Any
from sqlmodel import Field, SQLModel

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    role: MessageRole = Field(description="Message sender (user, assistant, system)")
    content: str = Field(description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Tool calls, tokens used, etc.")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 5. Chat UI Widget (Next.js)

**Component**: Floating ChatKit widget positioned bottom-right

**Location**: `frontend/src/components/chat/ChatWidget.tsx` (Client Component)

**Features**:
- Floating icon/button (bottom-right corner)
- Click to open/close chat window with smooth animation
- Message history loaded from database
- Authenticated users only (checks JWT token validity)
- Persists across page refresh
- Lazy loading (doesn't impact initial page load)

**Implementation Outline**:
```typescript
// frontend/src/components/chat/ChatWidget.tsx

"use client"; // Client component

import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import ChatWindow from "./ChatWindow";

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const { token, isAuthenticated } = useAuth();

  useEffect(() => {
    // Only show to authenticated users
    if (!isAuthenticated) return;

    // Load or create conversation
    const loadConversation = async () => {
      const response = await fetch("/api/v1/chat/conversations", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setConversationId(data.data.conversation_id);
      }
    };

    loadConversation();
  }, [isAuthenticated, token]);

  if (!isAuthenticated || !conversationId) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Float button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-12 h-12 bg-blue-600 rounded-full shadow-lg hover:bg-blue-700 transition"
      >
        Chat
      </button>

      {/* Chat window (animated) */}
      {isOpen && (
        <ChatWindow
          conversationId={conversationId}
          onClose={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}
```

**Integration**: Add `<ChatWidget />` to main layout (e.g., `layout.tsx` or route wrapper) once authenticated

---

## Phase-by-Phase Implementation

### Phase 1: Database Schema & Migrations (Effort: 2 days)

**Tasks**:
1. Create SQLModel classes for `Conversation` and `Message`
2. Create Alembic migration: `003_create_conversations_and_messages.py`
3. Create database indexes for performance
4. Add seed data for testing (optional)

**Deliverables**:
- New tables in Neon PostgreSQL
- SQLModel classes ready for ORM operations
- Migration script executable via `alembic upgrade head`
- No changes to Phase-II tables

**Dependencies**: None (standalone)

**Validation**:
- Run migration successfully
- Verify tables exist in Neon
- Confirm indexes are created
- Test ORM operations (create, read, update)

---

### Phase 2: MCP Server & Tool Definitions (Effort: 4 days)

**Tasks**:
1. Create MCP server module: `backend/src/mcp_server/`
2. Implement tool handlers:
   - `add_task.py` → POST `/api/{user_id}/tasks`
   - `list_tasks.py` → GET `/api/{user_id}/tasks` with filters
   - `update_task.py` → PATCH `/api/{user_id}/tasks/{id}`
   - `complete_task.py` → PATCH `/api/{user_id}/tasks/{id}/complete`
   - `delete_task.py` → DELETE `/api/{user_id}/tasks/{id}`
3. Implement tool registry and schema definitions
4. Add parameter validation and error handling
5. Create unit tests for each tool

**Deliverables**:
- MCP server module with 5 tools
- Tool schemas in JSON format
- Error handling and retry logic
- Unit tests (90% coverage for tools)

**Dependencies**: Phase 1 (database schema)

**Validation**:
- All tools callable and return expected schema
- Tools properly scope by user_id
- Error messages are user-friendly
- Phase-II endpoints are called correctly

---

### Phase 3: Chat Endpoint & Agent Integration (Effort: 5 days)

**Tasks**:
1. Implement ChatbotAgent class using OpenAI SDK
2. Create chat endpoint: `POST /api/v1/chat/conversations/{conversation_id}/messages`
3. Implement message persistence (user + assistant)
4. Implement conversation history retrieval (last 20 messages)
5. Implement token window management
6. Add confirmation flow for destructive operations
7. Create integration tests (end-to-end chat flows)

**Deliverables**:
- ChatbotAgent class with multi-turn support
- Chat endpoint with full JWT validation
- Message persistence and retrieval
- Integration tests for all user stories
- Error handling and graceful degradation

**Dependencies**: Phase 1 (database), Phase 2 (MCP tools)

**Validation**:
- Chat endpoint responds in <3 seconds
- Messages persisted correctly
- Agent calls correct tools
- 403 Forbidden on cross-user access
- All 5 user stories pass integration tests

---

### Phase 4: Chat UI Widget Integration (Effort: 3 days)

**Tasks**:
1. Create ChatKit or custom Chat component
2. Create floating ChatWidget component
3. Integrate into Phase-II layout
4. Implement message history loading
5. Test lazy loading and performance
6. Mobile responsiveness

**Deliverables**:
- ChatWidget component (Client Component)
- ChatWindow component with message list
- CSS animations for open/close
- Mobile-responsive design
- Integration with Phase-II layout

**Dependencies**: Phase 3 (chat endpoint)

**Validation**:
- Widget appears only to authenticated users
- Widget doesn't impact page load time (<500ms)
- Messages load and persist across refresh
- Animations smooth and performant
- Works on mobile/tablet

---

### Phase 5: Testing & Security Validation (Effort: 4 days)

**Tasks**:
1. Unit tests for all MCP tools (existing tests from Phase 2)
2. Integration tests for chat endpoint
3. End-to-end tests for all user stories
4. Security tests:
   - JWT validation
   - User isolation (403 on cross-user access)
   - SQL injection prevention
   - Token expiration handling
5. Performance tests (response time, throughput)
6. Regression tests (ensure Phase-II still works)

**Deliverables**:
- 70%+ code coverage for Phase-III
- All user stories passing tests
- Security test report
- Performance benchmarks
- Phase-II regression test report (zero failures)

**Dependencies**: All phases

**Validation**:
- Coverage report: 70%+ minimum
- All user stories pass acceptance tests
- Security audit passed
- Performance targets met (2-3 sec response time)
- Phase-II: zero regressions

---

## Technical Specifications

### Security Architecture

**JWT Validation Flow**:

```
1. Frontend sends Authorization: Bearer {JWT_TOKEN}
2. Backend middleware extracts user_id from JWT claims
3. All endpoints verify JWT user_id matches URL/request user_id
4. Tool invocations include user_id from JWT (cannot be forged)
5. Database queries filtered by user_id (WHERE clause)
6. Cross-user access returns 403 Forbidden (not 404)
```

**Implementation**:
```python
# backend/src/api/middleware.py

async def jwt_middleware(request: Request, call_next):
    """Extract user_id from JWT token"""
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        # Check if endpoint is public (e.g., /health)
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        raise UnauthorizedException("Missing JWT token")

    token = auth_header[7:]  # Remove "Bearer " prefix

    try:
        # Decode JWT
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")

        if not user_id:
            raise UnauthorizedException("Invalid JWT: missing user_id")

        # Attach user_id to request state
        request.state.user_id = UUID(user_id)
    except jwt.DecodeError:
        raise UnauthorizedException("Invalid JWT signature")
    except Exception as e:
        raise UnauthorizedException(f"JWT validation failed: {str(e)}")

    return await call_next(request)
```

**Tool-Level Security**:

```python
# backend/src/mcp_server/tools/base.py

async def execute_tool(tool_name: str, user_id: UUID, **params):
    """Execute tool with user_id scoping"""

    # Inject user_id into params (cannot be overridden by user)
    params["user_id"] = user_id

    # Validate parameters
    tool_schema = get_tool_schema(tool_name)
    validated_params = validate_parameters(params, tool_schema)

    # Execute tool
    handler = get_tool_handler(tool_name)
    return await handler(**validated_params)
```

### Error Handling

**Error Categories**:

| Error | Code | Status | Action |
|-------|------|--------|--------|
| Missing JWT | UNAUTHORIZED | 401 | Return error message; user logs in |
| Invalid JWT | UNAUTHORIZED | 401 | Return error message; user logs in |
| User doesn't own resource | FORBIDDEN | 403 | Return error; don't leak resource existence |
| Tool parameter invalid | VALIDATION_ERROR | 422 | Return field-level details; user retries |
| Task not found | NOT_FOUND | 404 | Agent asks for clarification |
| OpenAI API error | API_ERROR | 500 | Retry with backoff; user gets friendly message |
| Database error | DATABASE_ERROR | 500 | Log error; user gets "try again later" |

**User-Facing Error Messages**:
- "Sorry, I didn't understand. Could you rephrase?"
- "I couldn't find a task matching that description. Did you mean: [list options]?"
- "I encountered a temporary issue. Please try again."
- "Please confirm: Do you want to delete '[task name]'? (say 'yes' or 'no')"

### Token Window Management

**Problem**: Conversations can grow beyond OpenAI's context window (128k tokens for GPT-4)

**Solution**: Load only last 20 messages into agent context

```python
# backend/src/services/conversation_service.py

async def get_conversation_context(
    conversation_id: UUID,
    user_id: UUID,
    max_messages: int = 20,
) -> List[Message]:
    """Get last N messages for agent context"""

    result = await session.exec(
        select(Message)
        .where(
            (Message.conversation_id == conversation_id)
            & (Message.user_id == user_id)
        )
        .order_by(Message.created_at.desc())
        .limit(max_messages)
    )

    messages = result.all()
    # Reverse to chronological order
    return list(reversed(messages))
```

**Benefits**:
- Reduces token usage (cheaper)
- Faster inference (fewer tokens to process)
- Full history still available in database (searchable later)

---

## Integration with Phase-II

### API Reuse

Phase-III MCP tools call Phase-II endpoints directly. No modifications to Phase-II code.

**Tool → Phase-II Endpoint Mapping**:

| MCP Tool | HTTP Method | Phase-II Endpoint | Auth |
|----------|-------------|-------------------|------|
| add_task | POST | `/{user_id}/tasks` | JWT |
| list_tasks | GET | `/{user_id}/tasks` | JWT |
| update_task | PATCH | `/{user_id}/tasks/{id}` | JWT |
| complete_task | PATCH | `/{user_id}/tasks/{id}/complete` | JWT |
| delete_task | DELETE | `/{user_id}/tasks/{id}` | JWT |

**Example MCP Tool Implementation**:

```python
# backend/src/mcp_server/tools/add_task.py

async def add_task(
    user_id: UUID,
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    due_date: Optional[datetime] = None,
    tags: Optional[str] = None,
) -> Dict:
    """Create task via Phase-II API"""

    # Use internal service token (server-to-server)
    # Never expose user's JWT to internal calls
    service_token = generate_service_token(user_id)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.PHASE2_BASE_URL}/api/{user_id}/tasks",
            json={
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": due_date,
                "tags": tags,
            },
            headers={"Authorization": f"Bearer {service_token}"},
            timeout=10.0,  # 10 second timeout
        )

    if response.status_code == 201:
        task = response.json()["data"]
        return {
            "success": True,
            "task_id": str(task["id"]),
            "title": task["title"],
            "message": f"Task '{title}' created successfully!",
        }
    elif response.status_code == 403:
        return {
            "success": False,
            "error": "Permission denied. You don't have access to this task.",
        }
    elif response.status_code == 404:
        return {
            "success": False,
            "error": "Task not found.",
        }
    else:
        return {
            "success": False,
            "error": f"Failed to create task: {response.text}",
        }
```

### Data Flow

**Phase-II Database Unchanged**:
- `users` table: authentication, Better Auth integration
- `tasks` table: task data (title, description, due_date, completed, priority, tags)

**Phase-III Extends with**:
- `conversations` table: chat sessions per user
- `messages` table: conversation history (user + assistant)

**No Coupling**:
- Phase-III doesn't modify Phase-II tables
- Phase-II endpoints remain unchanged
- Phase-II can be deployed/updated independently
- Phase-III adds layers on top (agent + conversation storage)

---

## Security & Isolation

### User Isolation Strategy

**Principle**: Every query includes `WHERE user_id = :user_id` from JWT

**Implementation**:

1. **Conversation Access**:
```python
# Only user who owns conversation can access it
conversation = await session.get(Conversation, conversation_id)
if conversation.user_id != jwt_user_id:
    raise ForbiddenException("Access denied")
```

2. **Message Queries**:
```python
# Query filtered by both conversation_id AND user_id
messages = await session.exec(
    select(Message).where(
        (Message.conversation_id == conversation_id)
        & (Message.user_id == user_id)
    )
)
```

3. **Tool Calls**:
```python
# user_id from JWT injected into tool params (cannot be forged)
task = await add_task(
    user_id=jwt_user_id,  # From JWT, not user input
    title=user_input.title,
    ...
)
```

### HTTP Status Codes for Errors

**Security Best Practice**: Use 403 (not 404) for forbidden resources

```python
# WRONG: Leaks information to attacker
if task not found for user:
    return 404  # Attacker knows task doesn't exist

# CORRECT: Doesn't leak information
if task doesn't belong to user:
    return 403  # Attacker can't tell if task exists
```

**Implementation**:
```python
async def get_conversation_message(
    conversation_id: UUID,
    message_id: UUID,
    jwt_user_id: UUID,
) -> Message:
    """Get message with proper 403 handling"""

    conversation = await session.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != jwt_user_id:
        # 403: Whether conversation exists or not
        raise ForbiddenException("You do not have permission to access this resource")

    message = await session.get(Message, message_id)
    if not message or message.conversation_id != conversation_id:
        # 403: Whether message exists or not
        raise ForbiddenException("You do not have permission to access this resource")

    return message
```

---

## Testing Strategy

### Unit Tests (Tool Level)

**Coverage**: 90%+ for MCP tools

**Test Cases per Tool**:

```python
# backend/tests/unit/test_add_task_tool.py

@pytest.mark.asyncio
async def test_add_task_success():
    """Test successful task creation"""
    result = await add_task(
        user_id=test_user_id,
        title="Buy groceries",
        description="Milk, eggs, bread",
        priority="high",
    )
    assert result["success"] is True
    assert result["task_id"] is not None
    assert "created successfully" in result["message"]

@pytest.mark.asyncio
async def test_add_task_invalid_title():
    """Test validation of title field"""
    result = await add_task(
        user_id=test_user_id,
        title="",  # Empty title
        priority="medium",
    )
    assert result["success"] is False
    assert "title" in result["error"].lower()

@pytest.mark.asyncio
async def test_add_task_phase2_api_error():
    """Test handling of Phase-II API error"""
    # Mock Phase-II API to return 500
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Database error"

        result = await add_task(
            user_id=test_user_id,
            title="Test task",
        )
        assert result["success"] is False
        assert "Database error" in result["error"]

@pytest.mark.asyncio
async def test_add_task_user_id_scoping():
    """Test that user_id cannot be overridden"""
    # User tries to pass different user_id
    result = await add_task(
        user_id=test_user_id,  # Correct user
        title="Task",
        # Agent cannot override this user_id
    )
    # Verify task created for correct user
    assert result["success"] is True
```

### Integration Tests (Chat Endpoint)

**Coverage**: All user stories + edge cases

**Test Cases**:

```python
# backend/tests/integration/test_chat_endpoint.py

@pytest.mark.asyncio
async def test_create_task_via_chat():
    """Test US1: Create task via conversation"""
    client = AsyncClient(app=app, base_url="http://test")

    # Setup
    user = await create_test_user()
    token = generate_test_jwt(user.id)
    conversation = await create_test_conversation(user.id)

    # User initiates task creation
    response = await client.post(
        f"/api/v1/chat/conversations/{conversation.id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "Create a task to buy groceries"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert "groceries" in data["assistant_message"].lower()

    # Follow up with task details
    response = await client.post(
        f"/api/v1/chat/conversations/{conversation.id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "High priority, due tomorrow"},
    )

    assert response.status_code == 200

    # Confirm creation
    response = await client.post(
        f"/api/v1/chat/conversations/{conversation.id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "Yes, create it"},
    )

    assert response.status_code == 200

    # Verify task was created via Phase-II API
    tasks = await get_user_tasks(user.id)
    assert len(tasks) > 0
    task = tasks[0]
    assert task["title"] == "Buy groceries"
    assert task["priority"] == "high"

@pytest.mark.asyncio
async def test_list_tasks_via_chat():
    """Test US2: List and filter tasks"""
    # Create test user with tasks
    user = await create_test_user()
    await create_test_tasks(user.id, count=5)
    token = generate_test_jwt(user.id)
    conversation = await create_test_conversation(user.id)

    # Ask to list tasks
    response = await client.post(
        f"/api/v1/chat/conversations/{conversation.id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "Show me my tasks"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    # Response should list tasks
    assert any(len(data["assistant_message"]) > 0)

@pytest.mark.asyncio
async def test_cross_user_isolation():
    """Test US7: User isolation"""
    user_a = await create_test_user(email="a@test.com")
    user_b = await create_test_user(email="b@test.com")

    conversation_a = await create_test_conversation(user_a.id)
    token_b = generate_test_jwt(user_b.id)

    # User B tries to access User A's conversation
    response = await client.post(
        f"/api/v1/chat/conversations/{conversation_a.id}/messages",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"content": "Show me messages"},
    )

    # Should return 403 Forbidden
    assert response.status_code == 403
    assert "permission" in response.json()["error"]["message"].lower()

@pytest.mark.asyncio
async def test_delete_confirmation_required():
    """Test US5: Delete requires confirmation"""
    # Create task
    user = await create_test_user()
    task = await create_test_task(user.id, title="To Delete")
    token = generate_test_jwt(user.id)
    conversation = await create_test_conversation(user.id)

    # Ask to delete without confirmation
    response = await client.post(
        f"/api/v1/chat/conversations/{conversation.id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "Delete the task"},
    )

    # Agent should ask for confirmation
    assert response.status_code == 200
    data = response.json()["data"]
    assert "confirm" in data["assistant_message"].lower() or "sure" in data["assistant_message"].lower()

    # Task should still exist (not deleted yet)
    existing_task = await get_task(user.id, task.id)
    assert existing_task is not None

    # User confirms deletion
    response = await client.post(
        f"/api/v1/chat/conversations/{conversation.id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "Yes, delete it"},
    )

    assert response.status_code == 200

    # Task should be deleted
    existing_task = await get_task(user.id, task.id)
    assert existing_task is None

@pytest.mark.asyncio
async def test_conversation_persistence():
    """Test US6: Conversation persists across refresh"""
    user = await create_test_user()
    conversation = await create_test_conversation(user.id)
    token = generate_test_jwt(user.id)

    # Send 5 messages
    messages_sent = []
    for i in range(5):
        response = await client.post(
            f"/api/v1/chat/conversations/{conversation.id}/messages",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": f"Message {i+1}"},
        )
        messages_sent.append(response.json()["data"]["user_message"])

    # Simulate "refresh": Load conversation from DB
    response = await client.get(
        f"/api/v1/chat/conversations/{conversation.id}/messages",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    messages_loaded = response.json()["data"]["messages"]

    # Verify all messages are present
    assert len(messages_loaded) >= 5
    for msg in messages_sent:
        assert any(msg in m["content"] for m in messages_loaded)
```

### Security Tests

```python
# backend/tests/security/test_isolation.py

@pytest.mark.asyncio
async def test_jwt_validation_missing_token():
    """Test 401 on missing JWT"""
    response = await client.post(
        "/api/v1/chat/conversations/some-id/messages",
        json={"content": "Hello"},
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_jwt_validation_invalid_signature():
    """Test 401 on invalid JWT signature"""
    response = await client.post(
        "/api/v1/chat/conversations/some-id/messages",
        headers={"Authorization": "Bearer invalid.token.here"},
        json={"content": "Hello"},
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_tool_user_id_injection():
    """Test that tools receive scoped user_id from JWT"""
    # This is a unit test for MCP tools
    user_id = UUID("12345678-1234-1234-1234-123456789012")

    # Mock: Tool receives user_id from JWT
    with patch.object(add_task, "execute") as mock_execute:
        await add_task(user_id=user_id, title="Test")

        # Verify user_id is the one from JWT
        call_args = mock_execute.call_args
        assert call_args.kwargs["user_id"] == user_id
```

### Performance Tests

```python
# backend/tests/performance/test_response_time.py

@pytest.mark.asyncio
async def test_chat_response_time():
    """Test that chat response is <3 seconds"""
    user = await create_test_user()
    conversation = await create_test_conversation(user.id)
    token = generate_test_jwt(user.id)

    start = time.time()
    response = await client.post(
        f"/api/v1/chat/conversations/{conversation.id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "Create a task"},
    )
    elapsed = time.time() - start

    assert response.status_code == 200
    assert elapsed < 3.0, f"Response took {elapsed}s, expected <3s"

@pytest.mark.asyncio
async def test_conversation_history_loading():
    """Test that history loads quickly even with 100+ messages"""
    user = await create_test_user()
    conversation = await create_test_conversation(user.id)

    # Create 100 messages
    for i in range(100):
        await create_message(conversation.id, user.id, f"Message {i}")

    start = time.time()
    response = await client.get(
        f"/api/v1/chat/conversations/{conversation.id}/messages",
        headers={"Authorization": f"Bearer {generate_test_jwt(user.id)}"},
    )
    elapsed = time.time() - start

    assert response.status_code == 200
    assert elapsed < 1.0, f"History load took {elapsed}s, expected <1s"
```

### Regression Tests

Ensure all Phase-II tests still pass:

```bash
# Run existing Phase-II tests
pytest backend/tests/integration/test_create_task.py -v
pytest backend/tests/integration/test_list_tasks.py -v
pytest backend/tests/integration/test_update_task.py -v
pytest backend/tests/integration/test_complete_task.py -v
pytest backend/tests/integration/test_delete_task.py -v

# Expect: All tests pass, zero failures
```

---

## Risk Analysis & Mitigation

### Risk 1: OpenAI API Token Limits & Cost

**Severity**: High
**Probability**: Medium
**Blast Radius**: Service degradation, budget overruns

**Risk Description**:
- OpenAI API has rate limits (requests/minute, tokens/minute)
- Each user message consumes tokens (input + output)
- Token window of 20 messages per conversation could still be 5-10k tokens
- At scale (100+ concurrent users), could hit rate limits
- Cost could be unpredictable if tool calls fail and retry

**Mitigation**:
1. **Implement Rate Limiting**:
   - Limit to 10 messages per user per minute
   - Return 429 Too Many Requests if exceeded

2. **Token Budget Tracking**:
   - Log tokens used per message
   - Alert if daily usage exceeds threshold
   - Implement token quotas per user

3. **Graceful Degradation**:
   - If OpenAI API unavailable, return: "I'm temporarily offline. Try again in a moment."
   - Continue storing messages (don't lose data)

4. **Cost Controls**:
   - Set OpenAI API spending limits in dashboard
   - Use lower-cost model (gpt-3.5-turbo) for non-critical scenarios
   - Compress conversation history (summarize old messages)

**Implementation**:
```python
# backend/src/services/rate_limiter.py

async def check_rate_limit(user_id: UUID) -> bool:
    """Check if user has exceeded message rate limit"""
    key = f"chat:messages:{user_id}"
    count = await redis.incr(key)

    if count == 1:
        await redis.expire(key, 60)  # Reset after 60 seconds

    if count > 10:  # Max 10 messages per minute
        raise RateLimitedException("Too many messages. Please wait a moment.")

    return True
```

---

### Risk 2: Cross-User Data Leakage via AI

**Severity**: Critical
**Probability**: Low (if implemented correctly)
**Blast Radius**: Privacy violation, legal liability

**Risk Description**:
- AI agent has access to user_id via tool calls
- If JWT validation fails, agent could execute tools for wrong user
- If tool doesn't properly scope by user_id, could return another user's tasks
- Message metadata could leak user information

**Mitigation**:
1. **Strict JWT Validation**:
   - Middleware validates JWT before any request processing
   - Raises 401 if JWT missing/invalid
   - Extracts user_id, doesn't trust user input

2. **Tool-Level Scoping**:
   - Every tool receives user_id from JWT (not user input)
   - Tools never accept user_id as parameter (hardcoded injection)
   - Query filtering: `WHERE user_id = :extracted_user_id`

3. **Database-Level Isolation**:
   - Foreign key constraints enforce relationships
   - Indexes on (user_id, conversation_id) for efficient filtering

4. **Audit Logging**:
   - Log all tool executions with user_id
   - Flag suspicious patterns (same tool called 100x in 1 second)

**Testing**:
```python
@pytest.mark.asyncio
async def test_tool_cannot_access_other_users_tasks():
    """Verify tool strictly scopes by authenticated user_id"""
    user_a = create_user("a@test.com")
    user_b = create_user("b@test.com")
    task_a = create_task(user_a.id, "Task A")

    # User B's JWT
    token_b = generate_jwt(user_b.id)

    # Even if User B somehow calls tool with User A's user_id,
    # the middleware should have already validated and injected correct user_id
    # So this scenario shouldn't happen. But let's verify anyway:

    # Call tool directly (bypassing middleware for testing)
    result = await list_tasks(user_id=user_b.id)

    # Should only see User B's tasks, never User A's
    assert task_a not in result
    assert all(t.user_id == user_b.id for t in result)
```

---

### Risk 3: Conversation History Explosion

**Severity**: Medium
**Probability**: High
**Blast Radius**: Database growth, token window inefficiency

**Risk Description**:
- Each message (user + assistant) is stored
- Long conversations accumulate 100+ messages
- Loading full history into agent could exceed token limit
- Database could grow to GB+ sizes
- Queries become slower over time

**Mitigation**:
1. **Token Window Management** (already in design):
   - Only load last 20 messages into agent context
   - Full history remains in database (searchable, archived)

2. **Conversation Archival**:
   - After 30 days of inactivity, mark conversation as archived
   - Archived conversations not loaded by default
   - Can still be retrieved via API

3. **Database Optimization**:
   - Partition messages table by user_id or date
   - Regular index maintenance
   - Soft deletes (deleted_at) for GDPR compliance

4. **Retention Policy**:
   - Delete conversations older than 1 year
   - Allow users to export conversation history before deletion

**Implementation**:
```python
# backend/src/tasks/archive_conversations.py (Celery task)

@celery_app.task
async def archive_old_conversations():
    """Archive conversations inactive for 30 days"""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Find inactive conversations
    result = await session.exec(
        select(Conversation).where(
            Conversation.updated_at < thirty_days_ago
        )
    )

    for conversation in result:
        conversation.archived_at = datetime.utcnow()

    await session.commit()
```

---

### Risk 4: Agent Hallucination or Incorrect Tool Calls

**Severity**: Medium
**Probability**: Medium
**Blast Radius**: User frustration, unintended task modifications

**Risk Description**:
- Agent might misunderstand user intent
- Could call wrong tool (e.g., delete instead of update)
- Could pass incorrect parameters (wrong priority, due date)
- User expects AI to be accurate, but LLMs can hallucinate

**Mitigation**:
1. **Confirmation Gates** (already in design):
   - Before any write operation, agent summarizes and asks confirmation
   - Read-only operations (list_tasks) don't require confirmation
   - Destructive operations (delete) require explicit "yes"

2. **Parameter Validation**:
   - Tool schema enforces constraints
   - Invalid parameters rejected before execution
   - Error message explains what went wrong

3. **Clarification Prompts**:
   - If user reference is ambiguous ("that task"), ask for clarification
   - Show options: "Did you mean: [list]?"
   - Require explicit task selection

4. **Rollback Capability**:
   - User can "undo" recent actions via chat
   - "Undo the last task creation" → delete just-created task
   - Messages still stored for audit trail

**System Prompt Design**:
```python
def _get_system_prompt(self) -> str:
    return """You are a cautious task management assistant.

SAFETY FIRST:
1. Always confirm before CREATE, UPDATE, or DELETE operations
2. If user reference is ambiguous, ask for clarification
3. Summarize what you're about to do before doing it
4. If user says "no" or "cancel", DO NOT execute the tool

CONFIRMATION EXAMPLES:
- Before create: "I'll create a task: 'Buy groceries' (priority: high, due: tomorrow). Sound good? Say yes to confirm."
- Before delete: "This is permanent! Delete 'Old task'? Please say 'yes' to confirm."
- Before update: "I'll change the priority of 'My task' from medium to high. Confirm?"

CLARIFICATION EXAMPLES:
- If ambiguous: "I see multiple tasks. Which one did you mean: [1] Task A [2] Task B?"
- If missing info: "Got it! I need a title for the task. What's it about?"
"""
```

---

### Risk 5: Phase-II API Changes Break MCP Tools

**Severity**: High
**Probability**: Low (if governance is strong)
**Blast Radius**: Chatbot broken, need urgent tool fixes

**Risk Description**:
- Phase-II API endpoints could change (breaking change)
- Tool implementations depend on Phase-II endpoint contracts
- If endpoint removed or signature changes, tools fail
- Users see "error creating task" without context

**Mitigation**:
1. **API Versioning**:
   - Phase-II endpoints use `/api/v1/` prefix
   - Any breaking changes go to `/api/v2/`
   - Tools can support both versions if needed

2. **MCP Tool Abstraction**:
   - Don't call Phase-II directly; use a `TaskService` layer
   - TaskService encapsulates HTTP calls
   - If Phase-II API changes, only TaskService needs updates

3. **Monitoring & Alerts**:
   - Monitor Phase-II API health
   - Alert if tools fail > 5 times in 5 minutes
   - Graceful degradation (return friendly error)

4. **Testing**:
   - Regression tests verify tools still work
   - Contract tests ensure tool ↔ Phase-II API alignment
   - Run tests on every Phase-II release

**Implementation**:
```python
# backend/src/services/task_service.py (abstraction layer)

class TaskService:
    """Abstraction over Phase-II task APIs"""

    async def create_task(self, user_id: UUID, **kwargs) -> Task:
        """Create task via Phase-II endpoint"""
        # Implementation detail: which endpoint, how to call it
        # If Phase-II changes, only this class needs updates
        return await self._call_phase2_api(
            method="POST",
            endpoint=f"/api/v1/{user_id}/tasks",
            json=kwargs,
        )
```

---

## Effort Estimation

### Timeline Summary

| Phase | Duration | Effort (Engineer-Days) | Dependencies |
|-------|----------|------------------------|--------------|
| 1: Database Schema | 2 days | 1.5 | None |
| 2: MCP Server & Tools | 4 days | 3 | Phase 1 |
| 3: Chat Endpoint & Agent | 5 days | 4 | Phase 1, 2 |
| 4: Chat UI Widget | 3 days | 2.5 | Phase 3 |
| 5: Testing & Security | 4 days | 3 | All |
| **Total** | **18 days** | **14 engineer-days** | — |

### Parallelization Opportunities

**Can be done in parallel**:
- Phase 2 & early Phase 3 can overlap (MCP tools stubbed, endpoint started)
- Phase 4 (UI) can start once Phase 3 endpoints are defined (before implementation)
- Phase 5 tests can be written as Phase 3 code is implemented (TDD)

**Optimized Timeline** (with parallelization):
- Days 1-2: Phase 1 (Database) + Phase 2 start (MCP schemas)
- Days 2-6: Phase 2 (MCP tools) + Phase 3 (Chat endpoint) in parallel
- Days 4-6: Phase 4 (UI) based on Phase 3 interface
- Days 5-7: Phase 5 (Testing) running continuously
- **Total: 7-8 days wall time** (2-3 engineers)

### Resource Requirements

**Backend Engineer** (3-4 days):
- Database schema + migrations
- OpenAI Agents SDK integration
- Chat endpoint implementation
- MCP tool wrappers

**Full Stack Engineer** (4-5 days):
- MCP tool implementations (calling Phase-II APIs)
- Integration with FastAPI
- Testing framework and test cases
- Monitoring and observability

**Frontend Engineer** (2-3 days):
- ChatWidget component
- Chat UI (messages, input, animations)
- Integration with Phase-II layout
- Mobile responsiveness

**QA / Security Engineer** (2-3 days):
- Security testing (JWT, isolation, SQL injection)
- Performance testing (response time, concurrency)
- Regression testing (Phase-II)
- Test coverage reporting

---

## Success Criteria Mapping

| SC-ID | Criterion | How Achieved | Validation |
|-------|-----------|--------------|-----------|
| SC-001 | Task creation <90s (5-6 turn dialogue) | Multi-turn agent with confirmation gates | Timing test in integration suite |
| SC-002 | 95% tasks appear in UI within 1s without refresh | Immediate Phase-II API call + response to frontend | Performance test + manual verification |
| SC-003 | 100% message recovery across refresh/restart | Database-backed conversation storage | Persistence test (close/reopen browser) |
| SC-004 | Natural language filters with zero false positives | list_tasks tool with client-side filtering + agent reasoning | Filter test against Phase-II API results |
| SC-005 | Updates visible in UI within 1s | Immediate Phase-II PATCH call | Performance test + real-time verification |
| SC-006 | 100% accidental deletion prevention | Agent requires explicit "yes" before delete_task | Confirmation flow test |
| SC-007 | Zero cross-user data leaks | JWT validation + user_id scoping in all queries | Security test (User B accesses User A's data) |
| SC-008 | Response time 2-3s (p95) | Efficient agent + optimized tool calls | Load test with 100 concurrent users |
| SC-009 | Widget load <500ms impact | Lazy load ChatWidget; async initialization | Lighthouse performance audit |
| SC-010 | 90% user intuitivity | Clean UI + agent guidance + onboarding message | User testing (optional) + usability review |
| SC-011 | 70% test coverage | Unit + integration + security tests | Coverage report via pytest-cov |
| SC-012 | Zero Phase-II regression | Run all Phase-II tests after Phase-III | Test suite green light |

---

## Architecture Decision Records (ADRs)

The following decisions warrant ADRs:

1. **ADR-001**: Stateless Backend with Database Persistence
   - Decision: No in-memory conversation state; all data to Neon PostgreSQL
   - Alternatives: Redis cache (faster but stateful), In-memory (no persistence)
   - Rationale: Enables horizontal scaling, survives server restarts, auditable

2. **ADR-002**: OpenAI Agents SDK (not LangChain / Anthropic)
   - Decision: Use OpenAI Agents SDK for multi-turn agent
   - Alternatives: LangChain, Anthropic SDK, custom loop
   - Rationale: Native tool support, minimal wrapper code, built-in error handling

3. **ADR-003**: MCP-First Architecture (AI never queries database directly)
   - Decision: All task operations flow through MCP tools → Phase-II APIs
   - Alternatives: Direct database access, parallel API calls
   - Rationale: No duplicate CRUD logic, single source of truth (Phase-II), easier auditing

4. **ADR-004**: JWT-Scoped User Isolation (403 Forbidden, not 404)
   - Decision: Use 403 for cross-user access; never expose 404
   - Alternatives: Return 404 for both "not found" and "forbidden"
   - Rationale: Security best practice (don't leak resource existence)

5. **ADR-005**: Token Window of 20 Messages
   - Decision: Load only last 20 messages into agent context
   - Alternatives: Full conversation, sliding window, message summarization
   - Rationale: Balances context quality with token efficiency and cost

---

## Conclusion

This architecture provides a comprehensive, production-ready design for Phase-III AI Chatbot. Key highlights:

1. **Stateless & Scalable**: No server-side session state; horizontal scaling enabled
2. **Secure & Isolated**: JWT validation, user_id scoping, 403 for forbidden resources
3. **Zero Phase-II Changes**: Reuses existing APIs; Phase-II can evolve independently
4. **Well-Tested**: 70%+ coverage, security tests, performance benchmarks, regression tests
5. **User-Centric**: Multi-turn dialogue, confirmation gates, graceful error handling

**Next Steps**:
1. Confirm clarifications (token window, chat history pagination, timeout behavior)
2. Create ADRs for major decisions
3. Break into detailed tasks via `/sp.tasks`
4. Begin Phase 1 (Database) immediately
5. Parallel Phase 2 & 3 once Phase 1 complete

---

**Document Status**: Ready for Technical Review
**Last Updated**: 2026-02-07
