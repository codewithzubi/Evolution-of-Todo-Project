---
id: 008
title: Improve error handling to be friendly and helpful
stage: misc
date: 2026-02-12
surface: agent
model: claude-haiku-4-5-20251001
feature: 001-todo-ai-chatbot
branch: 001-todo-ai-chatbot
user: user
command: Improve error handling in chatbot to be more friendly and helpful
labels: ["error-handling", "ux", "multilingual", "friendly-messages", "user-guidance"]
links:
  spec: specs/001-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/app/services/chat_service.py
tests:
 - Manual: Invalid task ID → see friendly message with guidance
 - Manual: Missing task ID → helpful prompt showing ID format
 - Manual: Empty task title → encouraging message to provide title
 - Manual: Invalid date format → example of correct format shown
 - Manual: Invalid priority → options listed (high/medium/low)
 - Manual: Server error → friendly retry suggestion
 - Manual: Network error → connection troubleshooting message
 - Manual: Out-of-scope request → list of available commands
 - Manual: Roman Urdu user + error → response in Roman Urdu
 - Manual: Error message includes next action suggestion
---

## Prompt

Improve error handling in chatbot to be more friendly and helpful.

Current: Errors show technical message like "I apologize, but I encountered an error..."

Fix:
- Make errors friendly: "Sorry bhai, kuch galat ho gaya — please try again ya mujhe batao kya issue hai 😊"
- For specific errors:
  - No task found → "Task nahi mila bhai, please sahi ID check karo (card pe # wali number) 🔍"
  - Invalid input → "Title ya description galat hai bhai, please thoda clear batao 😅"
  - Quota/API error → "Thodi der mein try karo bhai, server busy hai 😅"
- Always suggest next action (e.g. "Ek naya task add karna chahte ho?")
- Keep responses in Urdu/Roman Urdu if user uses it

## Response snapshot

Completely rewrote error handling in system prompt with:

**Comprehensive ERROR HANDLING Section:**
9 specific error scenarios with multilingual responses:

1. **Task Not Found (invalid task_id)**
   - English: "Hmm, couldn't find that task. Please check the number on the card (like #5) 🔍"
   - Roman Urdu: "Yeh task nahi mila bhai. Card pe # wali number check karo 🔍"
   - Next action: "Show all tasks? | Try again?"

2. **Missing Task ID**
   - English: "Which task? (Tell me the ID number like 5 or 'task 3') 🔍"
   - Roman Urdu: "Konsa task bhai? ID batao (number like 5 ya 'task 3') 🔍"
   - Hint: Look for # on task card

3. **Invalid Task Title/Input**
   - English: "Title thoda empty hai. Tell me what you want to do! 😅"
   - Roman Urdu: "Title khali hai bhai. Kya karna chahte ho batao! 😅"

4. **Invalid Date Format**
   - English: "Hmm, date format seems off. Try DD-MM-YYYY or say 'tomorrow'/'next week' 📅"
   - Roman Urdu: "Date galat hai bhai. DD-MM-YYYY format mein likho ya '5 din baad' bol 📅"
   - Guidance: Shows example format

5. **Invalid Priority**
   - English: "Priority must be high, medium, or low! 🔴🟡🟢"
   - Roman Urdu: "Priority high, medium ya low ho sakta hai! 🔴🟡🟢"
   - Options listed visually with emoji

6. **API/Server Error**
   - English: "Sorry, server is a bit busy. Try again in a moment! 😅"
   - Roman Urdu: "Sorry bhai, server thoda busy hai. Aadhi der mein try kar! 😅"
   - Next action: "Try again? | Show tasks?"

7. **Network/Connection Error**
   - English: "Connection seems off. Check your internet and try again! 📡"
   - Roman Urdu: "Internet slow hai lagta hai bhai. Doobara try kar! 📡"
   - Suggests checking internet

8. **No Pending/Completed Tasks**
   - English: "No pending tasks here! Great job! 🎉 All caught up?"
   - Roman Urdu: "Koi pending task nahi! Shukriya! 🎉 Sab ho gaya?"
   - Positive reinforcement

9. **Out-of-scope Request**
   - English: "I'm just a task helper! I can: add tasks, delete them, mark complete, set priority, due dates 📋"
   - Roman Urdu: "Bhai main sirf task helper hoon! Add, delete, complete kar sakta hoon 📋"
   - List of available commands

**General Error Rules:**
- NEVER use technical terms (try/catch, exception, stack trace)
- ALWAYS explain in simple language what went wrong
- ALWAYS suggest next action to keep momentum
- Use EMOJIS to soften error message
- Keep SHORT (1-2 sentences max)
- Match user's language (English/Roman Urdu/Urdu)
- Be APOLOGETIC but HELPFUL ("Sorry bhai..." / "Oops...")
- ENCOURAGE retrying if appropriate

**Enhanced Exception Handler:**
- Detects user language from conversation history
- Checks for Urdu script characters (ا ب پ ت ث etc.)
- Checks for common Roman Urdu words (kar, karo, hai, ho, bhai, etc.)
- Friendly English error: "Oops! Something went wrong 😅 Server's slow. Try again in a moment! Add a task or see all tasks? 🎉"
- Friendly Roman Urdu error: "Sorry bhai, server thoda busy hai 😅 Aadhi der mein try kar! Task add karna hai ya sab dekh lena hai? 🎉"

## Outcome

- ✅ Impact: Errors are no longer scary or confusing. Users get friendly guidance, clear next steps, and language-appropriate responses. This reduces frustration and keeps users engaged even when errors occur.
- 🧪 Tests: Code review PASS; manual testing PENDING across error scenarios
- 📁 Files: 1 file modified (backend/app/services/chat_service.py) with 145 lines added
- 🔁 Next prompts: Deploy to staging; test all error scenarios; gather feedback on message clarity and helpfulness
- 🧠 Reflection: System now handles errors like a real friend would — with empathy, clarity, and helpful suggestions. The comprehensive error guide ensures LLM generates appropriate responses for various failure scenarios. Language detection makes it accessible to all users. Next action suggestions keep conversation momentum.

## Evaluation notes (flywheel)

- Failure modes observed: None in prompt definition; potential LLM may not always follow all rules (test in staging)
- Graders run and results (PASS/FAIL): Code review PASS - error scenarios comprehensive; runtime validation PENDING
- Prompt variant (if applicable): null
- Next experiment: Monitor which error scenarios occur most frequently; A/B test different friendly messages; add error logging for debugging
