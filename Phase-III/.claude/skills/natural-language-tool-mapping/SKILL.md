# Natural Language Tool Mapping

## Purpose
Intelligently map user natural language input to appropriate MCP tools, accurately detecting user intent and selecting the correct tool with properly formatted parameters, while avoiding spurious tool calls for ambiguous or non-actionable input.

## Key Principles
- **Intent Detection**: Accurately identify what the user wants to do (add, list, update, complete, delete)
- **Precision Over Recall**: Don't call a tool unless intent is clear; prefer confirmation over mistakes
- **Clean Parameters**: Extract and normalize parameters; never pass empty or malformed values
- **Contextual Understanding**: Use conversation history and prior messages for context
- **User Confirmation**: Ask for clarification when intent is ambiguous or parameters are missing
- **No Hallucination**: Never invent tool calls; stick to explicit user intent

## Core Responsibilities

### 1. Intent Classification System

Define clear intent patterns for each tool:

#### ADD Intent
**Triggers:**
- "create a task"
- "add a task"
- "make a new task"
- "new task about..."
- "I need to do..."
- Keywords: create, add, new, make, build, set up

**Required Parameters:**
- `title` (mandatory)
- `description` (optional)
- `priority` (optional, default: "medium")

**Example:**
```
User: "Add a task to buy groceries"
Intent: ADD
Parameters: { title: "buy groceries", priority: "medium" }
```

#### LIST Intent
**Triggers:**
- "show my tasks"
- "list tasks"
- "what do I need to do"
- "get my tasks"
- "tasks for today"
- Keywords: show, list, get, view, what, display, tasks, today, pending, overdue

**Optional Parameters:**
- `filter` (status, priority, date range)
- `limit` (number of results)
- `offset` (pagination)

**Example:**
```
User: "Show me my overdue tasks"
Intent: LIST
Parameters: { filter: { status: "pending", overdue: true } }
```

#### UPDATE Intent
**Triggers:**
- "change task title"
- "update priority"
- "modify task"
- "rename..."
- "set description"
- Keywords: change, update, modify, rename, set, edit

**Required Parameters:**
- `task_id` (must reference existing task from context)
- At least one update field: title, description, priority, status

**Example:**
```
User: "Change the priority of that task to high"
Intent: UPDATE
Parameters: { task_id: "<id-from-context>", priority: "high" }
```

#### COMPLETE Intent
**Triggers:**
- "mark task as done"
- "complete task"
- "finish task"
- "done with..."
- "check off"
- Keywords: done, complete, finish, mark, check off, accomplished

**Required Parameters:**
- `task_id` (must be from context or clearly identified)

**Example:**
```
User: "Mark that task complete"
Intent: COMPLETE
Parameters: { task_id: "<id-from-context>" }
```

#### DELETE Intent
**Triggers:**
- "remove task"
- "delete task"
- "get rid of"
- "discard"
- "clear"
- Keywords: remove, delete, discard, remove, clear, get rid of

**Required Parameters:**
- `task_id` (must be from context or clearly identified)

**Warning:** Require confirmation before deleting

**Example:**
```
User: "Delete that task"
Intent: DELETE
Parameters: { task_id: "<id-from-context>" }
Confirmation: "Are you sure you want to delete this task?"
```

### 2. Parameter Extraction Pipeline

