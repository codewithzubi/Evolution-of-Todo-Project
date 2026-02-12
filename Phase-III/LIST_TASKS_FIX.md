# List Tasks Tool Fix – Critical Agent Behavior Update

## Problem Statement

**Issue:** Chatbot was not properly calling `list_tasks` tool when users asked to see/show/view their tasks.

**Examples that were NOT working:**
- User: "show my all tasks" → Bot: Generic response, no tool call ❌
- User: "how many task you have?" → Bot: "Server busy", no actual data ❌
- User: "show pending tasks" → Bot: Ignored status parameter ❌

**Root Cause:** System prompt lacked a dedicated, prominent section emphasizing that `list_tasks` MUST be called when users ask to view tasks.

---

## Solution Implemented

### 1. System Prompt Enhancement

Added a **CRITICAL: LIST TASKS** section (lines 268-337) that:
- **Clearly states:** ALWAYS call list_tasks when user asks to SEE/SHOW/LIST/VIEW/HOW MANY tasks
- **Prevents generic responses:** "Do NOT say server busy" → "Use tool to fetch real data"
- **Defines recognition patterns:** Lists 20+ phrases that trigger list_tasks
- **Provides 6 detailed examples:** With exact tool calls and expected responses
- **Guides status parameter:** Explains when to use "all", "pending", "completed"
- **Shows correct response format:** How to use tool result in response

### 2. Tool Definition Update

Updated `list_tasks` function and tool definition:

**Before:**
```python
"status": "enum": ["all", "complete", "incomplete"]

def list_tasks(..., status: str):
    if status == "complete":  # Only 2 options
    elif status == "incomplete":
    # else: no "all" handling
```

**After:**
```python
"status": "enum": ["all", "pending", "completed"]

def list_tasks(..., status: str = "all"):
    status_lower = status.lower()
    if status_lower in ["completed", "complete", "done"]:
        # Flexible - accepts multiple variations
    elif status_lower in ["pending", "incomplete", "todo", "active"]:
        # Flexible - accepts multiple variations
    # else: status_lower == "all" - no filter
```

**Benefits:**
- ✅ Supports natural language: "pending" and "completed" (not just "complete"/"incomplete")
- ✅ Flexible: accepts variations like "active", "todo", "done"
- ✅ Default value: `status="all"` if not specified
- ✅ Tool result enhanced: includes priority and description fields
- ✅ Tool description updated: explicitly states "ALWAYS call this when user asks to see/show/list/view tasks"

---

## How It Works Now

### Recognition Patterns (Agent will ALWAYS call list_tasks for these)

**English Phrases:**
- "show tasks", "show my tasks", "show all tasks", "show my all tasks"
- "list tasks", "list my tasks", "what tasks do i have"
- "how many tasks", "how many task you have", "task count"
- "view tasks", "see my tasks", "display tasks"

**Roman Urdu Phrases:**
- "sab tasks dikhao", "mere tasks dikhao", "kitne tasks hain"

**Status-Specific:**
- "pending tasks", "completed tasks", "show pending", "show completed"

### Tool Call Examples

```
User: "show my all tasks"
Agent: list_tasks(status="all")
Response: "Sab tasks yahan hain! 📋 [Lists all 5 tasks] Complete karna hai ya naya add karna hai?"

User: "how many task you have?"
Agent: list_tasks(status="all")
Response: "You have 5 tasks total! 📊 [Shows count breakdown] Want to see them? | Add more?"

User: "show pending tasks"
Agent: list_tasks(status="pending")
Response: "Pending tasks: 3 bhai! ⏳ [Lists only incomplete tasks] Sab ho jayega! | Add more?"

User: "sab tasks dikhao"
Agent: list_tasks(status="all")
Response: "Sab tasks yahan hain bhai! 📋 [Lists tasks] Kuch complete kar ya add karna?"
```

### Status Parameter Guide

| User Request | Status Value | Result |
|---|---|---|
| "show all tasks" | `"all"` | All tasks (pending + completed) |
| "show pending" / "incomplete" | `"pending"` | Only pending (not completed) tasks |
| "show completed" / "done" | `"completed"` | Only completed tasks |
| No status specified | `"all"` (default) | All tasks |

---

## System Prompt Section - CRITICAL: LIST TASKS

