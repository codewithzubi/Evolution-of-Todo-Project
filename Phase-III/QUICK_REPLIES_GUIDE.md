# Quick Replies Feature Guide

## Overview

Quick replies are contextual suggestion buttons that appear below chatbot responses. They allow users to quickly send common follow-up messages without typing, improving user experience and conversation flow.

---

## Components

### 1. QuickReplies Component
**File:** `frontend/components/chat/quick-replies.tsx`

A reusable component that renders quick reply buttons.

```typescript
interface QuickReply {
  label: string  // Display text on button
  value: string  // Message sent when clicked
}

<QuickReplies
  replies={[
    { label: "Add task", value: "add task" },
    { label: "Show tasks", value: "show my tasks" }
  ]}
  onReplyClick={(reply) => sendMessage(reply)}
  disabled={isLoading}
/>
```

### 2. MessageBubble Component
**File:** `frontend/components/chat/MessageBubble.tsx`

Enhanced with quick reply support.

```typescript
<MessageBubble
  content="Task added!"
  role="assistant"
  quickReplies={[...]}
  onQuickReplyClick={handleQuickReply}
  isWaitingForReply={isLoading}
/>
```

### 3. ChatWindow Component
**File:** `frontend/components/chat/ChatWindow.tsx`

Coordinates quick reply logic and message sending.

---

## Features

### Smart Contextual Suggestions

The `getQuickReplies()` function analyzes message content and suggests relevant quick replies:

#### 1. Task Added/Created
```
Triggers on: "add", "added", "created"
Suggests:
- "Add another task" → "add task"
- "Show my tasks" → "show tasks"
- "Kuch aur batao" → "kuch aur task add karna hai"
```

#### 2. Task Deleted/Removed
```
Triggers on: "delete", "removed"
Suggests:
- "Show remaining" → "show my tasks"
- "Add new task" → "add task"
- "Aur kuch?" → "aur task manage karna hai?"
```

#### 3. Task Completed
```
Triggers on: "complete", "done", "marked"
Suggests:
- "Complete more" → "show pending tasks"
- "Add new task" → "add task"
- "Sab tasks dikhao" → "show all tasks"
```

#### 4. Task Listing
```
Triggers on: "task", "pending", "completed"
Suggests:
- "Add new task" → "add task"
- "Show pending" → "show pending tasks"
- "Task add karo" → "naya task add karna hai"
```

#### 5. Default
```
When no specific pattern matches:
- "Add task" → "add task"
- "Show tasks" → "show my tasks"
- "Help" → "what can you help with?"
```

---

## Responsive Design

### Mobile (< 640px)
- Small buttons (text-xs, px-2, py-1)
- Flex wrap for multiple buttons
- Stacking behavior when space is limited
- Responsive font sizing

### Tablet (640px - 1024px)
- Medium buttons (text-sm, px-3, py-2)
- Horizontal layout
- Full button text without truncation

### Desktop (> 1024px)
- Full-sized buttons with proper spacing
- Horizontal layout
- Maximum width display

---

## Styling

### Button States

**Default:**
```css
border: 1px solid rgba(107, 114, 128, 0.5)
text-color: #d1d5db (gray-300)
background: transparent
```

**Hover:**
```css
border: 1px solid rgba(96, 165, 250, 0.5)
text-color: #93c5fd (blue-300)
background: rgba(31, 41, 55, 0.8)
transition: all 200ms
```

**Active:**
```css
transform: scale(95%)
transition: all 200ms
```

**Disabled (Loading):**
```css
opacity: 50%
cursor: not-allowed
border: same as default (no hover effect)
text-color: same as default
```

---

## Usage Examples

### Example 1: Task Added
```
User: "add task buy milk"
Bot: "Task 'Buy milk' added! 🎉 Add more? | Show all?"
     [Add another task] [Show my tasks] [Kuch aur batao]
```

### Example 2: Task Completed
```
User: "task 3 complete kar do"
Bot: "Task #3 done bhai! 🎉 Kuch aur add karna?"
     [Complete more] [Add new task] [Sab tasks dikhao]
```

### Example 3: Showing Tasks
```
User: "show all tasks"
Bot: "Yeh rahe teri tasks! 📋 [lists tasks]"
     [Add new task] [Show pending] [Task add karo]
```

### Example 4: Loading State
```
User: [clicks quick reply]
Bot: "Thinking..." (buttons disabled, opacity 50%)
     [Add another task] [Show my tasks] [Kuch aur batao] (disabled)
```

---

## Implementation Details

### Message Flow

