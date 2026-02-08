# ChatKit Widget - Quick Start Guide

## Overview

The ChatKit Widget is a floating AI chat interface integrated into your app. It's ready to use with zero configuration.

## How It Works

### 1. **Floating Button** (Bottom-Right)
- Click to open/close chat window
- Shows when user is authenticated
- Disabled when user is not logged in
- Respects dark mode preference

### 2. **Chat Window**
- Select or create conversations
- Send messages to AI
- View conversation history
- Delete conversations

### 3. **Conversations**
- Click "New Conversation" to start
- Messages are persisted on the backend
- Active conversation remembered across page reloads
- Up to 5 recent conversations shown

## For Users

### Open Chat
1. Click the chat bubble (💬) in bottom-right corner
2. Click "New Conversation" or select existing one
3. Type a message and press Enter (or click Send)
4. Wait for AI response
5. Click X to close window

### Manage Conversations
- Click on conversation name to switch
- Click Delete button to remove conversation
- Confirm deletion when prompted

### Error Handling
- If connection fails: Click Retry or wait 5 seconds
- If session expires: Sign in again and retry
- Most errors auto-clear after 5 seconds

## For Developers

### Basic Usage

```tsx
// Already integrated in app/layout.tsx
// No additional setup required!
<ChatWidgetWrapper />
```

### Using useChat Hook

```tsx
'use client';

import { useChat } from '@/hooks/useChat';

export function MyComponent() {
  const {
    conversations,
    activeConversationId,
    messages,
    isLoading,
    error,
    createConversation,
    selectConversation,
    sendMessage,
    deleteConversation
  } = useChat();

  // Use the hook for your own chat UI
  return (
    <div>
      {/* Your custom chat UI */}
    </div>
  );
}
```

### Using Chat API Service

```tsx
import { chatApiService } from '@/services/chatApiService';

// Create conversation
const conv = await chatApiService.createConversation('My Chat');

// Send message
const response = await chatApiService.sendMessage(
  'conv-123',
  'Hello AI!'
);

// Get history
const history = await chatApiService.getMessageHistory(
  'conv-123',
  20, // limit
  0   // offset
);

// Delete
await chatApiService.deleteConversation('conv-123');
```

### Type Definitions

```tsx
import type {
  Conversation,
  Message,
  ChatState
} from '@/types/chat';

// Fully typed API responses
const conv: Conversation = {...};
const msg: Message = {...};
```

## API Reference

### useChat Hook

**Methods:**
- `createConversation(title?: string)` - Create new conversation
- `selectConversation(id: string)` - Switch to conversation
- `sendMessage(content: string)` - Send and get response
- `deleteConversation(id: string)` - Remove conversation
- `refetchConversations()` - Reload list
- `loadMessages(limit?: number)` - Load message history
- `deleteMessage(id: string)` - Remove message
- `clearError()` - Dismiss error

**State:**
- `conversations: Conversation[]` - All conversations
- `activeConversationId: string | null` - Current conversation
- `messages: Message[]` - Messages in current conversation
- `isLoading: boolean` - API call in progress
- `error: string | null` - Error message
- `isDarkMode: boolean` - Dark mode enabled

### Chat API Service

**Endpoints:**
- `createConversation(title?: string)` - POST /conversations
- `listConversations(limit, offset)` - GET /conversations
- `getConversation(id)` - GET /conversations/{id}
- `sendMessage(id, content, metadata?)` - POST /conversations/{id}/messages
- `getMessageHistory(id, limit, offset)` - GET /conversations/{id}/messages
- `deleteConversation(id)` - DELETE /conversations/{id}
- `deleteMessage(convId, msgId)` - DELETE /conversations/{id}/messages/{id}

## Customization

### Change Button Icon
Edit `frontend/src/components/chat/ChatWidget.tsx`:
```tsx
<button>
  <span className="text-2xl">🤖</span>  {/* Change emoji here */}
</button>
```

### Change Button Position
Edit styles in `ChatWidget.tsx`:
```tsx
<div className="fixed bottom-6 right-6 z-50">  {/* Adjust bottom/right */}
```

### Change Button Size
Edit size classes:
```tsx
<button className="w-16 h-16 rounded-full">  {/* Change to w-20 h-20 etc */}
```

### Disable Dark Mode
In `useChat.ts`, set:
```tsx
isDarkMode: false  // instead of detecting system preference
```

## Translation Keys

Add new keys to `frontend/src/i18n/locales/[lang].json`:

```json
{
  "chat": {
    "button": { "title": "Chat with AI" },
    "input": { "placeholder": "Type..." },
    "errors": { "networkError": "Connection failed" }
  }
}
```

Currently supported:
- ✅ English (en)
- ✅ Urdu (ur)
- ✅ Roman Urdu (ur-roman)

## Troubleshooting

### Widget Not Showing
- User is not authenticated? → Sign in first
- Z-index conflict? → Check z-50 in other components

### Chat Not Opening
- Check browser console for errors
- Verify JWT token exists in localStorage
- Check backend is running

### Messages Not Sending
- Is user authenticated? → Check auth cookie/token
- Network connection? → Check browser network tab
- Backend errors? → Check server logs

### Performance Issues
- Messages loading slowly? → Check pagination (default 20)
- Conversation list laggy? → Limit to 5 conversations
- Widget memory leak? → Check cleanup in useChat

## File Structure

```
frontend/
├── src/
│   ├── components/chat/
│   │   ├── ChatWidget.tsx           # Entry point
│   │   ├── ChatWindow.tsx           # Modal
│   │   ├── MessageList.tsx          # Messages
│   │   ├── ChatInput.tsx            # Input
│   │   ├── ConversationList.tsx     # Dropdown
│   │   ├── ErrorMessage.tsx         # Errors
│   │   ├── index.ts                 # Exports
│   │   └── README.md                # Full docs
│   ├── hooks/
│   │   └── useChat.ts               # State management
│   ├── services/
│   │   └── chatApiService.ts        # API wrapper
│   └── types/
│       └── chat.ts                  # TypeScript types
└── tests/unit/chat/
    ├── useChat.test.ts              # Hook tests
    └── chatApiService.test.ts       # Service tests
```

## Next Steps

1. **Test the Widget**
   - Run: `npm run dev`
   - Open app in browser
   - Click chat button
   - Create and send message

2. **Customize**
   - Change button icon/position
   - Add custom styles
   - Modify translations

3. **Integrate with Your Flow**
   - Use `useChat()` in custom components
   - Call `chatApiService` directly
   - Add more conversation types

4. **Deploy**
   - Build: `npm run build`
   - Test: `npm run test`
   - Deploy: `npm start`

## Getting Help

- **Component API**: See `frontend/src/components/chat/README.md`
- **Hook Usage**: Check `frontend/src/hooks/useChat.ts`
- **Type Definitions**: View `frontend/src/types/chat.ts`
- **Examples**: See `frontend/src/components/chat/ChatWidget.tsx`

## Performance Tips

1. **Message Pagination**
   - Load 20 messages per request
   - Use "Load earlier messages" button
   - Avoid loading entire conversation history

2. **Conversation List**
   - Shows 5 most recent only
   - Reduces dropdown clutter
   - Faster selection

3. **Code Splitting**
   - Widget is lazy-loaded
   - Only loads when needed
   - Minimal bundle impact

4. **Dark Mode**
   - Uses CSS-only detection
   - No JavaScript overhead
   - Respects system preference

---

**Version**: 1.0  
**Updated**: 2026-02-07  
**Status**: Production Ready
