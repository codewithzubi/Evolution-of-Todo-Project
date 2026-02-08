# Phase-III Integration Testing Checklist (T366-T380)

## Test Suite Status

### T366: Database Integration Tests ✅ IMPLEMENTED
**File**: `test_database_schema.py`
**Coverage**:
- [x] Conversation CRUD operations
- [x] Message CRUD operations
- [x] User isolation via foreign keys
- [x] Soft delete functionality
- [x] Cascade deletes
- [x] Message ordering (created_at DESC)
- [x] Index performance (<200ms queries)
- [x] Metadata JSON storage
- [x] Tool calls/results storage

**Classes**:
- `TestConversationCRUD`: Create, read, update, delete conversations
- `TestUserIsolation`: User-scoped conversation and message access
- `TestMessageCRUD`: Message CRUD operations
- `TestMessageOrdering`: Message ordering and filtering
- `TestPerformanceIndexes`: Index performance validation
- `TestCascadingOperations`: Delete cascade behavior
- `TestMetadataStorage`: JSON field persistence

### T367: MCP Tool Integration Tests ✅ IMPLEMENTED
**File**: `test_mcp_tools_integration.py`
**Coverage**:
- [x] add_task tool execution
- [x] list_tasks tool with filtering
- [x] update_task tool execution
- [x] complete_task tool execution
- [x] delete_task tool execution
- [x] User isolation enforcement in tools
- [x] Tool timeout handling
- [x] Error recovery
- [x] Malformed response handling

**Classes**:
- `TestAddTaskTool`: Tool execution and validation
- `TestListTasksTool`: Filtering and pagination
- `TestUpdateTaskTool`: Update operations
- `TestCompleteTaskTool`: Completion operations
- `TestDeleteTaskTool`: Deletion operations
- `TestToolErrorHandling`: Error scenarios
- `TestToolUserScopingInheritance`: User isolation

### T368: OpenAI Agents SDK Integration Tests (PARTIAL)
**Status**: PENDING (requires agent implementation)
**File**: To be created
**Coverage**:
- [ ] Single-turn conversation
- [ ] Multi-turn conversation (3+)
- [ ] Tool calling
- [ ] Tool result parsing
- [ ] Context window management
- [ ] System prompt constraints
- [ ] Error recovery
- [ ] Response parsing

### T369: Chat Endpoint Integration Tests ✅ IMPLEMENTED
**File**: `test_chat_endpoints_full.py`
**Coverage**:
- [x] POST /messages - Create task via chat (end-to-end)
- [x] GET /conversations - List with pagination
- [x] GET /messages - List with pagination
- [x] DELETE /conversations - Soft delete with cascade
- [x] JWT authentication enforcement
- [x] User isolation enforcement
- [x] Pagination (limit, offset)
- [x] Error responses
- [x] Response format validation

**Classes**:
- `TestChatEndpointsEndToEnd`: Full workflows
- `TestMessageEndpointsEndToEnd`: Message workflows
- `TestErrorHandlingAndEdgeCases`: Error scenarios
- `TestChatWorkflowWithMocking`: Agent mocking

### T370: User Isolation & Security Tests ✅ IMPLEMENTED
**File**: `test_user_isolation_security.py`
**Coverage**:
- [x] User A cannot read User B's conversations
- [x] User A cannot view User B's messages
- [x] User A cannot modify User B's conversations
- [x] User A cannot delete User B's messages
- [x] JWT validation (missing, invalid, expired)
- [x] JWT expiration handling
- [x] Database queries enforce user_id filters
- [x] Error messages don't leak sensitive info
- [x] Concurrent user access safety

**Classes**:
- `TestUserConversationIsolation`: Conversation access control
- `TestUserMessageIsolation`: Message access control
- `TestJWTAuthentication`: Token validation
- `TestDatabaseSecurityQueries`: Query filtering
- `TestErrorMessagesNoLeakage`: Info leakage prevention
- `TestConcurrentUserAccess`: Safe concurrent access
- `TestSecurityAuditLogging`: Audit trail verification

### T371: Conversation Persistence Tests ✅ IMPLEMENTED
**File**: `test_persistence.py`
**Coverage**:
- [x] Save conversation → Restart → Still exists
- [x] Save messages → Restart → Still exist
- [x] Soft delete persistence
- [x] Metadata persistence (JSONB)
- [x] Tool calls metadata persistence
- [x] Tool results metadata persistence
- [x] Large conversation (100+ messages) handling
- [x] Data consistency after failures
- [x] Atomic updates