1. User sends message via input or quick reply
2. Message appears in chat (user bubble)
3. Bot processes message (shows "Thinking...")
4. Bot response appears (assistant bubble)
5. `getQuickReplies()` analyzes response content
6. Quick reply buttons appear below response
7. User can click button or type new message

### Code Flow

```typescript
// ChatWindow.tsx
const getQuickReplies = (messageContent: string): QuickReply[] => {
  // Analyze content and return appropriate suggestions
}

const handleQuickReply = (reply: string) => {
  // Send quick reply as message
  sendMessage(reply)
}

// MessageBubble rendering
{messages.map((message) => (
  <MessageBubble
    // ... other props
    quickReplies={message.role === "assistant" ? getQuickReplies(message.content) : undefined}
    onQuickReplyClick={handleQuickReply}
    isWaitingForReply={isLoading}
  />
))}
```

---

## Adding New Quick Reply Patterns

To add new contextual patterns, modify `getQuickReplies()`:

```typescript
// Add new pattern
if (content.includes("priority") || content.includes("set priority")) {
  return [
    { label: "Set high priority", value: "make it high priority" },
    { label: "View by priority", value: "show tasks by priority" },
    { label: "Priority check", value: "kya priority important hai?" }
  ]
}
```

### Best Practices
- Use lowercase for comparison: `messageContent.toLowerCase()`
- Keep labels short (2-3 words)
- Use both English and Roman Urdu labels
- Ensure values are complete, actionable messages
- Test with various bot responses

---

## Customization

### Change Button Styling

Edit the className in QuickReplies component:

```typescript
className={cn(
  "text-xs sm:text-sm px-2 sm:px-3 py-1 sm:py-2",
  "border border-gray-500/50 hover:border-purple-400/50",  // Change colors
  "text-gray-300 hover:text-purple-300",
  "hover:bg-gray-800/80 transition-all duration-200",
  // ... more classes
)}
```

### Change Button Variant

```typescript
<Button
  variant="outline"  // Could be "default", "ghost", "outline", etc.
  size="sm"          // Could be "sm", "md", "lg"
  // ...
/>
```

### Change Quick Reply Patterns

Modify `getQuickReplies()` function in ChatWindow to return different suggestions based on message content.

---

## Accessibility

- ✅ Buttons are keyboard navigable (Tab, Enter)
- ✅ Proper disabled state during loading
- ✅ Clear visual feedback (hover, active states)
- ✅ Adequate color contrast (gray-300 text on dark background)
- ✅ Aria labels supported via Button component

---

## Testing Checklist

- [ ] Click quick reply → message sent
- [ ] Quick reply appears below assistant message
- [ ] No quick replies below user messages
- [ ] Quick replies disabled during loading
- [ ] Responsive buttons on mobile (stacked)
- [ ] Responsive buttons on desktop (horizontal)
- [ ] English buttons show for English messages
- [ ] Roman Urdu buttons show for Urdu messages
- [ ] Hover effect works
- [ ] Active/click effect (scale) works
- [ ] Different patterns show different buttons
- [ ] Default buttons show when no pattern matches
- [ ] Keyboard navigation works (Tab, Enter)
- [ ] Tooltip/title shows on hover

---

## Performance

- ✅ QuickReplies component is lightweight
- ✅ `getQuickReplies()` uses simple string matching
- ✅ No API calls or expensive operations
- ✅ Renders only for assistant messages
- ✅ Minimal re-renders (only when messages change)

---

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari 14+, Chrome Android)

---

## Related Documentation

- **ChatWindow:** `frontend/components/chat/ChatWindow.tsx`
- **MessageBubble:** `frontend/components/chat/MessageBubble.tsx`
- **QuickReplies:** `frontend/components/chat/quick-replies.tsx`
- **UI Button:** `@/components/ui/button` (shadcn/ui)

---

## Future Enhancements

1. **Machine Learning Suggestions:** Use ML to predict best next actions
2. **User Preferences:** Learn which quick replies user prefers
3. **Emoji Quick Replies:** Visual quick replies with icons
4. **Conditional Replies:** Show different replies based on task status
5. **Analytics:** Track which quick replies are most used
6. **A/B Testing:** Test different wording/options
7. **Custom Suggestions:** Let users customize quick replies
8. **Voice Quick Replies:** Audio options for accessibility

---

## Summary

Quick replies transform the chatbot from a passive responder to an active guide. Users can navigate the interface with single clicks, reducing friction and improving satisfaction. The contextual nature of suggestions makes each interaction feel personalized and helpful.

**Benefits:**
- ✅ Reduces typing effort
- ✅ Guides users to next action
- ✅ Improves conversation flow
- ✅ Increases engagement
- ✅ Accessible and responsive
- ✅ Multilingual support
