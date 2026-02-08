# Error & Confirmation Handling

## Purpose
Implement graceful error handling and user confirmations throughout the chat interface, ensuring destructive actions require explicit approval, providing friendly feedback after successful operations, and elegantly handling common error scenarios like missing tasks.

## Key Principles
- **Safety First**: Require explicit confirmation before any destructive action (delete, update, complete)
- **Clear Feedback**: Provide immediate, friendly confirmation after successful operations
- **User-Friendly Errors**: Transform technical errors into understandable messages
- **Graceful Degradation**: Handle errors without crashing; offer recovery paths
- **Context Preservation**: Keep conversation context intact even after errors
- **Undo Opportunities**: Where possible, suggest recovery actions (e.g., "You can undo this")

## Core Responsibilities

### 1. Destructive Action Confirmation

#### DELETE Confirmation
Always require explicit confirmation before deletion:

```python
async def handle_delete_confirmation(
    task_id: str,
    task_name: str,
    conversation_history: List[Dict]
) -> Tuple[bool, str]:
    """
    Request confirmation for task deletion.

    Returns:
        (should_proceed: bool, response_message: str)
    """

    confirmation_prompt = f"""
🗑️ Delete Task?

I'm about to delete: **"{task_name}"**

This action cannot be undone. Are you sure you want to proceed?

Please reply with:
- "yes" or "confirm" to delete
- "no" or "cancel" to keep it
    """.strip()

    return confirmation_prompt, False  # Don't execute yet
```

#### UPDATE Confirmation (Conditional)
Require confirmation for significant updates:

```python
async def handle_update_confirmation(
    task_id: str,
    current_task: Dict,
    proposed_changes: Dict
) -> Tuple[bool, str]:
    """
    Request confirmation for significant task updates.

    Only confirm if:
    - Changing title substantially
    - Changing priority to/from urgent
    - Changing status to completed
    """

    changes_list = []
    for field, new_value in proposed_changes.items():
        old_value = current_task.get(field)
        if old_value != new_value:
            changes_list.append(f"- {field}: {old_value} → {new_value}")

    if len(changes_list) > 1:  # Multiple changes
        confirmation_prompt = f"""
⚠️ Update Task?

I'm about to change: **"{current_task['title']}"**

Changes:
{chr(10).join(changes_list)}

Is this correct? Reply "yes" to confirm.
        """.strip()
        return confirmation_prompt, False

    # Single non-critical change, execute without confirmation
    return None, True
```

#### COMPLETE Confirmation (Optional)
```python
async def handle_complete_confirmation(
    task_id: str,
    task_name: str,
    is_overdue: bool = False
) -> str:
    """
    Optional confirmation for completing task (especially if overdue).
    """

    if is_overdue:
        return f"""
✅ Complete Task?

Marking **"{task_name}"** as complete.
(This task was overdue)

Confirm? Reply "yes" to proceed.
        """.strip()

    # No confirmation needed for normal completion
    return None
```

### 2. Confirmation Response Parsing

```python
def parse_confirmation_response(user_response: str) -> bool:
    """
    Parse user's confirmation response.

    Returns:
        True if user confirms, False otherwise
    """

    normalized = user_response.lower().strip()

    # Affirmative responses
    affirmative = [
        'yes', 'yep', 'yeah', 'sure', 'confirm', 'confirmed',
        'go ahead', 'do it', 'proceed', 'ok', 'okay', 'okey',
        'y', 'true', '✓', '👍'
    ]

    # Negative responses
    negative = [
        'no', 'nope', 'cancel', 'don\'t', 'stop', 'n',
        'false', '✗', '👎', 'wait'
    ]

    # Check exact and partial matches
    for term in affirmative:
        if normalized == term or normalized.startswith(term):
            return True

    for term in negative:
        if normalized == term or normalized.startswith(term):
            return False

    # Ambiguous response - request clarification
    return None  # Return None to signal clarification needed
```

### 3. Successful Operation Feedback

#### ADD Confirmation
```python
async def confirm_add_success(
    task_id: str,
    task_name: str,
    priority: str = "medium"
) -> str:
    """Return friendly confirmation after task creation."""

    emoji_map = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢"
    }
    emoji = emoji_map.get(priority, "⭕")

    return f"""
✅ Task Created!

I've added: {emoji} **"{task_name}"**
Priority: {priority}

What would you like to do next?
    """.strip()
```

