"use client"

import { useState, useRef, useEffect } from "react"
import { ChevronDown, Send, Minimize2, X, MessageSquare } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useChatStore } from "@/lib/store/chat-store"
import { useChat } from "@/hooks/useChat"
import { MessageBubble } from "./MessageBubble"
import type { QuickReply } from "./quick-replies"
import { cn } from "@/lib/utils"
import { Toaster } from "sonner"

export function ChatWindow() {
  const { isOpen, isMinimized, toggleMinimize, close } = useChatStore()
  const { messages, sendMessage, isLoading } = useChat()
  const [input, setInput] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Auto-focus input when chat opens
  useEffect(() => {
    if (isOpen && !isMinimized && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen, isMinimized])

  // Generate quick replies based on message content
  const getQuickReplies = (messageContent: string): QuickReply[] => {
    const content = messageContent.toLowerCase()

    // Task added/created
    if (content.includes("add") || content.includes("added") || content.includes("created")) {
      return [
        { label: "Add another task", value: "add task" },
        { label: "Show my tasks", value: "show pending tasks" },
        { label: "Kuch aur batao", value: "help" }
      ]
    }

    // Task deleted/removed
    if (content.includes("delete") || content.includes("removed") || content.includes("removed")) {
      return [
        { label: "Show remaining", value: "show pending tasks" },
        { label: "Add new task", value: "add task" },
        { label: "Aur kuch?", value: "what can you help with?" }
      ]
    }

    // Task completed
    if (content.includes("complete") || content.includes("done") || content.includes("marked")) {
      return [
        { label: "Complete more", value: "show pending tasks" },
        { label: "Add new task", value: "add task" },
        { label: "Sab tasks dikhao", value: "show all tasks" }
      ]
    }

    // Show/list tasks
    if (content.includes("task") || content.includes("pending") || content.includes("completed")) {
      return [
        { label: "Add new task", value: "add task" },
        { label: "Show pending", value: "show pending tasks" },
        { label: "Help", value: "what can you help with?" }
      ]
    }

    // Default quick replies - matching user specification
    return [
      { label: "Add another task", value: "add task" },
      { label: "Show my tasks", value: "show pending tasks" },
      { label: "Kuch aur batao", value: "help" }
    ]
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    sendMessage(input)
    setInput("")
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }

  const handleQuickReply = (reply: string) => {
    if (!isLoading) {
      sendMessage(reply)
      setInput("")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      if (!input.trim() || isLoading) return
      sendMessage(input)
      setInput("")
    }
  }

  if (!isOpen) return null

  return (
    <>
      <div
        className={cn(
          "fixed bottom-24 right-6 z-50 transition-all duration-300",
          "w-[calc(100vw-2rem)] sm:w-96",
          "max-h-[600px] h-[600px]",
          isMinimized && "h-14",
          "flex flex-col bg-gray-900 border border-gray-700/50 rounded-lg shadow-2xl"
        )}
      >
        {/* Top Bar */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700/50 bg-gray-800/80 backdrop-blur-sm rounded-t-lg flex-shrink-0">
          <div className="flex items-center gap-2">
            <h2 className="text-white font-semibold text-sm sm:text-base">Todo Chatbot</h2>
            {isLoading && (
              <div className="flex items-center gap-1">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                <span className="text-xs text-green-400">Thinking...</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={toggleMinimize}
              className="h-6 w-6 p-0 hover:bg-gray-700 text-gray-400 hover:text-white"
              aria-label={isMinimized ? "Maximize" : "Minimize"}
            >
              {isMinimized ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <Minimize2 className="w-4 h-4" />
              )}
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={close}
              className="h-6 w-6 p-0 hover:bg-red-600/20 text-gray-400 hover:text-red-400"
              aria-label="Close chat"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Messages Area */}
        {!isMinimized && (
          <>
            <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">
              {messages.length === 0 && (
                <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
                  <MessageSquare className="w-8 h-8 mb-2 opacity-50" />
                  <p className="text-xs sm:text-sm font-medium">Start chatting to manage your tasks</p>
                  <p className="text-xs mt-2 opacity-75">Try:</p>
                  <ul className="text-xs mt-1 space-y-1 opacity-75">
                    <li>"add task buy groceries"</li>
                    <li>"complete task 1"</li>
                    <li>"show all tasks"</li>
                  </ul>
                </div>
              )}

              {messages.map((message, index) => (
                <MessageBubble
                  key={index}
                  role={message.role as "user" | "assistant"}
                  content={message.content}
                  timestamp={message.timestamp}
                  isLoading={false}
                  quickReplies={message.role === "assistant" ? getQuickReplies(message.content) : undefined}
                  onQuickReplyClick={handleQuickReply}
                  isWaitingForReply={isLoading}
                />
              ))}

              {/* Loading state - show typing indicator */}
              {isLoading && (
                <MessageBubble
                  role="assistant"
                  content=""
                  isLoading={true}
                />
              )}

              {/* Scroll anchor */}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-3 border-t border-gray-700/50 bg-gray-800/50 flex-shrink-0 flex gap-2">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={isLoading ? "Waiting for response..." : "Type message... (Shift+Enter: new line)"}
                disabled={isLoading}
                className={cn(
                  "flex-1 rounded-md border border-gray-600 bg-gray-700/50 text-white text-sm px-3 py-2",
                  "placeholder:text-gray-500 placeholder:text-xs",
                  "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-blue-500",
                  "disabled:opacity-50 disabled:cursor-not-allowed",
                  "resize-none overflow-y-auto",
                  "max-h-20 transition-colors"
                )}
                rows={1}
                maxLength={10000}
              />
              <Button
                onClick={handleSubmit}
                disabled={isLoading || !input.trim()}
                className={cn(
                  "self-end h-10 w-10 p-0 transition-all",
                  isLoading
                    ? "bg-gray-600 cursor-not-allowed"
                    : "bg-blue-600 hover:bg-blue-700 active:scale-95"
                )}
                title={isLoading ? "Waiting for response..." : "Send message (Enter)"}
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </>
        )}
      </div>

      {/* Toast container for notifications */}
      <Toaster
        position="bottom-right"
        richColors
        theme="dark"
        toastOptions={{
          style: {
            marginRight: "1.5rem",
            marginBottom: "6rem",
          },
        }}
      />
    </>
  )
}
