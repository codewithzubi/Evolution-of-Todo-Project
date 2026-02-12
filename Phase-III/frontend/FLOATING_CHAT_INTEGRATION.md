# Floating Chat Integration Guide

## Quick Start

### Step 1: Install Zustand
```bash
npm install zustand
# or
pnpm add zustand
```

### Step 2: Add to Layout
Choose where to add the floating chat (usually in the root layout):

**Option A: Root Layout (Global)**
```typescript
// app/layout.tsx
import { FloatingChat } from "@/components/chat/FloatingChat"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        <FloatingChat />
      </body>
    </html>
  )
}
```

**Option B: Dashboard Layout Only**
```typescript
// app/(protected)/dashboard/layout.tsx
import { FloatingChat } from "@/components/chat/FloatingChat"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div>
      {children}
      <FloatingChat />
    </div>
  )
}
```

### Step 3: Done! 🎉
The floating chat button will now appear in the bottom-right corner of your screen.

---

## File Structure

```
frontend/
├── components/
│   └── chat/
│       ├── ChatBubble.tsx              (Floating button)
│       ├── ChatWindow.tsx              (Chat panel + messages)
│       ├── MessageBubble.tsx           (Single message bubble)
│       ├── FloatingChat.tsx            (Main wrapper)
│       └── README.md                   (Detailed docs)
├── lib/
│   └── store/
│       └── chat-store.ts              (Zustand state)
└── hooks/
    └── useChat.ts                     (Already exists - chat hook)
```

---

## How It Works

### 1. Floating Button (ChatBubble.tsx)
```
┌─────────────────────────────────┐
│                             ╭───╮
│     Your Page Content      │ 💬 │  ← Floating button
│                             ╰───╯
└─────────────────────────────────┘
```

### 2. Click to Open Chat Window
```
┌──────────────────────────────────────────┐
│                      ╔═══════════════════╗
│ Your Page Content    ║ Todo Chatbot    ✖ ║  ← Chat window
│                      ║─────────────────  ║
│                      ║ Messages here...  ║
│                      ║                   ║
│                      ║ [Input] [Send]    ║
│                      ╚═══════════════════╝
└──────────────────────────────────────────┘
```

---

## Features

### Floating Button
- **Position**: Fixed bottom-right corner
- **Icon**: Lucide MessageSquare (💬)
- **Hover**: Scale up + glow effect
- **Click**: Open/Close chat window
- **Visual**: Blue gradient with hover effect

### Chat Window
- **Width**: ~400px (responsive on mobile)
- **Height**: Max 600px
- **Slide**: Smooth slide-in from right
- **Theme**: Dark (gray-900 background)
- **Controls**:
  - Minimize button (collapse)
  - Close button (exit)
- **Messages**:
  - User: Blue right-aligned bubbles
  - Assistant: Gray left-aligned bubbles
  - Auto-scroll to latest
- **Input**:
  - Textarea with auto-grow
  - Shift+Enter = new line
  - Enter = send
  - Send button
  - Loading spinner

### State Management (Zustand)
```typescript
// Access chat state anywhere
import { useChatStore } from "@/lib/store/chat-store"

export function MyComponent() {
  const { isOpen, isMinimized, toggleOpen, close } = useChatStore()

  return (
    <button onClick={toggleOpen}>
      {isOpen ? "Close" : "Open"} Chat
    </button>
  )
}
```

---

## Responsive Design

### Desktop (>640px)
- 400px fixed width
- Positioned bottom-right
- Standard chat window

### Mobile (<640px)
- Full-width (calc(100vw - 2rem))
- Still bottom-right positioned
- Bottom sheet style

---

## Customization

### Change Button Colors
**File**: `components/chat/ChatBubble.tsx`
```typescript
// Line ~25
className={cn(
  "bg-gradient-to-r from-blue-600 to-blue-500",  // ← Change colors
  "hover:from-blue-700 hover:to-blue-600"
)}
```