#### UPDATE Confirmation
```python
async def confirm_update_success(
    task_name: str,
    changed_fields: Dict[str, Tuple[str, str]]
) -> str:
    """Return friendly confirmation after update."""

    changes_summary = "\n".join([
        f"- {field}: {old} → {new}"
        for field, (old, new) in changed_fields.items()
    ])

    return f"""
✅ Task Updated!

Updated: **"{task_name}"**

Changes:
{changes_summary}

Anything else you'd like to adjust?
    """.strip()
```

#### COMPLETE Confirmation
```python
async def confirm_complete_success(
    task_name: str,
    days_to_complete: int = None
) -> str:
    """Return encouraging confirmation after completion."""

    if days_to_complete:
        return f"""
🎉 Task Completed!

Great job finishing **"{task_name}"**!
You completed it in {days_to_complete} days.

What's next?
        """.strip()

    return f"""
✅ Task Complete!

Marked **"{task_name}"** as done.

Nice work! Ready for the next task?
    """.strip()
```

#### DELETE Confirmation
```python
async def confirm_delete_success(task_name: str) -> str:
    """Return confirmation after deletion."""

    return f"""
🗑️ Task Deleted

I've removed **"{task_name}"** from your list.

You can't undo this, but let me know if you need anything else.
    """.strip()
```

#### LIST Response
```python
async def confirm_list_success(
    tasks: List[Dict],
    filter_desc: str = None
) -> str:
    """Return friendly list of tasks."""

    if not tasks:
        if filter_desc:
            return f"📋 No {filter_desc} tasks found.\n\nWant to add one?"
        return "📋 You don't have any tasks yet.\n\nWant to create one?"

    # Format tasks with emojis
    task_lines = []
    for i, task in enumerate(tasks, 1):
        status_emoji = "☑️" if task.get('status') == 'completed' else "☐"
        priority_emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }.get(task.get('priority'), "⭕")

        task_lines.append(
            f"{i}. {status_emoji} {priority_emoji} **{task['title']}**"
        )

    task_list = "\n".join(task_lines)
    filter_text = f"({filter_desc})" if filter_desc else ""
    total = len(tasks)

    return f"""
📋 Your Tasks {filter_text}
Total: {total}

{task_list}

Need to create, update, or complete any?
    """.strip()
```

### 4. Error Handling

#### Task Not Found
```python
async def handle_task_not_found(
    task_reference: str,
    available_tasks: List[Dict]
) -> str:
    """Handle when referenced task doesn't exist."""

    if not available_tasks:
        return f"""
❌ Task Not Found

I couldn't find a task matching "{task_reference}".

You don't have any tasks yet. Want to create one?
        """.strip()

    # Show available tasks for user to pick from
    task_suggestions = "\n".join([
        f"- {task['title']}"
        for task in available_tasks[:5]
    ])

    return f"""
❌ Task Not Found

I couldn't find "{task_reference}" in your tasks.

Did you mean one of these?
{task_suggestions}

Or let me know the exact task name.
    """.strip()
```

#### Invalid Parameters
```python
async def handle_invalid_parameters(
    intent: str,
    missing_fields: List[str],
    guidance: str = None
) -> str:
    """Handle missing or invalid parameters."""

    fields_text = ", ".join(f"'{f}'" for f in missing_fields)

    response = f"""
⚠️ I Need More Info

To {intent}, I need:
{chr(10).join(f"- {f}" for f in missing_fields)}

Example: "Add a task to [title] with [priority] priority"
    """

    if guidance:
        response += f"\n\n{guidance}"

    return response.strip()
```

#### Permission Denied
```python
async def handle_permission_denied(
    action: str,
    resource: str
) -> str:
    """Handle cross-user access attempts."""

    return f"""
🔒 Access Denied

You don't have permission to {action} this {resource}.

If you think this is a mistake, please contact support.
    """.strip()
```

#### Server Error
```python
async def handle_server_error(
    error_details: str = None,
    correlation_id: str = None
) -> str:
    """Handle server-side errors gracefully."""

    response = """
😞 Something Went Wrong

I encountered an issue while processing your request.

Please try again in a moment. If the problem persists, here's info to share with support:
"""

    if correlation_id:
        response += f"\nError ID: `{correlation_id}`"

    return response.strip()
```

