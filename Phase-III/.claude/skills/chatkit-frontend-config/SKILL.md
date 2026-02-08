# ChatKit Frontend Config

## Purpose
Configure and integrate OpenAI ChatKit UI library into the existing Next.js application as a floating bottom-right widget, with authentication-based visibility and seamless embedding into the current app structure.

## Key Principles
- **Non-Invasive Integration**: Embed ChatKit without modifying existing app routes or pages
- **Floating Widget**: Bottom-right positioned widget that doesn't interfere with page content
- **Auth-Gated**: Only visible to authenticated users; hidden for anonymous visitors
- **Seamless UX**: Matches existing design system and color scheme
- **Client-Side Rendering**: ChatKit component loads on client to access JWT tokens
- **Lazy Loading**: Initialize ChatKit only when needed to reduce bundle size

## Core Responsibilities

### 1. ChatKit Library Setup
- Install OpenAI ChatKit package: `npm install @openai/chatkit` (or equivalent)
- Import ChatKit components and styles
- Configure API endpoint and authentication
- Set up ChatKit API key (from environment variables)

### 2. Create ChatKit Wrapper Component
Design a `ChatWidget.tsx` component that:
- Wraps ChatKit with authentication logic
- Manages widget visibility based on auth state
- Handles JWT token passing to ChatKit
- Provides user context (user_id, email) to ChatKit
- Manages widget state (open/closed)

```typescript
// components/ChatWidget.tsx
'use client';

import { useSession } from '@/hooks/useSession';
import ChatKit from '@openai/chatkit';
import { useEffect, useState } from 'react';

export function ChatWidget() {
  const { session, isLoading } = useSession();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Only show for authenticated users
  if (isLoading || !mounted) return null;
  if (!session) return null;

  return (
    <div id="chatkit-widget">
      <ChatKit
        apiKey={process.env.NEXT_PUBLIC_CHATKIT_API_KEY}
        userId={session.user.id}
        userEmail={session.user.email}
        userToken={session.token}
        theme="light"
        position="bottom-right"
        onClose={() => {
          // Optional: Track widget close event
        }}
        onMessage={(message) => {
          // Optional: Handle incoming messages
        }}
      />
    </div>
  );
}
```

### 3. Integrate into Root Layout
Add ChatKit to the main app layout (not individual pages):
- Modify `app/layout.tsx` or locale-based layout wrapper
- Import ChatWidget as Client Component
- Place widget outside main content area
- Ensure widget loads after authentication check

```typescript
// app/[locale]/layout.tsx
import { ChatWidget } from '@/components/ChatWidget';

export default async function LocaleLayout({
  children,
  params: { locale },
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  return (
    <html lang={locale}>
      <body>
        <MainNav />
        {children}
        <ChatWidget /> {/* Floating widget on all pages */}
      </body>
    </html>
  );
}
```

### 4. Authentication Context
- Use existing session hook to check auth status
- Extract JWT token from session/cookie
- Pass token to ChatKit for API requests
- ChatKit SDK handles token refresh (or pass refresh logic)

```typescript
// hooks/useSession.ts
export function useSession() {
  const [session, setSession] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch session from auth endpoint
    fetch('/api/auth/session')
      .then(res => res.json())
      .then(data => {
        setSession(data);
        setIsLoading(false);
      });
  }, []);

  return { session, isLoading };
}
```

### 5. ChatKit Configuration

#### Environment Variables
```env
# .env.local or .env.production
NEXT_PUBLIC_CHATKIT_API_KEY=<your-chatkit-api-key>
NEXT_PUBLIC_CHATBOT_ENDPOINT=http://localhost:8000/api/v1/chat
```

#### ChatKit Props
```typescript
interface ChatKitProps {
  apiKey: string;                // ChatKit SDK API key
  userId: string;                // Authenticated user ID
  userEmail: string;             // User email for context
  userToken: string;             // JWT token for API calls
  conversationId?: string;       // Resume existing conversation
  theme?: 'light' | 'dark';     // UI theme
  position?: 'bottom-right' | 'bottom-left' | 'top-right'; // Widget placement
  onClose?: () => void;          // Callback on widget close
  onMessage?: (msg: Message) => void; // Callback on new message
  header?: {
    title: string;
    subtitle?: string;
    avatar?: string;
  };
}
```

### 6. Styling & Positioning

#### CSS for Bottom-Right Placement
```css
/* styles/chatkit.css */
#chatkit-widget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  font-family: inherit;
}

#chatkit-widget iframe {
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

#### Tailwind Integration (Alternative)
```typescript
// If using Tailwind classes
<div className="fixed bottom-5 right-5 z-[9999]">
  <ChatKit {...props} />
</div>
```

### 7. Message Flow Integration

ChatKit communicates with your backend endpoint:

**Request Flow:**
1. User types message in ChatKit UI
2. ChatKit sends to `NEXT_PUBLIC_CHATBOT_ENDPOINT`
3. Backend receives with JWT token in header
4. Backend runs agent, stores in DB, returns response
5. ChatKit updates UI with response

**Headers Sent by ChatKit:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
X-User-Id: <user-id>
X-Conversation-Id: <conversation-id>
```

