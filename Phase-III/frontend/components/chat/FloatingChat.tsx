"use client"

import { ChatBubble } from "./ChatBubble"
import { ChatWindow } from "./ChatWindow"

/**
 * FloatingChat component - Main wrapper for floating chatbot UI
 * Combines the floating button and chat window
 */
export function FloatingChat() {
  return (
    <>
      <ChatBubble />
      <ChatWindow />
    </>
  )
}