### Change Chat Window Width
**File**: `components/chat/ChatWindow.tsx`
```typescript
// Line ~61
className={cn(
  "w-[calc(100vw-2rem)] sm:w-96",  // Change w-96 to w-80, w-[500px], etc.
)}
```

### Change Dark Theme
**File**: `components/chat/ChatWindow.tsx`
```typescript
// Replace gray-900/gray-800 with your preferred colors
"bg-gray-900"  // Main background
"bg-gray-800"  // Top bar
"text-white"   // Text color
```

---

## Usage Examples

### Simple: Just Add to Layout
```typescript
// app/layout.tsx
import { FloatingChat } from "@/components/chat/FloatingChat"

export default function RootLayout({ children }) {
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

### Advanced: Custom Controls
```typescript
import { useChatStore } from "@/lib/store/chat-store"

export function ChatControls() {
  const { isOpen, open, close, toggleMinimize } = useChatStore()

  return (
    <div>
      {isOpen && (
        <>
          <button onClick={close}>Close Chat</button>
          <button onClick={toggleMinimize}>Min/Max</button>
        </>
      )}
      {!isOpen && <button onClick={open}>Open Chat</button>}
    </div>
  )
}
```

### Advanced: Monitor Chat State
```typescript
import { useShallow } from "zustand/react"
import { useChatStore } from "@/lib/store/chat-store"

export function ChatStatus() {
  const { isOpen, isMinimized } = useChatStore(
    useShallow((state) => ({
      isOpen: state.isOpen,
      isMinimized: state.isMinimized,
    }))
  )

  return (
    <div>
      Status: {isOpen ? "Open" : "Closed"} {isMinimized ? "- Minimized" : ""}
    </div>
  )
}
```

---

## Testing Checklist

- [ ] Click floating button → Chat window opens
- [ ] Chat window slides in from right
- [ ] Click X button → Window closes, button visible
- [ ] Click minimize button → Window collapses
- [ ] Type message + press Enter → Message appears
- [ ] Type message + Shift+Enter → New line in input
- [ ] Messages auto-scroll to bottom
- [ ] User messages appear on right (blue)
- [ ] Assistant messages appear on left (gray)
- [ ] Mobile view: Full-width chat window
- [ ] Mobile view: Responsive buttons
- [ ] Send button shows loading spinner while sending

---

## Troubleshooting

### Zustand Not Found
```bash
npm install zustand
pnpm install zustand
# Then restart dev server
npm run dev
```

### Chat Window Not Appearing
1. Check that `FloatingChat` is in your layout
2. Verify `z-50` z-index is highest on page
3. Check browser console for errors
4. Clear browser cache (Ctrl+F5)

### State Not Updating
- Ensure `useChatStore` is imported from `@/lib/store/chat-store`
- Clear Next.js cache: `rm -rf .next`
- Restart dev server

### Styling Issues
- Verify Tailwind CSS is configured
- Check that classes are in `globals.css`
- Ensure `shadcn/ui` Button component is installed
- Verify Lucide icons are installed

---

## Next Steps

1. ✅ Create floating chat components
2. ✅ Set up Zustand store
3. ⬜ Add to layout/page
4. ⬜ Test functionality
5. ⬜ Optional: Add sound notifications
6. ⬜ Optional: Add keyboard shortcuts (ESC to close)
7. ⬜ Optional: Add chat history persistence

---

## Files Summary

| File | Purpose |
|------|---------|
| `ChatBubble.tsx` | Floating button in bottom-right |
| `ChatWindow.tsx` | Chat panel with messages & input |
| `MessageBubble.tsx` | Individual message component |
| `FloatingChat.tsx` | Wrapper component |
| `chat-store.ts` | Zustand state management |
| `README.md` | Detailed documentation |

---

Ready to go! 🚀

Add `<FloatingChat />` to your layout and you're done!