### 8. Conversation Persistence

#### Resume Conversations
```typescript
useEffect(() => {
  // Fetch user's last conversation on mount
  const getLastConversation = async () => {
    const res = await fetch('/api/v1/conversations?limit=1');
    const data = await res.json();
    setConversationId(data.conversations[0]?.id);
  };

  getLastConversation();
}, []);

return (
  <ChatKit
    conversationId={conversationId}
    {...otherProps}
  />
);
```

#### Store Conversation ID
```typescript
const handleNewConversation = (conversationId: string) => {
  localStorage.setItem('activeConversationId', conversationId);
};
```

### 9. Error Handling & Fallbacks

#### Handle Auth Errors
```typescript
if (error?.status === 401) {
  // Token expired, redirect to login
  window.location.href = '/auth/login';
}
```

#### Handle Network Errors
```typescript
const handleError = (error: Error) => {
  console.error('ChatKit error:', error);
  // Show user-friendly message
  showNotification('Chat temporarily unavailable');
};
```

### 10. Accessibility & Mobile

#### Mobile Responsiveness
```css
@media (max-width: 640px) {
  #chatkit-widget {
    bottom: 10px;
    right: 10px;
    width: calc(100vw - 20px);
  }
}
```

#### Keyboard Navigation
- Ensure ChatKit respects tab order
- Implement focus traps within widget
- Provide escape key to close widget

### 11. Performance Optimizations

#### Lazy Load ChatKit
```typescript
const ChatWidget = dynamic(
  () => import('@/components/ChatKit'),
  {
    loading: () => null, // Don't show anything while loading
    ssr: false, // Client-side only
  }
);
```

#### Code Splitting
```typescript
// Only load ChatKit on pages where user is authenticated
if (session) {
  const ChatKit = await import('@openai/chatkit');
  // Use ChatKit
}
```

### 12. Testing & Validation

#### Unit Tests
```typescript
// components/__tests__/ChatWidget.test.tsx
import { render, screen } from '@testing-library/react';
import { ChatWidget } from '@/components/ChatWidget';

describe('ChatWidget', () => {
  it('renders for authenticated users', () => {
    // Mock session
    // Expect widget to render
  });

  it('hides for unauthenticated users', () => {
    // Mock no session
    // Expect widget not to render
  });

  it('passes correct props to ChatKit', () => {
    // Verify userId, userToken, etc. passed correctly
  });
});
```

#### Integration Tests
- Test ChatKit loads after login
- Test ChatKit hidden after logout
- Test message sending and response
- Test conversation resumption

## Success Criteria
✅ ChatKit library installed and configured
✅ ChatWidget component renders only for authenticated users
✅ Widget positioned at bottom-right corner
✅ Widget doesn't interfere with existing app content
✅ Authentication context passed to ChatKit (user_id, token)
✅ Messages sent to backend API endpoint
✅ Conversation history loaded and resumed
✅ Error handling for auth failures (401, 403)
✅ Mobile responsive on all screen sizes
✅ Lazy loading reduces initial bundle size
✅ Accessibility features implemented (keyboard nav, focus management)
✅ No modifications to existing pages or routes

## Related Components
- **Next.js Frontend**: Host application
- **FastAPI Backend**: Chat endpoint (`/api/v1/conversations/{id}/messages`)
- **JWT Auth**: Session management and token passing
- **Neon Database**: Message persistence
- **OpenAI ChatKit SDK**: UI library

## Configuration Checklist
- [ ] ChatKit SDK installed
- [ ] API key configured in `.env.local`
- [ ] Chatbot endpoint configured
- [ ] ChatWidget component created
- [ ] Integrated into root layout
- [ ] Authentication check implemented
- [ ] Floating position CSS applied
- [ ] Mobile responsiveness tested
- [ ] Error handling for auth failures
- [ ] Conversation resumption logic added
- [ ] Lazy loading configured
- [ ] Accessibility tested (keyboard, screen readers)

## Environment Variables
```env
NEXT_PUBLIC_CHATKIT_API_KEY=sk_...
NEXT_PUBLIC_CHATBOT_ENDPOINT=https://api.example.com/api/v1
```

## Browser Support
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Known Limitations
- ChatKit requires modern browser with ES2020+ support
- WebSocket connections may require CORS configuration
- Token refresh must be handled by client or ChatKit SDK
- File uploads may need additional configuration

## Migration Path
If replacing existing chat UI:
1. Deploy ChatKit alongside old UI
2. Gradually migrate users to ChatKit
3. Monitor performance and user feedback
4. Deprecate old UI after validation
5. Remove old chat code

## Support & Resources
- ChatKit Documentation: https://github.com/openai/chatkit
- API Reference: `/api/v1/conversations`
- Authentication Docs: See auth-security skill
- Troubleshooting: Check browser console, network tab, auth logs
