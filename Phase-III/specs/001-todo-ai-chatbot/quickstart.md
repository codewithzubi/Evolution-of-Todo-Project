# Quickstart Guide: Todo AI Chatbot (Phase-III)

**Feature**: 001-todo-ai-chatbot
**Prerequisites**: Phase-II setup complete (Next.js frontend + FastAPI backend + Neon PostgreSQL)

## Overview

This guide walks you through setting up the Phase-III AI chatbot feature for natural language todo management. The chatbot uses OpenAI Agents SDK with MCP tools to enable conversational task operations.

## Prerequisites

Before starting, ensure you have:

- ✅ Phase-II application running (frontend + backend)
- ✅ Neon PostgreSQL database configured
- ✅ Better Auth authentication working
- ✅ Node.js 18+ and Python 3.13+ installed
- ✅ OpenAI API account with API key

## Step 1: Environment Variables

Add the following to your `.env` files:

### Backend `.env`

```bash
# Existing Phase-II variables
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256

# NEW: Phase-III variables
OPENAI_API_KEY=sk-...  # Your OpenAI API key
OPENAI_MODEL=gpt-4     # Or gpt-3.5-turbo for development
```

### Frontend `.env.local`

```bash
# Backend API URL (use your deployed backend URL or localhost for development)
NEXT_PUBLIC_API_URL=https://your-backend-url.hf.space
# For local development: NEXT_PUBLIC_API_URL=http://localhost:8000

# Authentication secret (must match backend)
BETTER_AUTH_SECRET=your-32-character-secret-key-here

# Better Auth URL (your frontend URL)
BETTER_AUTH_URL=http://localhost:3000

# NEW: Phase-III variables
NEXT_PUBLIC_CHAT_ENABLED=true
```

## Step 2: Install Dependencies

### Backend Dependencies

```bash
cd backend

# Install OpenAI and MCP SDKs
uv add openai mcp dateparser

# Install development dependencies
uv add --dev pytest-asyncio httpx
```

**Expected `pyproject.toml` additions**:
```toml
[project]
dependencies = [
    # ... existing dependencies
    "openai>=1.0.0",
    "mcp>=0.1.0",
    "dateparser>=1.2.0"
]
```

### Frontend Dependencies

```bash
cd frontend

# Install ChatKit and related packages
npm install @openai/chatkit

# Or with yarn
yarn add @openai/chatkit
```

**Expected `package.json` additions**:
```json
{
  "dependencies": {
    "@openai/chatkit": "^1.0.0"
  }
}
```

## Step 3: Database Migration

Run the Alembic migration to add conversation tables:

```bash
cd backend

# Generate migration (if not already created)
alembic revision --autogenerate -m "Add conversation and message tables for Phase-III"

# Review the generated migration in alembic/versions/
# Ensure it creates:
# - conversations table (id, user_id, created_at, updated_at)
# - messages table (id, conversation_id, user_id, role, content, tools_used, created_at)
# - All indexes and foreign keys

# Apply migration
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Should show: conversations, messages tables
```

**Migration Rollback** (if needed):
```bash
alembic downgrade -1
```

## Step 4: Backend Setup

### 4.1 Create Database Models

Create `backend/app/models/conversation.py`:

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    messages: List["Message"] = Relationship(back_populates="conversation")
```

Create `backend/app/models/message.py`:

```python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text, JSON
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    role: str = Field(sa_column_kwargs={"check": "role IN ('user', 'assistant')"})
    content: str = Field(sa_column=Column(Text))
    tools_used: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    conversation: Conversation = Relationship(back_populates="messages")
```

### 4.2 Create MCP Tools

Create `backend/app/services/mcp_server.py`:

```python
from mcp import MCPServer
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

mcp_server = MCPServer()

class AddTaskParams(BaseModel):
    user_id: UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None

@mcp_server.tool()
async def add_task(params: AddTaskParams) -> dict:
    # TODO: Implement using existing task service
    pass

# TODO: Implement remaining 4 tools (list_tasks, complete_task, update_task, delete_task)
```

### 4.3 Create Chat Service

Create `backend/app/services/chat_service.py`:

```python
from openai import AsyncOpenAI
from sqlmodel import Session, select
from uuid import UUID
from typing import Optional, List

class ChatService:
    def __init__(self, openai_client: AsyncOpenAI, db: Session):
        self.client = openai_client
        self.db = db

    async def process_message(
        self,
        user_id: UUID,
        message: str,
        conversation_id: Optional[UUID] = None
    ) -> dict:
        # TODO: Implement chat processing logic
        # 1. Get or create conversation
        # 2. Save user message
        # 3. Fetch conversation history
        # 4. Call OpenAI agent with MCP tools
        # 5. Save assistant response
        # 6. Return response
        pass
```

### 4.4 Create Chat Endpoint

Create `backend/app/api/routes/chat.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

router = APIRouter(prefix="/api", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID] = None

class ChatResponse(BaseModel):
    success: bool
    conversation_id: UUID
    response: str
    timestamp: str
    tools_used: list[str]
    context: dict

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user = Depends(get_current_user)
):
    # TODO: Implement endpoint logic
    pass
```

## Step 5: Frontend Setup

### 5.1 Create Chat Components

Create `frontend/components/chat/ChatInterface.tsx`:

```typescript
'use client'