**Classes**:
- `TestConversationPersistence`: Conversation data persistence
- `TestMessagePersistence`: Message data persistence
- `TestLargeConversationPersistence`: Scalability
- `TestSoftDeletePersistence`: Soft delete behavior
- `TestMetadataPersistence`: JSON field preservation
- `TestDataConsistencyAfterFailures`: Failure recovery

### T372: Error Handling & Recovery Tests ✅ IMPLEMENTED
**File**: `test_error_handling.py`
**Coverage**:
- [x] Network error handling
- [x] Database connection errors
- [x] API timeout handling (>10s)
- [x] Rate limiting (429) and backoff
- [x] Malformed JSON responses
- [x] Missing required response fields
- [x] Partial failures
- [x] Graceful degradation
- [x] Error response format consistency

**Classes**:
- `TestNetworkErrorHandling`: Network failures
- `TestTimeoutHandling`: Timeout scenarios
- `TestRateLimitHandling`: Rate limiting
- `TestAPIResponseValidation`: Response validation
- `TestGracefulDegradation`: Fallback behavior
- `TestErrorResponseFormats`: Response consistency
- `TestRecoveryMechanisms`: Recovery mechanisms

### T373: Performance & Benchmark Tests ✅ IMPLEMENTED
**File**: `test_performance.py`
**Coverage**:
- [x] Chat response time <3s (p95)
- [x] Conversation list <200ms (p95)
- [x] Message list <200ms (p95)
- [x] Database indexes working
- [x] Agent token window (20-message limit)
- [x] Concurrent users (10+) handling
- [x] Memory stability (1000+ messages)
- [x] Scalability testing

**Benchmarks**:
- `test_single_message_response_time`: < 3s
- `test_list_conversations_under_200ms`: < 200ms
- `test_list_messages_under_200ms`: < 200ms
- `test_10_concurrent_users_creating_conversations`: < 5s
- `test_10_concurrent_users_listing_conversations`: < 5s

### T374: Phase-II Regression Tests (PENDING)
**Status**: PENDING
**File**: To be created
**Coverage**:
- [ ] All Phase-II tasks API still works
- [ ] All Phase-II users API still works
- [ ] Phase-II database schema unchanged
- [ ] Phase-II authentication still works
- [ ] Phase-II CRUD operations still work
- [ ] Phase-II filtering/sorting still work
- [ ] Zero modifications to Phase-II code

### T375: API Contract Tests (PENDING)
**Status**: PENDING
**File**: To be created
**Coverage**:
- [ ] Response format: {data, error} envelope
- [ ] Timestamps: ISO 8601 format
- [ ] UUIDs: Valid UUID4 format
- [ ] Error codes: Match spec
- [ ] Pagination: limit, offset, total
- [ ] Sort order: DESC for timestamps
- [ ] Required fields present
- [ ] No extra fields

### T376: Frontend-Backend Integration Tests (PENDING)
**Status**: PENDING (requires frontend)
**File**: `frontend/tests/integration/test_chat_api_integration.test.tsx`
**Coverage**:
- [ ] Frontend authenticates with backend
- [ ] Frontend creates conversation
- [ ] Frontend sends/receives messages
- [ ] Frontend lists conversations
- [ ] Frontend displays errors
- [ ] Frontend retries on network error

