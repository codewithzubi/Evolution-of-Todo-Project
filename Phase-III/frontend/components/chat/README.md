# Floating Chat UI - Phase III

Complete floating chatbot UI with minimize, responsive design, and Zustand state management.

## Components

### 1. **ChatBubble.tsx**
Floating button in the bottom-right corner
- Lucide MessageSquare icon
- Hover scale and glow effects
- Click to open/close chat
- Auto-changes to X icon when open
- Fixed position on screen

### 2. **ChatWindow.tsx**
Main chat interface panel
- Slide-in from right (~400px width, 600px max height)
- Dark theme (gray-900 background)
- Top bar with title and controls
- Minimize/Close buttons
- Auto-scroll to latest message
- Input textarea with Shift+Enter for new line
- Send button
- Loading spinner
- Mobile responsive (full-width on small screens)

### 3. **MessageBubble.tsx**
Individual message component
- User messages: right-aligned, blue background
- Assistant messages: left-aligned, gray background
- Optional timestamp display
- Text wrapping support

### 4. **FloatingChat.tsx**
Wrapper component combining button + window
- Export this component to use the entire floating chat UI

### 5. **chat-store.ts** (Zustand)
Global state management
- `isOpen`: Chat window visibility
- `isMinimized`: Minimize state
- Methods: `toggleOpen()`, `toggleMinimize()`, `open()`, `close()`

## Installation

### 1. Install Zustand
```bash
npm install zustand
# or
yarn add zustand
# or
pnpm add zustand
```

### 2. Verify Dependencies
The following are already in package.json:
- lucide-react (icons)
- tailwindcss (styling)
- @radix-ui components
- sonner (notifications)

## Usage

### Add FloatingChat to your layout/page:

```typescript
// app/layout.tsx or app/dashboard/layout.tsx
import { FloatingChat } from "@/components/chat/FloatingChat"

export default function Layout({ children }) {
  return (
    <html>
      <body>
        {children}
        <FloatingChat />
      </body>
    </html>
  )
}
```

### Or use individual components:

```typescript
import { ChatBubble } from "@/components/chat/ChatBubble"
import { ChatWindow } from "@/components/chat/ChatWindow"

export function MyPage() {
  return (
    <>
      {/* ... your page content ... */}
      <ChatBubble />
      <ChatWindow />
    </>
  )
}
```

### Use Zustand store in your own components:

```typescript
import { useChatStore } from "@/lib/store/chat-store"

export function MyComponent() {
  const { isOpen, toggleOpen, open, close } = useChatStore()

  return (
    <button onClick={toggleOpen}>
      {isOpen ? "Close Chat" : "Open Chat"}
    </button>
  )
}
```

## Features

✅ **Floating Button**
- Fixed position (bottom-right)
- Hover effects (scale, glow)
- Icon changes based on state
- Smooth transitions

✅ **Chat Window**
- Slides in from right
- Minimize/maximize functionality
- Close button
- Responsive design (mobile-friendly)

✅ **Messages**
- User/assistant bubbles
- Auto-scroll to bottom
- Timestamps
- Text wrapping

✅ **Input Area**
- Textarea with auto-grow
- Shift+Enter for new line
- Enter to send
- Send button
- Loading state

✅ **State Management**
- Zustand store (lightweight)
- Global open/minimize state
- Accessible from anywhere

✅ **Styling**
- Dark theme (gray-900)
- Tailwind CSS
- Lucide icons
- Smooth animations
- Responsive design

## Responsive Design

| Screen Size | Behavior |
|------------|----------|
| Desktop (>640px) | 400px fixed width, bottom-right |
| Mobile (<640px) | Full-width (calc(100vw - 2rem)) |
| Very Small | Bottom sheet style |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Send message |
| Shift + Enter | New line in input |
| Escape | Close (future: can add) |

## Customization

### Change Button Position
Edit `ChatBubble.tsx` className:
```typescript
className="fixed bottom-6 right-6" // Change to bottom-6 left-6 for left side
```

### Change Chat Width
Edit `ChatWindow.tsx`:
```typescript
className="w-96" // Change to w-80, w-[500px], etc.
```

### Change Colors
Edit Tailwind classes in each component:
```typescript
"bg-blue-600 hover:bg-blue-700" // Change colors
"text-white" // Change text color
```

### Add Animations
Extend the existing transition classes:
```typescript
className="transition-all duration-300" // Adjust duration
```

## Files Created

```
frontend/
├── components/
│   └── chat/
│       ├── ChatBubble.tsx         (Floating button)
│       ├── ChatWindow.tsx         (Chat panel)
│       ├── MessageBubble.tsx      (Message component)
│       ├── FloatingChat.tsx       (Wrapper)
│       └── README.md              (This file)
└── lib/
    └── store/
        └── chat-store.ts         (Zustand store)
```

## Future Enhancements

- [ ] Keyboard shortcut to close (ESC key)
- [ ] Chat history persistence (localStorage)
- [ ] Sound notifications for new messages
- [ ] Drag to reposition button
- [ ] Custom themes
- [ ] Attachment support
- [ ] Typing indicators
- [ ] Message reactions

## Dependencies

Required:
- react (^19.0.0)
- next (16.1.6)
- tailwindcss (^3.4.17)
- lucide-react (^0.460.0)
- zustand (^4.5.0) - ✅ Added

Optional:
- sonner (for notifications)
- @radix-ui/* (for additional UI components)

## Testing

Verify functionality:
1. Click floating button → Chat window opens
2. Click X button → Chat window closes
3. Click minimize button → Chat window minimizes
4. Type message + press Enter → Message sends
5. Type + Shift+Enter → New line in input
6. Mobile responsive → Full-width on small screens

---

Ready to integrate! 🚀