import { ChatInterface as ChatKitInterface } from '@openai/chatkit'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export function ChatInterface() {
  const sendMessage = useMutation({
    mutationFn: async (message: string) => {
      return apiClient.post('/api/chat', { message })
    }
  })

  return (
    <ChatKitInterface
      onSendMessage={sendMessage.mutate}
      className="bg-background text-foreground"
    />
  )
}
```

Create `frontend/components/chat/ChatButton.tsx`:

```typescript
'use client'

import { MessageSquare } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useState } from 'react'
import { ChatInterface } from './ChatInterface'

export function ChatButton() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <Button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 rounded-full"
        size="lg"
      >
        <MessageSquare className="h-6 w-6" />
      </Button>

      {isOpen && (
        <div className="fixed bottom-20 right-4 w-96 h-[600px] bg-card border rounded-lg shadow-lg">
          <ChatInterface />
        </div>
      )}
    </>
  )
}
```

### 5.2 Add Chat to Dashboard

Update `frontend/app/dashboard/page.tsx`:

```typescript
import { ChatButton } from '@/components/chat/ChatButton'

export default function DashboardPage() {
  return (
    <div>
      {/* Existing dashboard content */}

      {/* NEW: Add chat button */}
      <ChatButton />
    </div>
  )
}
```

### 5.3 Update API Client

Update `frontend/lib/api-client.ts`:

```typescript
// Add chat methods
export const apiClient = {
  // ... existing methods

  async sendChatMessage(message: string, conversationId?: string) {
    return fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify({ message, conversation_id: conversationId })
    }).then(res => res.json())
  }
}
```

## Step 6: Running Locally

### Start Backend

```bash
cd backend

# Activate virtual environment (if using venv)
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Run FastAPI server
uvicorn app.main:app --reload --port 8000

# Server should start at http://localhost:8000
# Check health: curl http://localhost:8000/health
```

### Start Frontend

```bash
cd frontend

# Run Next.js development server
npm run dev
# or
yarn dev

# Server should start at http://localhost:3000
```

### Verify Setup

1. Open browser to `http://localhost:3000`
2. Login with existing Phase-II credentials
3. Navigate to dashboard
4. Click chat button (bottom-right corner)
5. Send test message: "Add a task to test the chatbot"
6. Verify task is created and AI responds

## Step 7: Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_mcp_tools.py

# Run with coverage
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm run test
# or
yarn test

# Run E2E tests
npm run test:e2e
# or
yarn test:e2e
```

## Step 8: Example Conversations

Try these example messages to test the chatbot:

### Create Task
- "Add a task to buy groceries tomorrow"
- "Create a task: finish the report by Friday"
- "Remind me to call the dentist"

### View Tasks
- "What tasks do I have?"
- "Show me my incomplete tasks"
- "List all my tasks"

### Complete Task
- "I finished buying groceries"
- "Mark the report task as done"
- "Complete the dentist task"

### Update Task
- "Change the due date of my report to next Monday"
- "Rename the shopping task to grocery shopping"
- "Add a note to the report: needs executive summary"

### Delete Task
- "Delete the grocery task"
- "Remove the dentist task"
- "Delete all completed tasks"

## Troubleshooting

### Issue: OpenAI API Key Invalid

**Error**: `401 Unauthorized` from OpenAI API

**Solution**:
1. Verify API key in `.env`: `OPENAI_API_KEY=sk-...`
2. Check API key is active in OpenAI dashboard
3. Restart backend server after updating `.env`

### Issue: Database Migration Fails

**Error**: `alembic.util.exc.CommandError`

**Solution**:
1. Check database connection: `psql $DATABASE_URL`
2. Verify Alembic is initialized: `alembic current`
3. Reset migrations if needed: `alembic downgrade base && alembic upgrade head`

### Issue: Chat Button Not Appearing

**Error**: Chat button not visible in dashboard

**Solution**:
1. Verify ChatButton imported in dashboard page
2. Check browser console for errors
3. Ensure `NEXT_PUBLIC_CHAT_ENABLED=true` in `.env.local`
4. Restart frontend server

### Issue: CORS Error

**Error**: `Access-Control-Allow-Origin` error in browser console

**Solution**:
1. Verify CORS middleware in `backend/app/main.py`
2. Add frontend origin to allowed origins:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
3. Restart backend server

### Issue: MCP Tools Not Found

**Error**: `Tool 'add_task' not found`

**Solution**:
1. Verify MCP server initialized in FastAPI startup
2. Check tools registered: `mcp_server.list_tools()`
3. Ensure MCP server passed to agent configuration

## Next Steps

1. **Implement TDD Cycle**: Follow Red-Green-Refactor for each component
2. **Run Tests**: Ensure all tests pass before proceeding
3. **Performance Testing**: Verify <2s response time
4. **Security Review**: Validate user_id filtering in all MCP tools
5. **Documentation**: Update API docs with chat endpoint

## Additional Resources

- **Spec**: `specs/001-todo-ai-chatbot/spec.md`
- **Plan**: `specs/001-todo-ai-chatbot/plan.md`
- **Research**: `specs/001-todo-ai-chatbot/research.md`
- **Contracts**: `specs/001-todo-ai-chatbot/contracts/`
- **Data Model**: `specs/phase-iii/data-model.md`
- **MCP Tools**: `specs/phase-iii/mcp-tools.md`
- **Chat Endpoint**: `specs/phase-iii/chat-endpoint.md`

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review spec and plan documents
3. Check constitution for architectural guidance
4. Consult Phase-II documentation for existing patterns
