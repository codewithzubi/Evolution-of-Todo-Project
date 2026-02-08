# ChatWidget Component Documentation

## Overview

The ChatWidget is a production-ready floating chat interface that integrates with the Phase-III AI Chatbot backend. It provides a modern, accessible chat experience with full support for multi-language internationalization, dark mode, and responsive design.

## Features

- **Floating Button**: Fixed bottom-right corner button that opens/closes the chat interface
- **Conversation Management**: Create, switch, and delete conversations
- **Message History**: View and send messages within conversations
- **Authentication**: Integrates with existing Phase-II JWT authentication
- **Error Handling**: Comprehensive error messages with retry capabilities
- **Accessibility**: WCAG AA compliant with full keyboard navigation
- **Responsive Design**: Mobile, tablet, and desktop optimized
- **Dark Mode**: Respects system color scheme preference
- **Internationalization**: Supports English, Urdu, and Roman Urdu

## Components

### ChatWidget
Main entry point component that manages the floating button and window state.

```tsx
import { ChatWidget } from '@/components/chat';

// In your root layout
<ChatWidget />
```

### ChatWindow
The main chat interface containing the conversation list, message display, and input.

**Props:**
- `isOpen: boolean` - Whether the chat window is visible
- `conversations: Conversation[]` - List of user conversations
- `activeConversationId: string | null` - Currently selected conversation
- `messages: Message[]` - Messages in active conversation
- `isLoading: boolean` - API call in progress
- `error: string | null` - Error message to display
- `isDarkMode: boolean` - Dark mode enabled
- `onClose: () => void` - Close window callback
- `onSelectConversation: (id: string) => void` - Select conversation
- `onCreateConversation: () => void` - Create new conversation
- `onSendMessage: (message: string) => Promise<void>` - Send message
- `onDeleteConversation: (id: string) => void` - Delete conversation
- `onClearError: () => void` - Clear error message

### ChatInput
Text input field with send button.

**Props:**
- `onSendMessage: (message: string) => Promise<void>` - Called when message is sent
- `isLoading: boolean` - Disable input while loading
- `isDarkMode: boolean` - Dark mode styling
- `disabled: boolean` - Disable input
- `placeholder: string` - Input placeholder text

### MessageList
Displays chat messages in chronological order.

**Props:**
- `messages: Message[]` - Messages to display
- `isDarkMode: boolean` - Dark mode styling
- `onLoadMore: () => void` - Load earlier messages
- `hasMore: boolean` - More messages available
- `isLoadingMore: boolean` - Loading earlier messages

### ConversationList
Dropdown list of recent conversations.

**Props:**
- `conversations: Conversation[]` - List of conversations
- `activeConversationId: string | null` - Selected conversation
- `onSelectConversation: (id: string) => void` - Select conversation
- `onCreateNew: () => void` - Create new conversation
- `onDeleteConversation: (id: string) => void` - Delete conversation
- `isDarkMode: boolean` - Dark mode styling
- `isOpen: boolean` - Dropdown open state
- `onToggle: () => void` - Toggle dropdown

### ErrorMessage
Error display with optional retry button.

**Props:**
- `error: string` - Error message
- `isDarkMode: boolean` - Dark mode styling
- `onRetry: () => void` - Retry callback
- `onDismiss: () => void` - Dismiss error

## Hooks

### useChat
Main state management hook for chat functionality.

```tsx
const {
  conversations,           // Conversation[]
  activeConversationId,   // string | null
  messages,               // Message[]
  isLoading,              // boolean
  error,                  // string | null
  isDarkMode,             // boolean
  createConversation,     // (title?: string) => Promise<Conversation>
  selectConversation,     // (id: string) => Promise<void>
  loadMessages,           // (limit?: number) => Promise<void>
  sendMessage,            // (content: string) => Promise<Message>
  deleteConversation,     // (id: string) => Promise<void>
  deleteMessage,          // (id: string) => Promise<void>
  refetchConversations,   // (limit?: number) => Promise<void>
  clearError,             // () => void
  setError                // (error: string | null) => void
} = useChat({
  autoLoadConversations: true,
  autoLoadMessages: true,
  storageKey: 'evolution_active_conversation_id'
});
```

**Options:**
- `autoLoadConversations: boolean` - Auto-load conversations on mount
- `autoLoadMessages: boolean` - Auto-load messages when conversation changes
- `storageKey: string` - localStorage key for persisting active conversation

## Services

### chatApiService
Wrapper around FastAPI chat endpoints with JWT authentication.

```tsx
import { chatApiService } from '@/services/chatApiService';

// Create conversation
await chatApiService.createConversation('My Chat');

// List conversations
const response = await chatApiService.listConversations(20, 0);

// Send message
const aiResponse = await chatApiService.sendMessage(conversationId, 'Hello');

// Get message history
const history = await chatApiService.getMessageHistory(conversationId, 20, 0);

// Delete conversation
await chatApiService.deleteConversation(conversationId);

// Delete message
await chatApiService.deleteMessage(conversationId, messageId);
```

