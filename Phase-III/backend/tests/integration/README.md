# Phase-III Integration Testing Guide

## Overview

Comprehensive integration testing suite for Phase-III AI Chatbot system. Tests verify:
- End-to-end chat workflows
- User isolation and security
- Database persistence
- MCP tool integration
- Error handling and recovery
- Performance benchmarks

## Test Suites (T366-T373)

### T366: Database Schema Integration Tests
**File**: `test_database_schema.py`

Tests for database layer including CRUD operations, user isolation, soft deletes, and indexes.

```bash
pytest test_database_schema.py -v
```

**Key Tests**:
- `TestConversationCRUD`: Create, read, update, delete conversations
- `TestUserIsolation`: User-scoped access control
- `TestMessageOrdering`: Message ordering and filtering
- `TestPerformanceIndexes`: Index query performance

**What It Tests**:
- Conversation persistence in database
- Message creation with proper timestamps
- Soft delete functionality (`deleted_at` field)
- User isolation via foreign keys
- Index performance (<200ms for 100+ records)
- JSON metadata storage (JSONB)

### T367: MCP Tool Integration Tests
**File**: `test_mcp_tools_integration.py`

Tests for OpenAI Agents SDK integration with Phase-II task API via MCP.

```bash
pytest test_mcp_tools_integration.py -v
```

**Key Tests**:
- `TestAddTaskTool`: Tool execution for adding tasks
- `TestListTasksTool`: Tool execution for listing tasks with filters
- `TestUpdateTaskTool`: Update task operations
- `TestCompleteTaskTool`: Mark tasks complete
- `TestDeleteTaskTool`: Soft delete tasks
- `TestToolErrorHandling`: Timeout and network errors

**What It Tests**:
- Each MCP tool (add_task, list_tasks, update_task, complete_task, delete_task)
- User isolation in tool calls
- Error handling (timeouts, network errors, malformed responses)
- Tool user scoping via JWT token

### T369: Chat Endpoint Integration Tests
**File**: `test_chat_endpoints_full.py`

End-to-end chat API tests including message handling and agent responses.

```bash
pytest test_chat_endpoints_full.py -v
```

**Key Tests**:
- `TestChatEndpointsEndToEnd`: Full conversation workflows
- `TestMessageEndpointsEndToEnd`: Message sending/receiving
- `TestErrorHandlingAndEdgeCases`: Error scenarios
- `TestChatWorkflowWithMocking`: Agent response mocking

**What It Tests**:
- Create conversation endpoint
- List conversations with pagination
- Send messages and receive agent responses
- Delete conversations (soft delete)
- User isolation between users
- Proper error responses

### T370: User Isolation & Security Tests
**File**: `test_user_isolation_security.py`

Security verification tests ensuring users cannot access each other's data.

```bash
pytest test_user_isolation_security.py -v
```

**Key Tests**:
- `TestUserConversationIsolation`: Users can't read other's conversations
- `TestUserMessageIsolation`: Users can't read other's messages
- `TestJWTAuthentication`: Token validation and expiration
- `TestDatabaseSecurityQueries`: WHERE user_id filters verified
- `TestErrorMessagesNoLeakage`: No sensitive info in errors

**What It Tests**:
- User A cannot read User B's conversations (403/404)
- User A cannot list User B's messages
- User A cannot delete User B's resources
- JWT token validation (missing, invalid, expired)
- Database queries properly filtered by user_id
- Error messages generic (not "owned by another user")

### T371: Conversation Persistence Tests
**File**: `test_persistence.py`

Data persistence and recovery tests.

```bash
pytest test_persistence.py -v
```

**Key Tests**:
- `TestConversationPersistence`: Conversation data persists
- `TestMessagePersistence`: Message data persists
- `TestLargeConversationPersistence`: Handles 100+ messages
- `TestSoftDeletePersistence`: Soft delete timestamps persist
- `TestMetadataPersistence`: JSON metadata preserved

**What It Tests**:
- Conversations persist across sessions
- Messages persist with correct ordering
- Soft-deleted records excluded from queries
- Complex JSON metadata preserved exactly
- Large conversations (100+ messages) remain fast
- Atomic updates (all fields updated together)