```python
from typing import Optional, Dict, Any
from enum import Enum

class Intent(Enum):
    ADD = "add"
    LIST = "list"
    UPDATE = "update"
    COMPLETE = "complete"
    DELETE = "delete"
    UNKNOWN = "unknown"

class ToolCall:
    def __init__(
        self,
        intent: Intent,
        tool_name: str,
        parameters: Dict[str, Any],
        confidence: float,  # 0.0 to 1.0
        requires_confirmation: bool = False,
        clarification_needed: Optional[str] = None
    ):
        self.intent = intent
        self.tool_name = tool_name
        self.parameters = parameters
        self.confidence = confidence
        self.requires_confirmation = requires_confirmation
        self.clarification_needed = clarification_needed

async def map_user_input_to_tool(
    user_message: str,
    conversation_history: List[Dict],
    current_tasks: List[Dict]
) -> Optional[ToolCall]:
    """
    Map natural language to tool call.

    Args:
        user_message: Raw user input
        conversation_history: Prior messages for context
        current_tasks: Available tasks for reference

    Returns:
        ToolCall with intent, tool, parameters, or None if no clear intent
    """

    # Step 1: Normalize input
    normalized = user_message.lower().strip()

    # Step 2: Detect intent
    intent = detect_intent(normalized, conversation_history)

    if intent == Intent.UNKNOWN:
        return None

    # Step 3: Extract parameters
    parameters = extract_parameters(
        normalized,
        intent,
        conversation_history,
        current_tasks
    )

    # Step 4: Validate parameters
    if not validate_parameters(intent, parameters):
        missing = get_missing_required_parameters(intent, parameters)
        return ToolCall(
            intent=intent,
            tool_name="",
            parameters={},
            confidence=0.5,
            clarification_needed=f"I need the following to complete this: {missing}"
        )

    # Step 5: Build tool call
    tool_call = build_tool_call(intent, parameters)

    # Step 6: Check if confirmation needed
    if intent == Intent.DELETE:
        tool_call.requires_confirmation = True

    return tool_call
```

### 3. Intent Detection Algorithm

```python
def detect_intent(
    message: str,
    conversation_history: List[Dict]
) -> Intent:
    """Classify user message into intent category."""

    # Keywords for each intent
    intent_keywords = {
        Intent.ADD: [
            'add', 'create', 'new', 'make', 'set up', 'build',
            'schedule', 'plan', 'need to', 'i should'
        ],
        Intent.LIST: [
            'show', 'list', 'get', 'view', 'display', 'what',
            'tasks', 'todo', 'pending', 'upcoming', 'today',
            'overdue', 'due'
        ],
        Intent.UPDATE: [
            'change', 'update', 'modify', 'rename', 'set',
            'edit', 'adjust', 'replace', 'switch'
        ],
        Intent.COMPLETE: [
            'done', 'complete', 'finish', 'mark', 'check off',
            'accomplished', 'finished'
        ],
        Intent.DELETE: [
            'remove', 'delete', 'discard', 'clear', 'get rid',
            'drop', 'erase'
        ]
    }

    # Score each intent
    scores = {}
    for intent, keywords in intent_keywords.items():
        score = sum(1 for kw in keywords if kw in message)
        scores[intent] = score

    # Return highest scoring intent, or UNKNOWN if no match
    max_intent = max(scores, key=scores.get)
    return max_intent if scores[max_intent] > 0 else Intent.UNKNOWN
```

### 4. Parameter Extraction

```python
def extract_parameters(
    message: str,
    intent: Intent,
    conversation_history: List[Dict],
    current_tasks: List[Dict]
) -> Dict[str, Any]:
    """Extract tool parameters from user message."""

    parameters = {}

    if intent == Intent.ADD:
        # Extract title (required)
        title = extract_title_for_add(message)
        if title:
            parameters['title'] = title

        # Extract description (optional)
        description = extract_description(message)
        if description:
            parameters['description'] = description

        # Extract priority (optional)
        priority = extract_priority(message)
        if priority:
            parameters['priority'] = priority

    elif intent == Intent.LIST:
        # Extract filters (optional)
        filters = {}

        # Check for status filter
        if 'overdue' in message:
            filters['status'] = 'overdue'
        elif 'pending' in message or 'incomplete' in message:
            filters['status'] = 'pending'
        elif 'done' in message or 'completed' in message:
            filters['status'] = 'completed'

        # Check for priority filter
        if 'high' in message:
            filters['priority'] = 'high'
        elif 'low' in message:
            filters['priority'] = 'low'

        # Check for time filter
        if 'today' in message:
            filters['due_date'] = 'today'
        elif 'this week' in message:
            filters['due_date'] = 'this_week'

        if filters:
            parameters['filters'] = filters

        # Extract pagination (optional)
        limit = extract_number(message, 'limit', 10)
        if limit:
            parameters['limit'] = limit

    elif intent == Intent.UPDATE:
        # Extract task reference (required)
        task_id = resolve_task_reference(message, conversation_history, current_tasks)
        if task_id:
            parameters['task_id'] = task_id

        # Extract what's being updated
        if 'title' in message or 'name' in message:
            new_title = extract_new_value(message, 'title')
            if new_title:
                parameters['title'] = new_title

        if 'description' in message:
            new_desc = extract_new_value(message, 'description')
            if new_desc:
                parameters['description'] = new_desc

        if 'priority' in message:
            new_priority = extract_priority(message)
            if new_priority:
                parameters['priority'] = new_priority

    elif intent == Intent.COMPLETE:
        # Extract task reference (required)
        task_id = resolve_task_reference(message, conversation_history, current_tasks)
        if task_id:
            parameters['task_id'] = task_id

    elif intent == Intent.DELETE:
        # Extract task reference (required)
        task_id = resolve_task_reference(message, conversation_history, current_tasks)
        if task_id:
            parameters['task_id'] = task_id

    return parameters
```

