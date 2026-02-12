/**
 * ChatButton component - Floating button to open/close chat interface
 */
"use client"

import { useState } from "react"
import { MessageSquare, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ChatInterface } from "./ChatInterface"
import { cn } from "@/lib/utils"

export function ChatButton() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      {/* Floating Chat Button */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg z-50",
          "hover:scale-110 transition-transform"
        )}
        size="icon"
      >
        {isOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <MessageSquare className="h-6 w-6" />
        )}
      </Button>

      {/* Chat Interface Popup */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 h-[600px] z-40 shadow-2xl">
          <ChatInterface />
        </div>
      )}
    </>
  )
}