### T372: Error Handling & Recovery Tests
**File**: `test_error_handling.py`

Error handling and graceful degradation tests.

```bash
pytest test_error_handling.py -v
```

**Key Tests**:
- `TestNetworkErrorHandling`: Connection failures
- `TestTimeoutHandling`: Slow operations
- `TestRateLimitHandling`: 429 responses
- `TestAPIResponseValidation`: Malformed responses
- `TestGracefulDegradation`: Service continues despite failures
- `TestErrorResponseFormats`: Consistent error format

**What It Tests**:
- Network error handling (503, 500)
- API timeouts (>10s)
- Rate limiting with backoff
- Malformed JSON responses
- Missing required response fields
- Error responses follow standard format
- Services degrade gracefully

### T373: Performance & Benchmark Tests
**File**: `test_performance.py`

Performance benchmarking and scalability tests.

```bash
pytest test_performance.py -v -s
```

**Key Tests**:
- `TestChatResponseTime`: <3 second response time
- `TestConversationQueryPerformance`: <200ms list queries
- `TestMessageQueryPerformance`: <200ms message queries
- `TestDatabaseIndexPerformance`: Indexes working correctly
- `TestConcurrentUserHandling`: 10+ users simultaneously
- `TestMemoryAndScalability`: 1000+ messages handling

**Performance Targets**:
- Single message response: < 3 seconds (p95)
- Conversation listing: < 200ms (p95)
- Message listing: < 200ms (p95)
- 10 concurrent creates: < 5 seconds total
- 1000 message queries: < 200ms per page

## Running Tests

### Prerequisites
```bash
cd backend
pip install -r requirements.txt
```

### Run All Integration Tests
```bash
pytest tests/integration/ -v
```

### Run Specific Test Suite
```bash
pytest tests/integration/test_database_schema.py -v
pytest tests/integration/test_user_isolation_security.py -v
pytest tests/integration/test_performance.py -v -s
```

### Run With Coverage
```bash
pytest tests/integration/ -v --cov=src --cov-report=html
```

### Run Specific Test Class
```bash
pytest tests/integration/test_user_isolation_security.py::TestUserConversationIsolation -v
```

### Run Single Test
```bash
pytest tests/integration/test_database_schema.py::TestConversationCRUD::test_create_conversation -v
```

### Run Performance Tests Only
```bash
pytest tests/integration/test_performance.py -v -s --tb=short
```

## Test Environment Setup

### Database
- Uses SQLite in-memory database (`:memory:`)
- Schema created fresh for each test session
- Database fixtures in `conftest.py`

### Authentication
- JWT tokens generated with test secret from `settings.jwt_secret`
- Sample tokens: `create_token(user_id)` helper function
- Tokens include: user_id, email, exp (24 hours from now)

### Mocking
- Phase-II API calls mocked with `patch("src.mcp.tools._call_phase2_api")`
- OpenAI Agents SDK mocked with `patch("src.services.message_service.AgentExecutor")`
- Real database used (not mocked)

## Key Fixtures

### User Fixtures
```python
@pytest.fixture
async def test_user(test_session: AsyncSession, test_user_id: UUID):
    """Creates User in database for FK constraints"""

@pytest.fixture
async def other_user(test_session: AsyncSession, other_user_id: UUID):
    """Creates second user for isolation testing"""
```

### Conversation Fixtures
```python
@pytest.fixture
async def sample_conversation(test_session: AsyncSession, test_user):
    """Creates conversation for test_user"""

@pytest.fixture
async def user_a_conversation(test_session: AsyncSession, test_user):
    """User A's conversation"""

@pytest.fixture
async def user_b_conversation(test_session: AsyncSession, other_user):
    """User B's conversation (different user)"""
```

### Message Fixtures
```python
@pytest.fixture
async def sample_message(test_session: AsyncSession, test_user, sample_conversation):
    """Creates sample message in conversation"""
```