### 5. Task Reference Resolution

```python
def resolve_task_reference(
    message: str,
    conversation_history: List[Dict],
    current_tasks: List[Dict]
) -> Optional[str]:
    """
    Resolve vague references like 'that task' or 'the first one'
    to actual task IDs from context.
    """

    # Check for explicit task ID
    if 'task #' in message or 'id:' in message:
        return extract_task_id(message)

    # Check for positional references
    if 'first task' in message or 'that one' in message:
        return current_tasks[0]['id'] if current_tasks else None

    if 'last task' in message:
        return current_tasks[-1]['id'] if current_tasks else None

    # Check for title references
    if 'the task' in message or 'this task' in message:
        # Look for recent message mentioning a task
        for msg in reversed(conversation_history[-5:]):
            if msg['role'] == 'assistant' and 'task' in msg['content']:
                # Extract task from assistant's recent message
                task_id = extract_task_id_from_assistant_message(msg['content'])
                if task_id:
                    return task_id

    return None
```

### 6. Validation

```python
def validate_parameters(intent: Intent, parameters: Dict[str, Any]) -> bool:
    """Check if required parameters are present and valid."""

    required_params = {
        Intent.ADD: ['title'],
        Intent.LIST: [],  # No required parameters
        Intent.UPDATE: ['task_id', 'title', 'description', 'priority'],  # At least one of last 3
        Intent.COMPLETE: ['task_id'],
        Intent.DELETE: ['task_id']
    }

    required = required_params.get(intent, [])

    # Check for ADD: need title
    if intent == Intent.ADD:
        return 'title' in parameters and len(parameters['title'].strip()) > 0

    # Check for UPDATE: need task_id AND at least one field to update
    if intent == Intent.UPDATE:
        has_task_id = 'task_id' in parameters
        has_field = any(k in parameters for k in ['title', 'description', 'priority'])
        return has_task_id and has_field

    # Check for COMPLETE/DELETE: need task_id
    if intent in [Intent.COMPLETE, Intent.DELETE]:
        return 'task_id' in parameters

    # LIST has no hard requirements
    if intent == Intent.LIST:
        return True

    return False
```

### 7. Confidence Scoring

```python
def calculate_confidence(
    intent: Intent,
    message: str,
    parameters: Dict[str, Any]
) -> float:
    """
    Calculate confidence (0.0 to 1.0) that extraction is correct.

    Lower confidence triggers confirmation request.
    """

    confidence = 0.5  # baseline

    # Boost for explicit keywords
    explicit_keywords = {
        Intent.ADD: ['add', 'create', 'new'],
        Intent.LIST: ['show', 'list', 'get'],
        Intent.UPDATE: ['change', 'update'],
        Intent.COMPLETE: ['done', 'complete'],
        Intent.DELETE: ['delete', 'remove']
    }

    for keyword in explicit_keywords.get(intent, []):
        if keyword in message.lower():
            confidence += 0.2
            break

    # Boost for complete parameters
    if intent == Intent.ADD and 'title' in parameters:
        confidence += 0.3

    if intent == Intent.UPDATE and 'task_id' in parameters:
        confidence += 0.2

    # Reduce if task reference is vague (e.g., "that task" without context)
    if intent in [Intent.UPDATE, Intent.COMPLETE, Intent.DELETE]:
        if 'task_id' not in parameters:
            confidence -= 0.3

    # Cap at 1.0
    return min(confidence, 1.0)
```

