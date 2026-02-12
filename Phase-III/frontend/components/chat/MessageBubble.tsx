"use client"

import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { QuickReplies, type QuickReply } from "./quick-replies"

interface MessageBubbleProps {
  content: string
  role: "user" | "assistant"
  timestamp?: Date
  isLoading?: boolean
  quickReplies?: QuickReply[]
  onQuickReplyClick?: (reply: string) => void
  isWaitingForReply?: boolean
}

export function MessageBubble({
  content,
  role,
  timestamp,
  isLoading,
  quickReplies,
  onQuickReplyClick,
  isWaitingForReply = false
}: MessageBubbleProps) {
  const isUser = role === "user"

  if (isLoading) {
    return (
      <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
        <div
          className={cn(
            "rounded-lg px-4 py-2",
            isUser
              ? "bg-blue-600 text-white rounded-br-none"
              : "bg-gray-700 text-gray-100 rounded-bl-none"
          )}
        >
          <div className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">Typing</span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}>
      <div className={cn("max-w-[80%] sm:max-w-[70%]", isUser && "flex flex-col items-end")}>
        <div
          className={cn(
            "rounded-lg px-4 py-2 text-sm whitespace-pre-wrap break-words",
            isUser
              ? "bg-blue-600 text-white rounded-br-none"
              : "bg-gray-700 text-gray-100 rounded-bl-none"
          )}
        >
          <p>{content}</p>
          {timestamp && (
            <p className={cn("text-xs mt-1 opacity-70", isUser ? "text-blue-200" : "text-gray-400")}>
              {timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </p>
          )}
        </div>

        {/* Quick Replies - only for assistant messages */}
        {!isUser && quickReplies && quickReplies.length > 0 && onQuickReplyClick && (
          <QuickReplies
            replies={quickReplies}
            onReplyClick={onQuickReplyClick}
            disabled={isWaitingForReply}
          />
        )}
      </div>
    </div>
  )
}
