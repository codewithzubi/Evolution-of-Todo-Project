/**
 * Custom hook for managing chat state with TanStack Query
 */
"use client"

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { toast } from "sonner"
import { chatApi, ChatRequest, ChatResponse } from "@/lib/api-client"

export interface ChatMessage {
  role: "user" | "assistant"
  content: string
  timestamp?: Date
}

export function useChat() {
  const [conversationId, setConversationId] = useState<string | undefined>()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const queryClient = useQueryClient()

  const sendMessageMutation = useMutation({
    mutationFn: (message: string) => {
      const request: ChatRequest = {
        message,
        conversation_id: conversationId,
      }
      return chatApi.sendMessage(request)
    },
    onSuccess: (data: ChatResponse) => {
      // Update conversation ID if this is a new conversation
      if (!conversationId) {
        setConversationId(data.conversation_id)
      }

      // Add assistant response to messages with timestamp
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          timestamp: new Date()
        },
      ])

      // Invalidate tasks query to refresh task list if tools were used
      if (data.tools_used && data.tools_used.length > 0) {
        queryClient.invalidateQueries({ queryKey: ["tasks"] })

        // Show specific success message based on operation
        const operation = data.tools_used[0]
        const operationMessages: Record<string, string> = {
          "add_task": "Task added successfully",
          "delete_task": "Task deleted successfully",
          "toggle_task": "Task status updated",
          "update_task": "Task updated successfully",
          "list_tasks": "Tasks loaded",
        }

        const message = operationMessages[operation] || "Action completed successfully"
        toast.success(message)
      }
    },
    onError: (error: Error) => {
      // Show error toast notification
      const errorMessage = error.message || "Failed to send message"
      toast.error(errorMessage)

      // Add error message to chat with timestamp
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `I encountered an error: ${errorMessage}. Please try again or rephrase your request.`,
          timestamp: new Date()
        },
      ])
    },
  })

  const sendMessage = (message: string) => {
    // Add user message to messages immediately with timestamp
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: message,
        timestamp: new Date()
      }
    ])

    // Send to API
    sendMessageMutation.mutate(message)
  }

  const clearChat = () => {
    setMessages([])
    setConversationId(undefined)
  }

  return {
    messages,
    sendMessage,
    clearChat,
    isLoading: sendMessageMutation.isPending,
    error: sendMessageMutation.error,
    conversationId,
  }
}
