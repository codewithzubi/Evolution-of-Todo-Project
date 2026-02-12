# Error Handling Guide - Friendly & Helpful

## Overview

The chatbot now provides friendly, helpful error messages across 9 different error scenarios. All error messages are:
- ✅ Non-technical (no jargon)
- ✅ Clear and actionable
- ✅ Multilingual (English & Roman Urdu)
- ✅ Include next action suggestions
- ✅ Use emojis for warmth

---

## Error Scenarios & Responses

### 1. Task Not Found (Invalid Task ID)

**Scenario:** User tries to delete/complete/update a task that doesn't exist.

**English Response:**
```
"Hmm, couldn't find that task. Please check the number on the card (like #5) 🔍"
"That task doesn't exist buddy. Which one did you mean? 🔍"
```

**Roman Urdu Response:**
```
"Yeh task nahi mila bhai. Card pe # wali number check karo 🔍"
"Woh task nahi hai bhai. Konsa task chahiye? 🔍"
```

**Next Action:** "Show all tasks? | Try again?"

**Example User Flow:**
```
User: "delete task 999"
Bot: "Hmm, couldn't find that task. Please check the number on the card (like #5) 🔍
      Show all tasks? | Try again?"
```

---

### 2. Missing Task ID for Operation

**Scenario:** User doesn't provide task ID when deleting/updating/completing.

**English Response:**
```
"Which task? (Tell me the ID number like 5 or 'task 3') 🔍"
"I need the task number! What's the ID? (Hint: look for # on task card)"
```

**Roman Urdu Response:**
```
"Konsa task bhai? ID batao (number like 5 ya 'task 3') 🔍"
"Bhai ID chahiye! # wali number dekho card pe 🔍"
```

**Next Action:** "See all tasks?"

**Example User Flow:**
```
User: "delete the grocery task"
Bot: "Which task? (Tell me the ID number like 5 or 'task 3') 🔍
      See all tasks?"
```

---

### 3. Invalid Task Title/Input

**Scenario:** User provides empty or unclear task title.

**English Response:**
```
"Title thoda empty hai. Tell me what you want to do! 😅"
"Please describe the task clearly. What's the title? ✨"
```

**Roman Urdu Response:**
```
"Title khali hai bhai. Kya karna chahte ho batao! 😅"
"Thoda clearly batao bhai. Task ka naam kya hai? ✨"
```

**Next Action:** "Try again?"

**Example User Flow:**
```
User: "add task"
Bot: "Sure! What's the task? ✨"
User: ""
Bot: "Title thoda empty hai. Tell me what you want to do! 😅
      Try again?"
```

---

### 4. Invalid Date Format

**Scenario:** User provides date in wrong format.

**English Response:**
```
"Hmm, date format seems off. Try DD-MM-YYYY or say 'tomorrow'/'next week' 📅"
"Date samajh nahi aaya. Use format like 15-03-2026 or say 'in 5 days' 📅"
```

**Roman Urdu Response:**
```
"Date galat hai bhai. DD-MM-YYYY format mein likho ya '5 din baad' bol 📅"
"Date samajh nahi aaya bhai. 15-03-2026 format use kar 📅"
```

**Next Action:** "Try setting due date again?"

**Example User Flow:**
```
User: "task 3 due date 03/15/2026"
Bot: "Hmm, date format seems off. Try DD-MM-YYYY or say 'tomorrow'/'next week' 📅
      Try setting due date again?"
```

**Accepted Formats:**
- `DD-MM-YYYY` (15-03-2026)
- `YYYY-MM-DD` (2026-03-15)
- Natural language (tomorrow, next week, in 5 days)

---

### 5. Invalid Priority

**Scenario:** User specifies invalid priority (not high/medium/low).

**English Response:**
```
"Priority must be high, medium, or low! 🔴🟡🟢"
"Got confused with priority. Use: high, medium, or low 🔴🟡🟢"
```

**Roman Urdu Response:**
```
"Priority high, medium ya low ho sakta hai! 🔴🟡🟢"
"Priority samajh nahi aaya. High, medium ya low use kar 🔴🟡🟢"
```

**Next Action:** "Try again? | Skip for now?"