### T377: Multi-user Chat Scenario Tests (PENDING)
**Status**: PENDING
**File**: To be created
**Coverage**:
- [ ] User A and B chat independently
- [ ] Task isolation (A's task invisible to B)
- [ ] Rapid multi-turn (5 messages in 10s)
- [ ] Network recovery scenario

### T378: Accessibility & Internationalization Tests (PENDING)
**Status**: PENDING
**File**: `frontend/tests/integration/test_accessibility.test.tsx`
**Coverage**:
- [ ] Chat UI translations
- [ ] Dark/light mode support
- [ ] Keyboard navigation
- [ ] ARIA labels
- [ ] Color contrast WCAG AA
- [ ] Mobile responsive
- [ ] No page interference

### T379: Load Testing & Scalability (PENDING)
**Status**: PENDING
**File**: To be created
**Coverage**:
- [ ] 10 concurrent users
- [ ] 100 concurrent message sends
- [ ] 1000 messages per conversation
- [ ] DB connection pooling
- [ ] OpenAI rate limits
- [ ] Bottleneck analysis

### T380: Final Verification & Sign-Off (PENDING)
**Status**: PENDING
**File**: `TEST_RESULTS.md`, `FINAL_VERIFICATION.md`
**Checklist**:
- [ ] 70+ tests passing
- [ ] 70%+ code coverage
- [ ] Performance benchmarks met
- [ ] Security tests passing
- [ ] Phase-II regression tests passing
- [ ] Documentation complete
- [ ] Stakeholder sign-off

## Fixture Configuration

### conftest.py Updates
✅ Added test user fixtures:
- `test_user`: Creates User in database for FK constraints
- `other_user`: Creates second user for isolation testing
- Updated `sample_conversation`, `sample_message` to use test_user fixture
- Updated `user_a_conversation`, `user_b_conversation` to use user fixtures

## Execution Steps

1. **Run Database Tests**
   ```bash
   pytest backend/tests/integration/test_database_schema.py -v --cov
   ```

2. **Run MCP Tool Tests**
   ```bash
   pytest backend/tests/integration/test_mcp_tools_integration.py -v
   ```

3. **Run Chat Endpoint Tests**
   ```bash
   pytest backend/tests/integration/test_chat_endpoints_full.py -v
   ```

4. **Run User Isolation Tests**
   ```bash
   pytest backend/tests/integration/test_user_isolation_security.py -v
   ```

5. **Run Persistence Tests**
   ```bash
   pytest backend/tests/integration/test_persistence.py -v
   ```

6. **Run Error Handling Tests**
   ```bash
   pytest backend/tests/integration/test_error_handling.py -v
   ```

7. **Run Performance Tests**
   ```bash
   pytest backend/tests/integration/test_performance.py -v -s
   ```

8. **Run All Tests with Coverage**
   ```bash
   pytest backend/tests/integration/ -v --cov=src --cov-report=html
   ```

## Key Test Patterns

### User Isolation Pattern
```python
# Create separate users and tokens
user_a_token = create_token(user_a_id)
user_b_token = create_token(user_b_id)

# Verify access control
resp = client.get(
    f"/api/v1/chat/conversations/{user_b_conv_id}",
    headers={"Authorization": f"Bearer {user_a_token}"}
)
assert resp.status_code == 404  # Not found in user A's scope
```

### Database Test Pattern
```python
@pytest.mark.asyncio
async def test_something(test_session: AsyncSession, test_user):
    # Create data
    conv = Conversation(user_id=test_user.id, title="Test")
    test_session.add(conv)
    await test_session.commit()

    # Query and verify
    stmt = select(Conversation).where(Conversation.id == conv.id)
    result = await test_session.execute(stmt)
    retrieved = result.scalar_one_or_none()
    assert retrieved is not None
```

### JWT Token Pattern
```python
def create_token(user_id):
    payload = {
        "user_id": str(user_id),
        "email": f"user-{user_id}@example.com",
        "sub": str(user_id),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
```

## Known Issues & Gaps

1. **Agent Integration**: T368 requires agent implementation completion
2. **Frontend Tests**: T376, T378 require frontend build
3. **Phase-II Regression**: T374 requires Phase-II API setup
4. **API Contract Tests**: T375 requires spec review
5. **Load Testing**: T379 requires staging environment
6. **Agents SDK**: Multi-turn tests require working agent executor

## Dependencies

- `pytest`: Testing framework
- `pytest-asyncio`: Async test support
- `sqlalchemy`: ORM queries
- `jose`: JWT token creation
- `httpx`: HTTP client (for MCP API calls)
- `unittest.mock`: Mocking framework

## Next Steps

1. ✅ Create database integration tests (T366)
2. ✅ Create MCP tool tests (T367)
3. ✅ Create chat endpoint tests (T369)
4. ✅ Create user isolation tests (T370)
5. ✅ Create persistence tests (T371)
6. ✅ Create error handling tests (T372)
7. ✅ Create performance tests (T373)
8. [ ] Create Phase-II regression tests (T374)
9. [ ] Create API contract tests (T375)
10. [ ] Create frontend integration tests (T376)
11. [ ] Create multi-user scenario tests (T377)
12. [ ] Create accessibility tests (T378)
13. [ ] Create load tests (T379)
14. [ ] Generate final verification report (T380)

## Success Criteria

- [x] Database integration tests working
- [x] MCP tool tests working
- [x] Chat endpoint tests working
- [x] User isolation verified
- [x] Persistence verified
- [x] Error handling tested
- [x] Performance baselines established
- [ ] All 70+ tests passing
- [ ] 70%+ coverage achieved
- [ ] Performance benchmarks met
- [ ] Stakeholder sign-off obtained