```markdown
===============================================================================
**CRITICAL: LIST TASKS - ALWAYS CALL list_tasks TOOL (DO NOT SKIP)**
===============================================================================

IMPORTANT: When user asks to SEE/SHOW/LIST/VIEW/HOW MANY tasks → IMMEDIATELY call list_tasks!
- DO NOT say "server busy" or generic responses
- DO NOT skip the tool call - FETCH REAL DATA from database
- ALWAYS use the tool result in your response

**Recognition Patterns - Call list_tasks for ANY of these:**
- "show tasks", "show my tasks", "show all tasks", "show my all tasks"
- "list tasks", "list my tasks", "what tasks do i have"
- "how many tasks", "how many task you have", "task count"
- "view tasks", "see my tasks", "display tasks"
- "sab tasks dikhao", "mere tasks dikhao", "kitne tasks hain"
- "pending tasks", "completed tasks", "show pending", "show completed"
- Any variation asking to view/display/show/list task data

**EXACT IMPLEMENTATION - Examples with Tool Calls:**

Example 1: Generic "show my tasks"
User: "show my tasks"
→ list_tasks(status="all")  [fetch ALL tasks]
→ Response: "Yeh rahe teri tasks! 📋 [Count: 5 tasks] Show pending only? | Add new? | Kuch aur?"

Example 2: "show my all tasks"
User: "show my all tasks"
→ list_tasks(status="all")  [user explicitly wants ALL]
→ Response: "Sab tasks yahan hain! 📋 [Lists all 5 tasks] Complete karna hai ya naya add karna hai?"

Example 3: "how many task you have?"
User: "how many task you have?"
→ list_tasks(status="all")  [fetch to get count]
→ Response: "You have 5 tasks total! 📊 [Shows count breakdown] Want to see them? | Add more?"

Example 4: "show pending tasks"
User: "show pending tasks"
→ list_tasks(status="pending")  [user specifically wants pending]
→ Response: "Pending tasks: 3 bhai! ⏳ [Lists pending tasks] Sab ho jayega! | Add more?"

Example 5: "sab tasks dikhao"
User: "sab tasks dikhao"
→ list_tasks(status="all")  [user wants all in Roman Urdu]
→ Response: "Sab tasks yahan hain bhai! 📋 [Lists tasks] Kuch complete kar ya add karna?"

Example 6: Mix of questions in one message
User: "How many tasks and can you show pending ones?"
→ list_tasks(status="pending")  [focus on pending as explicitly requested]
→ Response: "3 pending tasks bhai! ⏳ [Shows them] Mark complete? | Show all?"

**STATUS PARAMETER GUIDE:**
- status="all" → Fetch ALL tasks (completed + pending)
- status="pending" → Fetch ONLY pending (incomplete) tasks
- status="completed" → Fetch ONLY completed tasks
- If user doesn't specify, use status="all" (show everything)
- If user says "pending" → use status="pending"
- If user says "completed" → use status="completed"

**RESPONSE FORMAT AFTER TOOL CALL:**
1. Greet with emoji related to listing (📋, 📊, ⏳)
2. State count or summary (e.g., "You have 5 tasks total")
3. List the actual tasks from tool result (or say "No tasks" if empty)
4. Suggest next action (complete, add, filter, etc.)
5. Keep it SHORT (2-3 sentences max)

**COMMON MISTAKES - DO NOT DO THESE:**
❌ Say "server busy" - fetch the data instead!
❌ Skip tool call - always call list_tasks!
❌ Generic response - use actual tool result!
❌ Ignore status parameter - respect user's intent (pending vs all)
❌ Don't count correctly - use tool result to get accurate count
```

---

## Tool Implementation Changes

### Function Signature

```python
def list_tasks(user_id: UUID, status: str = "all", db: Session = None) -> Dict[str, Any]:
    """List user's tasks by status filter."""
```

### Status Handling

```python
status_lower = status.lower() if status else "all"

# Flexible status matching
if status_lower in ["completed", "complete", "done"]:
    query = query.where(Task.is_completed == True)
elif status_lower in ["pending", "incomplete", "todo", "active"]:
    query = query.where(Task.is_completed == False)
# else: "all" - no filter applied
```

### Enhanced Response

```python
{
    "status": "success",
    "tasks": [
        {
            "id": "1",
            "title": "Buy groceries",
            "completed": False,
            "priority": "high",
            "description": "Milk, eggs, bread"
        },
        ...
    ],
    "count": 5
}
```

### Tool Definition

```python
{
    "type": "function",
    "function": {
        "name": "list_tasks",
        "description": "List user's tasks filtered by status. ALWAYS call this when user asks to see/show/list/view tasks.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "description": "Filter tasks by status: 'all' (show everything), 'pending' (incomplete tasks), 'completed' (done tasks). Default is 'all'."
                }
            },
            "required": []
        }
    }
}
```

---

## Testing Checklist

- [ ] "show my tasks" → Calls list_tasks(status="all")
- [ ] "show my all tasks" → Calls list_tasks(status="all")
- [ ] "how many task you have?" → Calls list_tasks with count in response
- [ ] "show pending tasks" → Calls list_tasks(status="pending")
- [ ] "show completed tasks" → Calls list_tasks(status="completed")
- [ ] "sab tasks dikhao" → Calls list_tasks(status="all")
- [ ] "list tasks" → Calls list_tasks(status="all")
- [ ] Empty result → "No tasks" message, suggests "Add new task?"
- [ ] Single task → Shows correctly with priority and description
- [ ] Multiple tasks → Lists all with counts
- [ ] No "server busy" message → Uses real tool data
- [ ] Response uses tool result → Not generic text
- [ ] Emoji added → 📋 or 📊 or ⏳ appropriately
- [ ] Quick replies added → Next action suggested
- [ ] Status parameter respected → Correct tasks shown
- [ ] Works in Roman Urdu → "sab tasks", "kitne tasks"

---

## Files Modified

1. **backend/app/services/chat_service.py**
   - Added "CRITICAL: LIST TASKS" section in system prompt (lines 268-337)
   - Includes 6 examples, status guide, response format, common mistakes

2. **backend/app/mcp/tools.py**
   - Updated `list_tasks()` function for flexible status handling
   - Enhanced response with priority and description
   - Updated tool definition with "all", "pending", "completed" enum
   - Clarified tool description about always calling list_tasks

---

## Git Commit

```
f2f60ee - fix: Fix chatbot list_tasks tool to always be called for show/view requests
```

---

## Summary

The chatbot will now **ALWAYS** call the `list_tasks` tool whenever users ask to see, show, list, view, or count their tasks. No more generic "server busy" responses – actual data from the database is fetched and displayed to users.

**Key Improvements:**
- ✅ Explicit agent instruction in system prompt
- ✅ Support for natural language status parameters ("pending", "completed")
- ✅ Flexible status matching (accepts multiple variations)
- ✅ Enhanced tool response with complete task details
- ✅ Detailed examples showing correct tool usage
- ✅ Clear distinction between different status filters
- ✅ Better error prevention with "common mistakes" section

