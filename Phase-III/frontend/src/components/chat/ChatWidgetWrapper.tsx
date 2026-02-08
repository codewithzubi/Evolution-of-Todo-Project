// [Task]: T347, [From]: specs/004-ai-chatbot/spec.md
// ChatWidgetWrapper - Client component wrapper for ChatWidget

'use client';

import dynamic from 'next/dynamic';

// Dynamically import ChatWidget to reduce bundle impact
const ChatWidget = dynamic(() => import('./ChatWidget').then(mod => ({ default: mod.ChatWidget })), {
  loading: () => null,
  ssr: false
});

/**
 * ChatWidgetWrapper Component
 * Wraps ChatWidget to enable client-side only loading and dynamic imports
 */
export function ChatWidgetWrapper() {
  return <ChatWidget />;
}
