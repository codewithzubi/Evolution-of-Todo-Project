"use client"

import { MessageSquare, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useChatStore } from "@/lib/store/chat-store"
import { cn } from "@/lib/utils"

export function ChatBubble() {
  const { isOpen, toggleOpen } = useChatStore()

  return (
    <Button
      onClick={toggleOpen}
      className={cn(
        "fixed bottom-6 right-6 rounded-full w-14 h-14 shadow-lg hover:shadow-xl transition-all duration-300 z-40",
        "flex items-center justify-center p-0",
        "bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600",
        "hover:scale-110 active:scale-95",
        isOpen && "bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600"
      )}
      aria-label={isOpen ? "Close chat" : "Open chat"}
    >
      {isOpen ? (
        <X className="w-6 h-6 text-white" />
      ) : (
        <MessageSquare className="w-6 h-6 text-white" />
      )}
    </Button>
  )
}
