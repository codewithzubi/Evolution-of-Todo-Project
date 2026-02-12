"use client"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export interface QuickReply {
  label: string
  value: string
}

interface QuickRepliesProps {
  replies: QuickReply[]
  onReplyClick: (reply: string) => void
  disabled?: boolean
}

export function QuickReplies({ replies, onReplyClick, disabled = false }: QuickRepliesProps) {
  if (!replies || replies.length === 0) {
    return null
  }

  return (
    <div className={cn(
      "flex flex-wrap gap-2 mt-3",
      "justify-start"
    )}>
      {replies.map((reply, index) => (
        <Button
          key={index}
          variant="outline"
          size="sm"
          onClick={() => {
            if (!disabled) {
              onReplyClick(reply.value)
            }
          }}
          disabled={disabled}
          className={cn(
            "text-xs sm:text-sm px-2 sm:px-3 py-1 sm:py-2",
            "border border-gray-500/50 hover:border-blue-400/50",
            "text-gray-300 hover:text-blue-300",
            "hover:bg-gray-800/80 transition-all duration-200",
            "rounded-md hover:rounded-lg",
            "whitespace-nowrap sm:whitespace-normal",
            "active:scale-95",
            disabled && "opacity-50 cursor-not-allowed hover:border-gray-500/50 hover:text-gray-300"
          )}
        >
          {reply.label}
        </Button>
      ))}
    </div>
  )
}