**Example User Flow:**
```
User: "task 5 priority urgent"
Bot: "Priority must be high, medium, or low! 🔴🟡🟢
      Try again? | Skip for now?"
```

**Valid Priorities:**
- `high` (🔴 Red)
- `medium` (🟡 Yellow)
- `low` (🟢 Green)

---

### 6. API/Server Error

**Scenario:** Groq API is slow, database timeout, or service error.

**English Response:**
```
"Sorry, server is a bit busy. Try again in a moment! 😅"
"Something went wrong on my end. Retry? The system should be back soon! 🔄"
```

**Roman Urdu Response:**
```
"Sorry bhai, server thoda busy hai. Aadhi der mein try kar! 😅"
"Mere taraf se kuch glitch ho gaya. Doobara try kar bhai! 🔄"
```

**Next Action:** "Try again? | Show tasks?"

**Example User Flow:**
```
User: "add task buy milk"
[Server timeout]
Bot: "Sorry, server is a bit busy. Try again in a moment! 😅
      Try again? | Show tasks?"
```

---

### 7. Network/Connection Error

**Scenario:** Internet connectivity issue, request timeout.

**English Response:**
```
"Connection seems off. Check your internet and try again! 📡"
"Lost connection buddy. Please reconnect and try again 📡"
```

**Roman Urdu Response:**
```
"Internet slow hai lagta hai bhai. Check kar aur doobara try kar! 📡"
"Connection connect nahi ho paya bhai. Doobara try kar 📡"
```

**Next Action:** "Retry?"

**Example User Flow:**
```
User: "show tasks"
[Network timeout]
Bot: "Connection seems off. Check your internet and try again! 📡
      Retry?"
```

---

### 8. No Pending/Completed Tasks (Filter-related)

**Scenario:** User filters by pending/completed but no tasks match.

**English Response - No Pending:**
```
"No pending tasks here! Great job! 🎉 All caught up?"
```

**English Response - No Completed:**
```
"No completed tasks yet. Get working! 💪"
```

**Roman Urdu Response - No Pending:**
```
"Koi pending task nahi! Shukriya! 🎉 Sab ho gaya?"
```

**Roman Urdu Response - No Completed:**
```
"Abhi koi task complete nahi kiya. Shuru kar de! 💪"
```

**Next Action:** "Add new task? | Show all?"

**Note:** This is handled by the EmptyState component but good to mention in error handling.

---

### 9. Unrecognized/Out-of-scope Request

**Scenario:** User asks for something outside task management (weather, jokes, etc.).

**English Response:**
```
"I'm just a task helper! I can: add tasks, delete them, mark complete, set priority, due dates 📋"
"That's outside my task skills, buddy! I only do todo management 💼"
```

**Roman Urdu Response:**
```
"Bhai main sirf task helper hoon! Add, delete, complete kar sakta hoon 📋"
"Woh kaam mere liye nahi hai yaar! Main sirf tasks manage karta hoon 💼"
```

**Next Action:** "Want to add a task? | Show tasks?"

**Example User Flow:**
```
User: "What's the weather today?"
Bot: "I'm just a task helper! I can: add tasks, delete them, mark complete, set priority, due dates 📋
      Want to add a task? | Show tasks?"
```

---

## Error Message Best Practices

### ✅ DO:
- Use friendly, conversational tone
- Include emoji for visual appeal
- Explain what went wrong in simple terms
- Suggest how to fix it
- Offer next action
- Match user's language preference
- Keep it SHORT (1-2 sentences)
- Be apologetic ("Sorry", "Oops", "Hmm")
- Use casual language ("bhai", "buddy", "pal")

### ❌ DON'T:
- Use technical jargon (exception, error code, stack trace)
- Be apologetic without helping (just say "sorry" without guidance)
- Give up (always suggest a way forward)
- Use formal, robotic language
- Overwhelm with long explanations
- Ignore the user's language preference
- Blame the user ("You did this wrong")

---

## Language Detection

The exception handler automatically detects user language:

### Urdu Detection
**Checks for:**
- Urdu script characters: ا ب پ ت ث ج چ ح خ د ڈ ذ ر ڑ ز ژ س ش ص ض ط ظ ع غ ف ق ک گ ل م ن ں ی ہ و ؤ ء ئ
- Common Roman Urdu words: kar, karo, hai, ho, ki, ka, ke, bhai

### English Detection
- Default language if none of the above are detected

---

## Exception Handler Implementation

```python
except Exception as e:
    # Detect user language from recent messages
    user_language = "en"  # Default
    if history:
        last_user_msg = next(...)
        # Check for Urdu script
        if any(char in last_user_msg for char in "ابپتثجچحخدڈ..."):
            user_language = "urdu"
        # Check for Roman Urdu words
        elif any(word in last_user_msg.lower() for word in ["kar", "karo", ...]):
            user_language = "urdu"

    # Friendly error based on language
    if user_language == "urdu":
        assistant_response = "Sorry bhai, server thoda busy hai 😅 ..."
    else:
        assistant_response = "Oops! Something went wrong 😅 ..."
```

---

## Error Message Templates

### English Template
```
[Friendly exclamation] [What went wrong] [How to fix] [Emoji]
[Next action suggestion 1] | [Next action suggestion 2]
```

**Example:**
```
"Hmm, couldn't find that task. Please check the number on the card (like #5) 🔍
Show all tasks? | Try again?"
```

### Roman Urdu Template
```
[Friendly greeting] [Kya galat hua] [Kaise fix kare] [Emoji]
[Next action 1]? | [Next action 2]?
```

**Example:**
```
"Yeh task nahi mila bhai. Card pe # wali number check karo 🔍
Sab tasks dikhao? | Doobara try kar?"
```

---

## Emoji Guide for Errors

| Emoji | Usage |
|-------|-------|
| 🔍 | Task not found, clarification needed |
| 😅 | Oops/mistake moment, friendly error |
| 📅 | Date-related issues |
| 🔴🟡🟢 | Priority options |
| 🔄 | Retry/try again |
| 📡 | Connection/network issues |
| 💪 | Motivation/encouragement |
| 📋 | Task management/scope |
| 💼 | Out of scope / different topic |

---

## Testing Error Scenarios

### Test Cases

```
1. Task Not Found
   User: "delete task 999"
   Expected: "Hmm, couldn't find that task... 🔍"

2. Missing Task ID
   User: "delete the grocery task"
   Expected: "Which task? (Tell me the ID...) 🔍"

3. Invalid Title
   User: "add task" → [blank response]
   Expected: "Title thoda empty hai... 😅"

4. Invalid Date
   User: "task 3 due 03/15/2026"
   Expected: "Hmm, date format seems off... 📅"

5. Invalid Priority
   User: "task 5 priority urgent"
   Expected: "Priority must be high/medium/low! 🔴🟡🟢"

6. Server Error
   [Groq timeout]
   Expected: "Sorry, server is busy... 😅"

7. Network Error
   [Connection timeout]
   Expected: "Connection seems off... 📡"

8. Out of Scope
   User: "What's the weather?"
   Expected: "I'm just a task helper! 📋"
```

---

## Future Enhancements

1. **Error Logging:** Track which errors occur most frequently
2. **A/B Testing:** Test different friendly messages for conversion
3. **Contextual Help:** Link to help articles for specific errors
4. **Error Recovery:** Suggest alternative actions (e.g., "show tasks" when delete fails)
5. **User Feedback:** "Was this helpful?" button after errors
6. **Retry Logic:** Automatic retry for transient errors
7. **Voice Errors:** Audio feedback for error messages
8. **Error Analytics:** Dashboard of error trends

---

## References

- **System Prompt:** `backend/app/services/chat_service.py` (ERROR HANDLING section)
- **Exception Handler:** `backend/app/services/chat_service.py` (lines 562-578)
- **Related:** Friendly confirmations guide, Quick replies guide

---

## Summary

The error handling system transforms frustrating technical errors into warm, helpful conversations. Users get:
- Clear explanation of what went wrong
- Guidance on how to fix it
- Next action suggestions
- Language-appropriate responses
- Emoji for visual warmth

This keeps users engaged and reduces frustration even when errors occur.