## Types

All TypeScript types are defined in `@/types/chat`:

```tsx
import type {
  Conversation,           // Conversation metadata
  Message,               // Message with timestamp
  ChatState,             // Full chat state
  ChatError,             // Error information
  ChatRequest,           // API request
  ChatResponse,          // API response
  ConversationResponse,  // Conversation from API
  MessageResponse        // Message from API
} from '@/types/chat';
```

## Internationalization

Chat strings are translated in `frontend/src/i18n/locales/`:

- `en.json` - English
- `ur.json` - Urdu
- `ur-roman.json` - Roman Urdu

Keys are under `chat.*`:

```json
{
  "chat": {
    "button": {
      "title": "Chat with AI",
      "open": "Open chat",
      "close": "Close chat"
    },
    "input": {
      "placeholder": "Type your message...",
      "send": "Send"
    },
    "errors": {
      "networkError": "Connection failed...",
      "sessionExpired": "Session expired...",
      "signInRequired": "Please sign in to chat."
    }
  }
}
```

## Authentication Flow

1. **Check Authentication**: ChatWidget checks if user is authenticated via `useAuth()`
2. **Show Sign-In Prompt**: If not authenticated, displays disabled button with sign-in message
3. **JWT in Headers**: All API calls include `Authorization: Bearer {token}` header automatically
4. **Session Management**: If token expires, user is prompted to sign in again
5. **API Error Handling**: 401/403 errors trigger logout and sign-in redirect

## Error Handling

The widget handles these error scenarios:

| Error | Handling |
|-------|----------|
| Network Error | Show "Connection failed. Retry?" with auto-retry |
| 401 Unauthorized | Show "Session expired" + logout |
| 403 Forbidden | Show "Access denied" error |
| 404 Not Found | Show "Conversation not found" |
| 500 Server Error | Show "Server error" with retry |
| Timeout | Show "Request timed out" + retry |

All errors auto-clear after 5 seconds or on user action.

## Accessibility Features

- **ARIA Labels**: All interactive elements have proper aria-labels
- **Keyboard Navigation**: 
  - Tab through messages and buttons
  - Enter to send message
  - Escape to close chat
- **Focus Management**: Focus indicators visible on all interactive elements
- **Screen Reader Friendly**: Messages read naturally with proper roles
- **Color Contrast**: 7:1 contrast ratio (WCAG AAA)
- **Responsive Touch**: 44×44px minimum tap targets

## Performance Optimizations

- **Code Splitting**: ChatWidget is lazy-loaded via `next/dynamic`
- **Pagination**: Messages loaded in batches of 20
- **State Management**: Optimistic updates with rollback on error
- **No Polling**: Stateless architecture (can add SSE for v2)
- **localStorage**: Persists active conversation ID for quick reload

## Dark Mode

The widget respects system color scheme preference:

```tsx
const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
```

Styling automatically adjusts for light/dark modes using Tailwind utilities.

## Responsive Design

| Breakpoint | Behavior |
|-----------|----------|
| Mobile (<640px) | Full-screen modal, 100vw × 100vh |
| Tablet (640-768px) | 90vw width, 80vh height |
| Desktop (>768px) | Fixed 380px × 600px in bottom-right |

## Integration Example

```tsx
// In your root layout (already done)
import { ChatWidget } from '@/components/chat';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <Providers>
          <main>{children}</main>
          <ChatWidget />
        </Providers>
      </body>
    </html>
  );
}
```

## Testing

### Unit Tests
- `useChat.test.ts` - Hook state management and API calls
- `chatApiService.test.ts` - Service layer with JWT injection

### Integration Tests
- `ChatWidget.integration.test.tsx` - End-to-end widget flow

## Browser Support

- Chrome/Edge: 90+
- Firefox: 88+
- Safari: 14+
- Mobile browsers: 2 versions back

## Known Limitations

1. Message history limited to 100 messages per conversation
2. No real-time updates (stateless design)
3. No file uploads in v1
4. No message editing/deletion from UI in v1

## Future Enhancements

- [ ] Server-Sent Events (SSE) for real-time updates
- [ ] Message search and filtering
- [ ] Custom conversation titles
- [ ] Message reactions and pins
- [ ] AI model selection (GPT-4, etc.)
- [ ] Voice input/output
- [ ] Message persistence across devices

## Support

For issues or questions, refer to:
- Phase-III specification: `specs/004-ai-chatbot/spec.md`
- Backend documentation: `IMPLEMENTATION_SUMMARY_T328-T345.md`
- Architecture: `ARCHITECTURE_INDEX.md`
