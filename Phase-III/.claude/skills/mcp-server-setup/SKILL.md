# MCP Server Setup

## Purpose
Design and implement a stateless MCP (Model Context Protocol) server in FastAPI that exposes task management tools with proper user isolation and database persistence.

## Key Principles
- **Stateless Architecture**: No in-memory state; all state persists in PostgreSQL via SQLModel
- **User Isolation**: Enforce `user_id` from JWT tokens on all operations
- **Tool-First Design**: Expose task tools as MCP resources that agents can invoke
- **Official SDK**: Use the MCP SDK (https://github.com/anthropics/python-sdk) for all MCP operations

## Core Responsibilities

### 1. MCP Server Setup
- Initialize FastAPI application with MCP server endpoints
- Configure MCP SDK to expose tools as callable resources
- Set up proper request/response handling for MCP protocol

### 2. Task Tools Implementation
Expose the following MCP tools:
- **add**: Create a new task (title, description, priority)
- **list**: Retrieve tasks for authenticated user (with filtering/pagination)
- **update**: Modify existing task (title, description, priority, status)
- **complete**: Mark task as completed
- **delete**: Soft-delete or remove task

### 3. Database Integration
- Use SQLModel ORM for all database operations
- Connect to Neon serverless PostgreSQL
- Implement Task schema with `user_id` foreign key
- Ensure all queries filter by authenticated user

### 4. JWT Authentication & User Context
- Extract JWT token from request headers
- Validate token signature using shared secret
- Decode to get `user_id` claim
- Pass `user_id` context to all tool operations
- Reject requests with missing/invalid tokens (401)
- Reject cross-user access attempts (403)

### 5. Error Handling
- Return proper MCP error responses
- Distinguish between authentication (401), authorization (403), and validation (422) errors
- Log errors with correlation IDs
- Never expose internal details in error messages

## Implementation Workflow

1. **Setup FastAPI + MCP SDK**
   - Install MCP SDK and dependencies
   - Create FastAPI app with MCP server integration
   - Configure CORS, middleware, and error handlers

2. **Design SQLModel Schemas**
   - Create Task model with: id, user_id, title, description, priority, status, created_at, updated_at
   - Add proper indexes for user_id and created_at
   - Define relationships if needed (e.g., Task→User)

3. **Implement MCP Tools**
   - Create tool definitions for add, list, update, complete, delete
   - Each tool receives user_id from JWT context
   - Validate input and enforce user ownership
   - Return structured responses

4. **Wire Everything Together**
   - Create FastAPI endpoint that processes MCP requests
   - Extract JWT token and user_id
   - Route to appropriate tool handler
   - Return MCP-formatted responses

5. **Testing & Validation**
   - Test each tool with valid/invalid tokens
   - Verify user isolation (user A can't access user B's tasks)
   - Test error cases (missing fields, invalid operations)
   - Verify stateless behavior (restart server, data persists)

## Success Criteria
✅ MCP server starts and accepts requests
✅ All 5 tools (add, list, update, complete, delete) are callable
✅ User_id is enforced on every operation
✅ Cross-user access is rejected with 403
✅ Data persists across server restarts
✅ JWT validation works correctly
✅ Error responses follow MCP format
✅ No in-memory state; all data in PostgreSQL

## Related Components
- **FastAPI Backend**: Main server implementation
- **Neon Database**: PostgreSQL storage with SQLModel
- **JWT Auth**: Token validation and user context
- **Agents SDK**: Will consume these tools via MCP

## Notes
- Keep the MCP server stateless and focused on data access
- Business logic should be in tool handlers, not in FastAPI routes
- All user context flows through JWT claims
- Use connection pooling for database efficiency in serverless