### JWT Token Fixtures
```python
@pytest.fixture
def test_user_id() -> UUID:
    """Test user ID"""

@pytest.fixture
def test_jwt_token(test_user_id: UUID) -> str:
    """Valid JWT token for test_user"""

@pytest.fixture
def auth_headers(test_jwt_token: str) -> dict:
    """Authorization headers with token"""
```

## Common Test Patterns

### Testing User Isolation
```python
def test_user_a_cannot_read_user_b_conversation(self, client, valid_token, other_user_token):
    # User B creates conversation
    resp = client.post(
        "/api/v1/chat/conversations",
        json={"title": "Private"},
        headers={"Authorization": f"Bearer {other_user_token}"}
    )
    user_b_conv_id = resp.json()["data"]["id"]

    # User A tries to access (should fail)
    resp = client.get(
        f"/api/v1/chat/conversations/{user_b_conv_id}",
        headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert resp.status_code == 404  # Not found in User A's scope
```

### Testing Database Persistence
```python
@pytest.mark.asyncio
async def test_conversation_persists(self, test_session: AsyncSession, test_user: User):
    # Create
    conv = Conversation(user_id=test_user.id, title="Persistent")
    test_session.add(conv)
    await test_session.commit()
    conv_id = conv.id

    # Retrieve
    stmt = select(Conversation).where(Conversation.id == conv_id)
    result = await test_session.execute(stmt)
    retrieved = result.scalar_one_or_none()

    assert retrieved is not None
    assert retrieved.title == "Persistent"
```

### Testing Performance
```python
def test_response_time_under_3s(self, client, valid_token):
    start = time.time()
    resp = client.get(
        "/api/v1/chat/conversations",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    elapsed = time.time() - start

    assert elapsed < 3.0, f"Took {elapsed}s"
```

## Expected Test Results

### Full Test Run Output
```
tests/integration/test_database_schema.py::TestConversationCRUD::test_create_conversation PASSED [ 1%]
tests/integration/test_database_schema.py::TestConversationCRUD::test_read_conversation PASSED [ 2%]
...
tests/integration/test_performance.py::TestChatResponseTime::test_single_message_response_time PASSED [ 98%]
tests/integration/test_performance.py::TestConcurrentUserHandling::test_10_concurrent_users_creating_conversations PASSED [ 99%]

========================= 200+ passed in 45.23s =========================
```

## Troubleshooting

### Tests Failing with "Conversation not found"
**Issue**: User FK constraint - database missing test users
**Solution**: Fixtures now create users first. Ensure conftest.py is in tests/ directory

### Tests Hanging on Async Operations
**Issue**: AsyncSession not properly closed
**Solution**: Use `@pytest.mark.asyncio` decorator and proper await statements

### JWT Token Validation Failures
**Issue**: Token created with wrong algorithm or secret
**Solution**: Use `settings.jwt_secret` and `settings.jwt_algorithm` from config

### Mocking Phase-II API Calls
**Issue**: Real HTTP requests to Phase-II backend
**Solution**: Ensure `@patch("src.mcp.tools._call_phase2_api")` is used

### Performance Tests Too Slow
**Issue**: Actual OpenAI API calls in tests
**Solution**: Mock AgentExecutor with `@patch("src.services.message_service.AgentExecutor")`

## Next Steps

1. Run full test suite: `pytest tests/integration/ -v --cov`
2. Review coverage report: `open htmlcov/index.html`
3. Fix any failures in the order:
   - Database tests (foundation)
   - MCP tool tests (integration)
   - Chat endpoint tests (API)
   - User isolation tests (security)
   - Persistence tests (data integrity)
   - Error handling tests (resilience)
   - Performance tests (optimization)

4. Create remaining test suites (T374-T380)
5. Generate final test report and sign-off

## Documentation

- **TESTING_CHECKLIST.md**: Full test plan and status
- **test_database_schema.py**: Database integration tests
- **test_mcp_tools_integration.py**: MCP tool tests
- **test_chat_endpoints_full.py**: Chat endpoint tests
- **test_user_isolation_security.py**: Security tests
- **test_persistence.py**: Persistence tests
- **test_error_handling.py**: Error handling tests
- **test_performance.py**: Performance benchmarks