#### Rate Limiting
```python
async def handle_rate_limit(
    retry_after_seconds: int = None
) -> str:
    """Handle rate limit errors."""

    response = "⏱️ Too Many Requests\n\nI'm receiving too many requests at once."

    if retry_after_seconds:
        response += f"\n\nPlease try again in {retry_after_seconds} seconds."
    else:
        response += "\n\nPlease try again in a moment."

    return response.strip()
```

### 5. Error Recovery Paths

```python
class ErrorRecovery:
    """Suggest recovery actions based on error type."""

    @staticmethod
    def get_recovery_suggestions(error_type: str, context: Dict) -> List[str]:
        """Return recovery actions user can take."""

        suggestions = {
            "task_not_found": [
                "Check the exact task name",
                "List all tasks to find the right one",
                "Create a new task if needed"
            ],
            "invalid_parameters": [
                "Provide the missing information",
                "Try a simpler request",
                "Ask for examples"
            ],
            "permission_denied": [
                "Make sure you're logged in",
                "Verify you own the task",
                "Try again after logging out and back in"
            ],
            "server_error": [
                "Try again in a moment",
                "Check your internet connection",
                "Refresh the page"
            ],
            "rate_limit": [
                "Wait a few seconds",
                "Reduce the number of requests",
                "Try a simpler action"
            ]
        }

        return suggestions.get(error_type, ["Try again"])

    @staticmethod
    def format_recovery_message(
        error_type: str,
        context: Dict,
        suggestions: List[str]
    ) -> str:
        """Format recovery suggestions for user."""

        suggestions_text = "\n".join([
            f"- {s}" for s in suggestions
        ])

        return f"""
You can try:
{suggestions_text}
        """.strip()
```

### 6. Confirmation Context Tracking

```python
class ConfirmationState:
    """Track pending confirmations during conversation."""

    def __init__(self):
        self.pending_action = None  # {'type': 'delete', 'task_id': '...', ...}
        self.confirmation_message = None
        self.created_at = None
        self.attempts = 0
        self.max_attempts = 3

    def set_pending(
        self,
        action_type: str,
        task_id: str,
        task_name: str,
        message: str
    ) -> None:
        """Set action awaiting confirmation."""
        self.pending_action = {
            'type': action_type,
            'task_id': task_id,
            'task_name': task_name
        }
        self.confirmation_message = message
        self.created_at = datetime.utcnow()
        self.attempts = 0

    def clear_pending(self) -> None:
        """Clear pending action after confirmation/cancellation."""
        self.pending_action = None
        self.confirmation_message = None
        self.created_at = None
        self.attempts = 0

    def is_expired(self, timeout_minutes: int = 5) -> bool:
        """Check if confirmation request expired."""
        if not self.created_at:
            return False
        elapsed = (datetime.utcnow() - self.created_at).total_seconds() / 60
        return elapsed > timeout_minutes

    def increment_attempts(self) -> bool:
        """Track confirmation attempts, return True if still valid."""
        self.attempts += 1
        return self.attempts < self.max_attempts
```

### 7. Complete Flow Example

