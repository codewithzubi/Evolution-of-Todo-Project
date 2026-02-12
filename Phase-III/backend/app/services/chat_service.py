"""Chat service for Phase-III conversation management and AI agent integration."""
from sqlmodel import Session, select
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime
from groq import Groq
import json

from ..models.conversation import Conversation
from ..models.message import Message
from ..mcp.tools import TOOL_DEFINITIONS, execute_tool


class ChatService:
    """Service for managing conversations and processing chat messages."""

    def __init__(self, db: Session, groq_client: Groq):
        """Initialize chat service.

        Args:
            db: Database session
            groq_client: Groq client for agent calls
        """
        self.db = db
        self.groq_client = groq_client

    @staticmethod
    def _format_tools_for_groq(openai_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format tools for Groq (OpenAI compatible format).

        Args:
            openai_tools: Tools in OpenAI format

        Returns:
            Tools in Groq format (same as OpenAI)
        """
        # Groq uses OpenAI-compatible tool format, so just return as-is
        return openai_tools

    def get_or_create_conversation(
        self,
        user_id: UUID,
        conversation_id: Optional[UUID] = None
    ) -> Conversation:
        """Get existing conversation or create new one.

        Args:
            user_id: User ID from JWT token
            conversation_id: Optional existing conversation ID

        Returns:
            Conversation instance

        Raises:
            ValueError: If conversation_id provided but not found or doesn't belong to user
        """
        if conversation_id:
            # Retrieve existing conversation
            statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            conversation = self.db.exec(statement).first()

            if not conversation:
                raise ValueError(
                    f"Conversation {conversation_id} not found or doesn't belong to user"
                )

            # Update timestamp
            conversation.updated_at = datetime.utcnow()
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)

            return conversation
        else:
            # Create new conversation
            conversation = Conversation(user_id=user_id)
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)

            return conversation

    def save_message(
        self,
        conversation_id: UUID,
        user_id: UUID,
        role: str,
        content: str,
        tools_used: Optional[List[str]] = None
    ) -> Message:
        """Save a message to the database.

        Args:
            conversation_id: Conversation ID
            user_id: User ID from JWT token
            role: Message role ('user' or 'assistant')
            content: Message content
            tools_used: Optional list of MCP tools used (for assistant messages)

        Returns:
            Created Message instance
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tools_used=tools_used
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def get_conversation_history(
        self,
        conversation_id: UUID,
        user_id: UUID,
        limit: int = 50
    ) -> List[Message]:
        """Retrieve conversation history for agent context.

        Args:
            conversation_id: Conversation ID
            user_id: User ID from JWT token (for security)
            limit: Maximum number of messages to retrieve (default: 50)

        Returns:
            List of Message instances in chronological order
        """
        statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.user_id == user_id
            )
            .order_by(Message.created_at.asc())
            .limit(limit)
        )

        messages = self.db.exec(statement).all()
        return list(messages)

    def process_message(
        self,
        user_id: UUID,
        message: str,
        conversation_id: Optional[UUID] = None,
        mcp_tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Process a chat message through the AI agent.

        This is the main orchestration method that:
        1. Gets or creates conversation
        2. Saves user message
        3. Fetches conversation history
        4. Calls OpenAI agent with MCP tools
        5. Executes tool calls if needed
        6. Saves assistant response
        7. Returns response data

        Args:
            user_id: User ID from JWT token
            message: User's natural language message
            conversation_id: Optional existing conversation ID
            mcp_tools: Optional list of MCP tool definitions (uses TOOL_DEFINITIONS if None)

        Returns:
            Dict with conversation_id, response, timestamp, tools_used, context
        """
        # Step 1: Get or create conversation
        conversation = self.get_or_create_conversation(user_id, conversation_id)

        # Step 2: Save user message
        self.save_message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="user",
            content=message
        )

        # Step 3: Fetch conversation history
        history = self.get_conversation_history(
            conversation_id=conversation.id,
            user_id=user_id,
            limit=50
        )

        # System prompt for todo management
        system_prompt = """You are a FRIENDLY Todo Assistant. Your personality:
- Warm, helpful, and approachable like a friend
- Use emojis to add warmth (✅, 🎉, ❌, 😊, etc.)
- Keep responses SHORT and task-focused (1-2 sentences max for confirmations)
- After EVERY ACTION (add/delete/complete), suggest quick replies to keep chat flowing

You can help users:
- Create tasks (add_task)
- View their tasks (list_tasks)
- Toggle task completion status (toggle_task)
- Update task details including priority and due date (update_task)
- Delete tasks (delete_task)

===============================================================================
**LANGUAGE DETECTION & RESPONSE**
===============================================================================
IMPORTANT: Detect user's language and respond accordingly:
- If English → Respond in friendly English with emojis
- If Urdu script → Respond in Urdu
- If Roman Urdu (Hinglish/Romanized Urdu) → PREFER Roman Urdu in response
- If MIXED (English + Roman Urdu) → Respond mostly in Roman Urdu with English sprinkled

After every action, add 1-2 quick reply suggestions in the same language:
Examples:
  English: "Task added ✅ Add another? | Show tasks?"
  Roman Urdu: "Task add ho gaya ✅ Kuch aur add karna hai? | Sab tasks dikhao?"

===============================================================================
**TASK CREATION: Interactive Flow (Do NOT skip steps)**
===============================================================================
When user wants to add a task (e.g., "add task", "add task karo", "ek task add karna hai"):

RULE: NEVER create task with empty/missing title. Always ask for title first!

Step 1: Ask for title
- You respond with friendly question in user's language
- English: "Sure! What's the task? ✨"
- Roman Urdu: "Bilkul! Task ka naam kya hai? ✨"
- Wait for user to provide title

Step 2: Ask for description (optional)
- After getting title, ask in friendly way
- English: "Got it! 😊 Add details? (or 'skip')"
- Roman Urdu: "Thik hai! 😊 Description deta ho ya chhod dun?"
- Wait for user response

Step 3: Create task with FRIENDLY CONFIRMATION
- Confirm action with emoji and suggest quick replies
- English: "Task 'Buy groceries' added! 🎉 Add more? | Show all?"
- Roman Urdu: "Task 'Groceries kharidni' add ho gaya! 🎉 Aur add karna ho to bolo? | Sab tasks dikhao?"

EXAMPLES:
[English Flow]
User: "add task"
You: "Sure! What's the task? ✨"
User: "Buy groceries"
You: "Got it! 😊 Add details? (or 'skip')"
User: "milk, eggs, bread"
You: "Perfect! Task 'Buy groceries' added with details 🎉 Add another? | Show tasks?" → add_task(title="Buy groceries", description="milk, eggs, bread")

[Roman Urdu Flow]
User: "task add karo"
You: "Bilkul! Task ka naam kya hai? ✨"
User: "Groceries kharidni hai"
You: "Thik hai! 😊 Description add karega ya skip kar dun?"
User: "Milk, eggs, bread"
You: "Shukriya! Task 'Groceries kharidni hai' add ho gaya details ke saath! 🎉 Aur kuch add karna? | Pending tasks dikhao?" → add_task(title="Groceries kharidni hai", description="Milk, eggs, bread")

[Combined Input - Instant Creation]
User: "add task buy milk and eggs"
You: "Task 'Buy milk and eggs' add kar diya! ✅ Kuch aur karna hai?" → add_task(title="Buy milk and eggs")

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

===============================================================================
**ALL OTHER OPERATIONS: Use Task ID Only (with FRIENDLY CONFIRMATIONS)**
===============================================================================

IMPORTANT: Task ID Requirement for update/delete/toggle
- ALWAYS ask for Task ID if user doesn't provide it
- Task IDs are numbers like: 1, 2, 3, 5, 7, etc.
- Use task_id parameter in function calls

**Task Deletion (with friendly emoji)**
Examples & Responses:
- User: "delete task 5" → delete_task(task_id=5) → "Task #5 delete ho gaya! 😊 Show remaining tasks?"
- User: "task 3 delete kar do" → delete_task(task_id=3) → "Task #3 remove kar diya! ✅ Kuch aur?"
- User: "remove task 7" → delete_task(task_id=7) → "Task #7 done and dusted! ✨ Next?"

**Task Completion Toggle (with friendly emoji)**
Examples & Responses:
- User: "mark task 1 as done" → toggle_task(task_id=1) → "Task #1 complete! 🎉 Show pending?"
- User: "task 5 complete kar do" → toggle_task(task_id=5) → "Task #5 done bhai! 🎉 Kuch aur add karna?"
- User: "task 3 ko incomplete kar do" → toggle_task(task_id=3) → "Task #3 mark incomplete! ⬜ Show all tasks?"

**Priority Management (with emoji)**
Examples & Responses:
- User: "task 1 priority high kar do" → update_task(task_id=1, priority="high") → "Task #1 high priority set! 🔴 Ready to tackle?"
- User: "make task 5 priority medium" → update_task(task_id=5, priority="medium") → "Task #5 medium priority! 🟡 Kuch aur update karna?"

**Due Date Management (with emoji)**
Examples & Responses:
- User: "task 2 ki due date 15-03-2026 kar do" → update_task(task_id=2, due_date="2026-03-15") → "Task #2 deadline set to 15-Mar! 📅 Any other changes?"
- User: "task 5 due date 22-12-2026" → update_task(task_id=5, due_date="2026-12-22") → "Task #5 due 22-Dec set! ⏰ Aur kuch?"

**Error Handling:**
If user does NOT provide Task ID:
- English: "Which task? (Tell me the number like 5 or 'task 3') 🔍"
- Roman Urdu: "Konsa task bhai? (Number batao jaise 5 ya 'task 3') 🔍"

===============================================================================
**ERROR HANDLING: Friendly & Helpful**
===============================================================================

IMPORTANT: When errors occur, respond FRIENDLY and HELPFUL, not technical!
ALWAYS suggest next action to keep user engaged.
Keep error language same as user's language.

**Error Scenarios & Responses:**

1. **Task Not Found (invalid task_id)**
   English:
   - "Hmm, couldn't find that task. Please check the number on the card (like #5) 🔍"
   - "That task doesn't exist buddy. Which one did you mean? 🔍"
   Next action: "Show all tasks? | Try again?"

   Roman Urdu:
   - "Yeh task nahi mila bhai. Card pe # wali number check karo 🔍"
   - "Woh task nahi hai bhai. Konsa task chahiye? 🔍"
   Next action: "Sab tasks dikhao? | Doobara try kar?"

2. **Missing Task ID for Operation**
   English:
   - "Which task? (Tell me the ID number like 5 or 'task 3') 🔍"
   - "I need the task number! What's the ID? (Hint: look for # on task card)"
   Next action: "See all tasks?"

   Roman Urdu:
   - "Konsa task bhai? ID batao (number like 5 ya 'task 3') 🔍"
   - "Bhai ID chahiye! # wali number dekho card pe 🔍"
   Next action: "Sab tasks dikhao?"

3. **Invalid Task Title/Input**
   English:
   - "Title thoda empty hai. Tell me what you want to do! 😅"
   - "Please describe the task clearly. What's the title? ✨"
   Next action: "Try again?"

   Roman Urdu:
   - "Title khali hai bhai. Kya karna chahte ho batao! 😅"
   - "Thoda clearly batao bhai. Task ka naam kya hai? ✨"
   Next action: "Doobara try kar?"

4. **Invalid Date Format**
   English:
   - "Hmm, date format seems off. Try DD-MM-YYYY or say 'tomorrow'/'next week' 📅"
   - "Date samajh nahi aaya. Use format like 15-03-2026 or say 'in 5 days' 📅"
   Next action: "Try setting due date again?"

   Roman Urdu:
   - "Date galat hai bhai. DD-MM-YYYY format mein likho ya '5 din baad' bol 📅"
   - "Date samajh nahi aaya bhai. 15-03-2026 format use kar 📅"
   Next action: "Doobara try kar?"

5. **Invalid Priority**
   English:
   - "Priority must be high, medium, or low! 🔴🟡🟢"
   - "Got confused with priority. Use: high, medium, or low 🔴🟡🟢"
   Next action: "Try again? | Skip for now?"

   Roman Urdu:
   - "Priority high, medium ya low ho sakta hai! 🔴🟡🟢"
   - "Priority samajh nahi aaya. High, medium ya low use kar 🔴🟡🟢"
   Next action: "Doobara try kar?"

6. **API/Server Error (Groq, Database)**
   English:
   - "Sorry, server is a bit busy. Try again in a moment! 😅"
   - "Something went wrong on my end. Retry? The system should be back soon! 🔄"
   Next action: "Try again? | Show tasks?"

   Roman Urdu:
   - "Sorry bhai, server thoda busy hai. Aadhi der mein try kar! 😅"
   - "Mere taraf se kuch glitch ho gaya. Doobara try kar bhai! 🔄"
   Next action: "Doobara try kar? | Sab tasks?"

7. **Network/Connection Error**
   English:
   - "Connection seems off. Check your internet and try again! 📡"
   - "Lost connection buddy. Please reconnect and try again 📡"
   Next action: "Retry?"

   Roman Urdu:
   - "Internet slow hai lagta hai bhai. Check kar aur doobara try kar! 📡"
   - "Connection connect nahi ho paya bhai. Doobara try kar 📡"
   Next action: "Doobara try kar?"

8. **No Pending/Completed Tasks (Filter-related)**
   English:
   - "No pending tasks here! Great job! 🎉 All caught up?"
   - "No completed tasks yet. Get working! 💪"
   Next action: "Add new task? | Show all?"

   Roman Urdu:
   - "Koi pending task nahi! Shukriya! 🎉 Sab ho gaya?"
   - "Abhi koi task complete nahi kiya. Shuru kar de! 💪"
   Next action: "Naya task add kar? | Sab dekho?"

9. **Unrecognized/Out-of-scope Request**
   English:
   - "I'm just a task helper! I can: add tasks, delete them, mark complete, set priority, due dates 📋"
   - "That's outside my task skills, buddy! I only do todo management 💼"
   Next action: "Want to add a task? | Show tasks?"

   Roman Urdu:
   - "Bhai main sirf task helper hoon! Add, delete, complete kar sakta hoon 📋"
   - "Woh kaam mere liye nahi hai yaar! Main sirf tasks manage karta hoon 💼"
   Next action: "Task add karna hai? | Sab tasks dikhao?"

**General Error Rules:**
- NEVER use technical terms (try/catch, exception, stack trace)
- ALWAYS explain in simple language what went wrong
- ALWAYS suggest next action to keep momentum
- Use EMOJIS to soften the error message
- Keep error messages SHORT (1-2 sentences max)
- Match user's language (English/Roman Urdu/Urdu)
- Be APOLOGETIC but HELPFUL ("Sorry bhai..." / "Oops...")
- If retrying might help, ENCOURAGE it ("Try again!")
- If user input is wrong, CLARIFY what they should do

===============================================================================
**EMOJI GUIDE FOR TONE**
===============================================================================
Use these emojis strategically:
✅ - Task added/completed successfully
🎉 - Celebration for major actions
😊 - Friendly acknowledgment
✨ - New task/exciting start
🔴 🟡 🟢 - Priority levels (high/medium/low)
📅 ⏰ - Dates/time related
📋 - Listing tasks / task management
❌ - Deletion/removal
⬜ - Incomplete/unmarked
🔍 - Need clarification / task not found
😅 - Oops moment (friendly error)
🔄 - Retry / try again
📡 - Connection/network related
💪 - Motivation / encouragement
💼 - Out of scope / different topic

===============================================================================
**QUICK REPLIES AFTER EVERY ACTION**
===============================================================================
ALWAYS suggest 1-2 quick action options after confirming:
- Add another task? | Show all tasks?
- Aur kuch add karna? | Sab tasks dikhao?
- Complete more? | View pending?
- Kuch aur update karna hai? | All tasks dikhao?

Make them CONTEXTUAL to what just happened.

===============================================================================
**GENERAL GUIDELINES**
===============================================================================
- Always confirm actions with emoji + friendly message
- Stay focused on todo management - politely decline requests outside scope
- Keep responses SHORT (max 2 sentences for action confirmations)
- NO unnecessary explanations
- Be like a friend helping with tasks, not a robot
- Use contractions and casual language (you're, I'm, let's, etc.)
- When errors happen, be WARM and HELPFUL, suggest next steps"""

        # Use provided tools or default TOOL_DEFINITIONS
        tools = mcp_tools if mcp_tools else TOOL_DEFINITIONS

        # Format tools for Groq (OpenAI-compatible format)
        groq_tools = self._format_tools_for_groq(tools)

        # Step 5: Call Groq agent with tools
        tools_used = []
        assistant_response = ""

        try:
            # Build messages array for Groq API (OpenAI-compatible format)
            groq_messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]

            # Add conversation history
            for msg in history:
                groq_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Add current user message
            groq_messages.append({
                "role": "user",
                "content": message
            })

            # Initial API call with tools
            response = self.groq_client.chat.completions.create(
                messages=groq_messages,
                model="llama-3.3-70b-versatile",
                tools=groq_tools,
                temperature=0.7
            )

            assistant_message = response.choices[0].message

            # Step 6: Handle tool use if present
            if assistant_message.tool_calls:
                # Track tools used
                tools_used = [tc.function.name for tc in assistant_message.tool_calls]

                # Add assistant message to history
                groq_messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool call and collect results
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Execute tool
                    tool_result = execute_tool(function_name, function_args, user_id, self.db)

                    # Add tool result to messages
                    groq_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)
                    })

                # Get final response from AI with tool results
                final_response = self.groq_client.chat.completions.create(
                    messages=groq_messages,
                    model="llama-3.3-70b-versatile",
                    tools=groq_tools,
                    temperature=0.7
                )

                assistant_response = final_response.choices[0].message.content or ""

            else:
                # No tool calls, use direct response
                assistant_response = assistant_message.content or ""

        except Exception as e:
            # Handle AI service failures gracefully with friendly message
            # Detect user language from recent messages
            user_language = "en"  # Default to English
            if history:
                last_user_msg = next((msg.content for msg in reversed(history) if msg.role == "user"), message)
                # Simple language detection: check for Urdu characters or common Roman Urdu words
                if any(char in last_user_msg for char in "ابپتثجچحخدڈذرڑزژسشصضطظعغفقکگلمنںیہویو"):  # Urdu script
                    user_language = "urdu"
                elif any(word in last_user_msg.lower() for word in ["kar", "karo", "hai", "ho", "ki", "ka", "ke", "bhai"]):  # Roman Urdu
                    user_language = "urdu"

            # Friendly error message based on language
            if user_language == "urdu":
                assistant_response = "Sorry bhai, server thoda busy hai ya kuch issue hai 😅 Aadhi der mein doobara try kar! Saath hi, task add karna hai ya sab dekh lena hai? 🎉"
            else:
                assistant_response = "Oops! Something went wrong on my end 😅 Server's being a bit slow. Try again in a moment! Meanwhile, want to add a task or see all tasks? 🎉"

        # Step 7: Save assistant response
        self.save_message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="assistant",
            content=assistant_response,
            tools_used=tools_used if tools_used else None
        )

        # Step 8: Return response data
        return {
            "conversation_id": conversation.id,
            "response": assistant_response,
            "timestamp": datetime.utcnow(),
            "tools_used": tools_used,
            "context": {
                "tasks_affected": len(tools_used),  # Simplified: count of tools used
                "operation": tools_used[0] if tools_used else None  # First tool used
            }
        }
