# Phase-III: Todo AI Chatbot

## Overview

**Phase**: Phase-III
**Title**: Todo AI Chatbot
**Status**: Specification Complete

## Objective

Enable natural language todo management through a conversational AI interface. Users can create, view, update, complete, and delete tasks by simply describing their intent in plain English, without needing to navigate forms or understand specific commands.

## Technology Stack

- **OpenAI ChatKit**: Conversational interface framework
- **OpenAI Agents SDK**: Agent orchestration and tool calling
- **MCP SDK**: Model Context Protocol for tool integration
- **FastAPI**: Backend API framework
- **Neon PostgreSQL**: Database for tasks and conversation history

## Key Architecture Principles

### Stateless Chat Design

The chat interface is stateless at the application level:
- Each request is independent and self-contained
- No in-memory session state maintained between requests
- All context retrieved from database on each interaction

### Database-Driven Conversation State

Conversation continuity is achieved through persistent storage:
- Conversation history stored in Neon PostgreSQL
- Each message (user + AI response) persisted immediately
- Context retrieved from database before processing each new message
- Supports multiple concurrent conversation threads per user

## Core Features

1. **Natural Language Task Creation**: Users describe tasks conversationally
2. **Task Status Inquiry**: Users ask about their tasks in plain language
3. **Task Completion**: Mark tasks done through conversation
4. **Task Modification**: Update task details via natural language
5. **Task Deletion**: Remove tasks through conversational requests

## Integration Points

- **Phase-II Authentication**: Leverages existing Better Auth JWT system
- **Phase-II Task API**: Extends existing task CRUD operations
- **Phase-II Database**: Uses existing Neon PostgreSQL instance

## Success Metrics

- Task creation in under 10 seconds
- 90% intent recognition accuracy
- 85% first-attempt success rate
- Sub-3-second response times

## Documentation

- **Feature Specification**: `specs/001-todo-ai-chatbot/spec.md`
- **MCP Tools**: `specs/phase-iii/mcp-tools.md`
- **Chat Endpoint**: `specs/phase-iii/chat-endpoint.md`