```python
async def process_user_message_with_confirmations(
    user_message: str,
    conversation_history: List[Dict],
    confirmation_state: ConfirmationState,
    current_tasks: List[Dict]
) -> Tuple[str, bool]:
    """
    Process message, handle confirmations, and return response.

    Returns:
        (response_message, tool_executed)
    """

    # Step 1: Check if we're waiting for confirmation
    if confirmation_state.pending_action:
        # Parse confirmation response
        confirmed = parse_confirmation_response(user_message)

        if confirmed is None:
            return "Could you say 'yes' to confirm or 'no' to cancel?", False

        if not confirmed:
            confirmation_state.clear_pending()
            return f"Canceled. I won't {confirmation_state.pending_action['type']}.", False

        # User confirmed - proceed with action
        action = confirmation_state.pending_action
        result = await execute_tool(
            action['type'],
            action['task_id'],
            current_tasks
        )
        confirmation_state.clear_pending()

        if result['success']:
            response = get_success_message(action['type'], action)
        else:
            response = get_error_message(result['error'])

        return response, True

    # Step 2: Map user input to tool
    tool_call = map_user_input_to_tool(
        user_message,
        conversation_history,
        current_tasks
    )

    if tool_call is None:
        return "I'm not sure what you'd like to do. Can you rephrase?", False

    # Step 3: Check if confirmation needed
    if tool_call.requires_confirmation or tool_call.confidence < 0.7:
        confirmation_message = get_confirmation_message(tool_call)
        confirmation_state.set_pending(
            tool_call.intent.value,
            tool_call.parameters.get('task_id'),
            tool_call.parameters.get('title'),
            confirmation_message
        )
        return confirmation_message, False

    # Step 4: Execute tool
    try:
        result = await execute_tool(
            tool_call.intent,
            tool_call.parameters,
            current_tasks
        )

        if result['success']:
            response = get_success_message(tool_call.intent, result)
        else:
            response = get_error_message(result['error'])

    except Exception as e:
        response = handle_server_error(str(e), correlation_id=uuid4())

    return response, result.get('success', False)
```

## Error Status Codes & Handling

| Code | Meaning | Response |
|------|---------|----------|
| 400 | Bad Request | "I didn't understand. Can you try again?" |
| 401 | Unauthorized | "You've been logged out. Please log back in." |
| 403 | Forbidden | "You don't have permission to do this." |
| 404 | Not Found | "I couldn't find that task. Did you mean...?" |
| 422 | Validation Error | "I need [missing field]. Can you provide it?" |
| 429 | Rate Limited | "Too many requests. Please wait a moment." |
| 500 | Server Error | "Something went wrong. Please try again." |
| 503 | Service Unavailable | "Service is temporarily down. Try again soon." |

## Success Criteria
✅ All destructive actions (delete, update) require confirmation
✅ Confirmation messages are clear and friendly
✅ User responses parsed correctly (yes/no, confirm/cancel)
✅ Success messages provide positive feedback
✅ Error messages are user-friendly, not technical
✅ Task-not-found errors show helpful suggestions
✅ Confirmation state tracked across conversation turns
✅ Invalid parameters trigger helpful guidance
✅ Server errors include correlation ID for debugging
✅ Recovery suggestions provided for each error type
✅ Rate limiting handled gracefully
✅ Confirmation requests expire after timeout
✅ Permission denied errors are clear and secure

## Related Components
- **Natural Language Tool Mapping**: Generates confirmations
- **OpenAI Agents SDK**: Receives error/confirmation messages
- **Stateless Chat Endpoints**: Persist error/confirmation state
- **Conversation DB**: Store confirmation state for resumption
- **Error Logging**: Log errors with correlation IDs for debugging

## Confirmation Flow Diagram

```
User Input
    ↓
Pending Confirmation?
    ├─ Yes → Parse Response → Execute or Cancel
    └─ No → Map to Tool
         ↓
    Requires Confirmation?
         ├─ Yes → Show Confirmation → Wait
         └─ No → Execute
             ↓
         Success?
         ├─ Yes → Success Message
         └─ No → Error Message + Recovery Suggestions
```

## Best Practices

### Confirmation Messages
- ✅ Use emojis for visual clarity
- ✅ Show exactly what will happen
- ✅ Ask clear yes/no questions
- ✅ Suggest recovery paths for errors

### Error Messages
- ✅ Be empathetic ("Something went wrong...")
- ✅ Explain what happened (specific error)
- ✅ Suggest action (try again, wait, contact support)
- ✅ Provide debugging info (correlation ID) when needed

### Avoid
- ❌ Confusing error codes (500 Internal Server Error)
- ❌ Vague messages ("Error")
- ❌ Assuming user can fix it (no guidance)
- ❌ Unnecessary confirmations for safe operations

## Testing Checklist
- [ ] Delete confirmation works
- [ ] Confirmation expiration handled
- [ ] Task-not-found shows suggestions
- [ ] Success messages are encouraging
- [ ] Server errors include correlation ID
- [ ] Rate limit backoff works
- [ ] Permission denied is clear
- [ ] Confirmation state survives conversation refresh
- [ ] Multi-attempt confirmation parsing works
- [ ] Recovery suggestions are actionable
