# Conversation State FSM (Finite State Machine) - Phase-III Final Architecture

## Overview

The Conversation State FSM ensures strict, step-based task workflows without intent mixing or fallback errors during normal flows.

## Architecture

### 1. ConversationState Model
**Location:** `backend/src/models/conversation_state.py`

Persistent database model tracking FSM state per conversation:

```python
ConversationState:
  - conversation_id: UUID (foreign key to conversations)
  - user_id: UUID (foreign key to users)
  - intent_mode: str (IDLE | ADD_TASK | UPDATE_TASK | DELETE_TASK | COMPLETE_TASK)
  - intent_step: str (TITLE | DESCRIPTION | PRIORITY | DUE_DATE | TASK_ID | CONFIRM)
  - intent_payload: Dict (collected fields for current intent)
```

### 2. ConversationStateService
**Location:** `backend/src/services/conversation_state_service.py`

Manages FSM state transitions and field collection:

- `get_conversation_state()` - Retrieve current FSM state
- `initialize_state()` - Create new IDLE state
- `set_intent()` - Start new intent (ADD_TASK, UPDATE_TASK, etc.)
- `advance_step()` - Collect field and move to next step
- `reset_state()` - Return to IDLE after successful action
- `is_in_multi_step_flow()` - Check if conversation has active intent
- `get_next_step_message()` - Get prompt for next step

## Multi-Step Workflows

### ADD_TASK Flow

```
User: "add task"
  ↓
Bot: "What would you like to call this task?"
  ↓ 
Intent: ADD_TASK, Step: TITLE, Payload: {}
  ↓
User: "Buy groceries"
  ↓
Bot: "Great! Now describe what this task is about (optional):"
  ↓
Intent: ADD_TASK, Step: DESCRIPTION, Payload: {title: "Buy groceries"}
  ↓
User: "Milk, eggs, bread, butter"
  ↓
Bot: "All required fields collected. Ready to proceed."
  ↓
Intent: ADD_TASK, Step: CONFIRM, Payload: {title: "Buy groceries", description: "..."}
  ↓
[Tool executes add_task with all fields]
  ↓
Bot: "Your task has been added successfully."
  ↓
Intent: IDLE (state reset)
```

### UPDATE_TASK Flow

```
User: "update task"
  ↓
Bot: "Which task? Please provide the task ID."
  ↓
Intent: UPDATE_TASK, Step: TASK_ID, Payload: {}
  ↓
User: "a1b2c3d4"
  ↓
Bot: "All required fields collected. Ready to proceed."
  ↓
Intent: UPDATE_TASK, Step: CONFIRM, Payload: {task_id: "a1b2c3d4"}
  ↓
[Tool executes update_task]
  ↓
Bot: "The task has been updated."
  ↓
Intent: IDLE
```

## Intent Locking Rules

**CRITICAL:** While `intent_mode != IDLE`:

1. **DO NOT re-detect intent** - Ignore intent keywords in user input
2. **DO NOT switch intents** - User cannot change task during flow
3. **ONLY accept data** - Extract fields for current step
4. **STRICT PROGRESSION** - Only move to next step after field collected

### Example (Intent Locking)

```
Intent Mode: ADD_TASK, Step: TITLE
User: "update task instead"
  ↗ Ignored! Still in ADD_TASK flow
User: "Finish project"
  → Accepted as TITLE field value
  → Move to DESCRIPTION step
```

## Tool Invocation Guard

Tools are ONLY called when:

```python
if state.intent_mode == CONFIRM and all_required_fields_present:
    execute_tool()
else:
    ask_for_next_field()
```

**Never** call tool if:
- Missing required fields
- Still in TITLE step
- Not in CONFIRM step

## Fallback Restriction

"I'm taking longer than expected" message ONLY returned if:

1. ✅ OpenAI API timeout/failure
2. ✅ Tool throws exception
3. ✅ Network connection error

**NOT** returned for:
- ❌ User says something ambiguous
- ❌ User asks wrong thing during flow
- ❌ Message parsing confusion

During normal flow, bot always responds contextually.

## Database Schema

```sql
CREATE TABLE conversation_states (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    user_id UUID REFERENCES users(id),
    intent_mode VARCHAR(50) DEFAULT 'IDLE',
    intent_step VARCHAR(50),
    intent_payload JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_conversation_states_conversation_user 
ON conversation_states(conversation_id, user_id);
```

## Integration Points

### 1. Chat Endpoint (`/api/v1/chat/conversations/{id}/messages`)

```python
# On each message:
1. Get conversation state
2. If IDLE:
   - Detect intent from user message
   - Call set_intent() → transition to first step
   - Return prompt for first step
3. If in multi-step flow:
   - Extract field value from user message
   - Call advance_step() → collect field & move to next step
   - If ready_to_execute=True:
     - Execute tool with collected fields
     - Call reset_state() → back to IDLE
   - Return next step prompt or success message
```

### 2. Agent Executor

Agent does NOT trigger during multi-step flows. Only:
- Detect intent when IDLE
- Execute tools when CONFIRM step reached

No OpenAI calls during intermediate steps (TITLE, DESCRIPTION, etc.)

## Success Criteria

✅ **Add Task Flow**
- User says "add task" → transitions to TITLE step
- User provides title → moves to DESCRIPTION step
- User provides description → becomes READY_TO_EXECUTE
- Tool executes with full data
- State resets to IDLE
- No fallback during flow

✅ **Strict Intent Locking**
- Cannot switch intents mid-flow
- Previous intent keywords ignored
- Only current step data accepted

✅ **Tool Invocation Guard**
- Tools only called with complete data
- No partial/empty tool calls
- No "I'm taking longer" during normal flow

✅ **State Persistence**
- Conversations with interrupted flow resume correctly
- Fresh conversation starts with IDLE
- State survives across multiple API calls

## Production Benefits

1. **Zero Ambiguity** - Clear step-by-step progression
2. **No Mixing** - Cannot confuse two task actions
3. **Guaranteed Execution** - Tools only call with complete data
4. **Smart Fallback** - Only true errors trigger fallback
5. **User-Friendly** - Context-aware prompts at each step
6. **Debuggable** - FSM state logged at each transition

## Testing the FSM

```bash
# Test ADD_TASK flow
curl -X POST /api/v1/chat/conversations/{id}/messages \
  -d '{"message": "add task"}'
  
# Response: "What would you like to call this task?"
# State: ADD_TASK, TITLE

curl -X POST /api/v1/chat/conversations/{id}/messages \
  -d '{"message": "Buy groceries"}'
  
# Response: "Great! Now describe what this task is about..."
# State: ADD_TASK, DESCRIPTION
```

---

**Status:** ✅ Production Ready
**Deployment:** Ready for Phase-III final release