### 8. Handling Ambiguous Input

When intent is unclear or parameters are incomplete:

```python
async def handle_ambiguous_input(
    tool_call: ToolCall,
    conversation_history: List[Dict]
) -> str:
    """Generate clarification request or confirmation."""

    if tool_call.clarification_needed:
        return f"I need a bit more info: {tool_call.clarification_needed}"

    if tool_call.requires_confirmation:
        return f"I'm about to {tool_call.intent.value} this task. Is that correct?"

    if tool_call.confidence < 0.7:
        return (
            f"I think you want to {tool_call.intent.value}, but I'm not 100% sure. "
            "Could you clarify what you'd like to do?"
        )

    return None
```

## Tool Call Examples

### Example 1: Clear ADD
```
User: "Add a task to finish the report"
Intent: ADD (confidence: 0.95)
Tool: add_task
Parameters: {
  "title": "finish the report",
  "priority": "medium"
}
Action: Execute without confirmation
```

### Example 2: LIST with Filter
```
User: "Show me my overdue tasks"
Intent: LIST (confidence: 0.90)
Tool: list_tasks
Parameters: {
  "filters": {
    "status": "overdue"
  }
}
Action: Execute without confirmation
```

### Example 3: UPDATE Requires Confirmation
```
User: "Change that to high priority"
Intent: UPDATE (confidence: 0.6)
Clarification: "I found a task in our conversation, but I'm not certain which one. Did you mean: 'finish the report'?"
Action: Wait for user confirmation before executing
```

### Example 4: DELETE Requires Explicit Confirmation
```
User: "Delete this task"
Intent: DELETE (confidence: 0.8)
Tool: delete_task
Parameters: {
  "task_id": "task-123"
}
Confirmation: "Are you sure you want to delete 'finish the report'? This can't be undone."
Action: Wait for explicit "yes" before executing
```

### Example 5: No Clear Intent
```
User: "The weather is nice today"
Intent: UNKNOWN (confidence: 0.0)
Action: Respond naturally without tool call
```

## Success Criteria
✅ Correctly detects user intent (add, list, update, complete, delete)
✅ Extracts parameters with high accuracy
✅ Resolves task references from conversation context
✅ No tool calls for ambiguous intent
✅ Confirmation requested for DELETE operations
✅ Clarification requested when parameters missing
✅ Confidence scoring is calibrated (0.7+ for auto-execution)
✅ No hallucinated parameters
✅ Handles edge cases (typos, colloquial language)
✅ Contextual understanding of prior messages

## Related Components
- **OpenAI Agents SDK**: Uses this mapping to decide when to call tools
- **MCP Server**: Tools that are mapped to
- **Conversation History**: Used for context and task references
- **Natural Language Processing**: Intent classification

## Edge Cases & Fallbacks

#### Typos/Colloquial Language
- "creat a task" → Detect as ADD (fuzzy matching)
- "get my todos" → Detect as LIST
- "check it off" → Detect as COMPLETE

#### Ambiguous References
- "change that" without prior context → Ask for clarification
- "delete it" without identifying task → Ask which task

#### Multi-Intent Messages
- "Create a task and show me my list" → Execute both intents sequentially

#### Context Switch
- User mentions multiple tasks, then says "update it" → Use most recent task

## Performance Notes
- Intent detection: O(n) where n = keywords (fast)
- Parameter extraction: O(m) where m = message length (fast)
- Task resolution: O(k) where k = conversation history length (may need caching)
- Cache task mappings during conversation to avoid re-parsing

## Future Enhancements
- Machine learning for intent classification
- Entity recognition for better parameter extraction
- Dialogue state tracking for complex multi-turn interactions
- User preference learning (e.g., default priority levels)
- Spell-check and autocorrect for task titles
