"use client"

import { Button } from "@/components/ui/button"
import { InboxIcon, ListPlus, Sparkles } from "lucide-react"

interface EmptyStateProps {
  filter?: "all" | "pending" | "completed"
  onAddTask: () => void
  language?: "en" | "urdu"
}

const messages = {
  en: {
    all: {
      title: "No tasks yet. Add your first one! 🚀",
      description: "Start organizing your day with your first task. It's that simple!",
      button: "Create Your First Task",
    },
    pending: {
      title: "All caught up! ✨",
      description: "No pending tasks at the moment. Great job!",
      button: "Add a New Task",
    },
    completed: {
      title: "No completed tasks yet",
      description: "Complete some tasks to see them here. You've got this!",
      button: null,
    },
  },
  urdu: {
    all: {
      title: "Abhi koi task nahi hai. Pehla task add karo! 🚀",
      description: "Apni din ko organize karo apna pehla task banane se!",
      button: "Apna Pehla Task Banao",
    },
    pending: {
      title: "Sab kuch complete ho gaya! ✨",
      description: "Abhi koi pending task nahi hai. Zabardast kaam!",
      button: "Naya Task Add Karo",
    },
    completed: {
      title: "Abhi koi completed task nahi",
      description: "Kuch tasks complete karo unhe yahan dikhne ke liye.",
      button: null,
    },
  },
}

export function EmptyState({ filter = "all", onAddTask, language = "en" }: EmptyStateProps) {
  const messageSet = language === "urdu" ? messages.urdu : messages.en
  const message = messageSet[filter]

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] px-4 py-12 animate-in fade-in duration-500">
      {/* Decorative background gradient */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-full blur-3xl" />
      </div>

      {/* Main content */}
      <div className="relative z-10 text-center max-w-md">
        {/* Icon Container */}
        <div className="relative mb-8 inline-flex">
          {/* Background glow */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full opacity-20 blur-xl -m-2" />

          {/* Icon circle */}
          <div className="relative w-24 h-24 rounded-full bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/20 flex items-center justify-center group hover:border-blue-500/40 transition-all duration-300">
            {filter === "all" ? (
              <>
                <ListPlus className="w-12 h-12 text-blue-400 group-hover:text-blue-300 transition-colors" />
                <Sparkles className="absolute w-5 h-5 text-purple-400 top-2 right-2 group-hover:animate-spin" />
              </>
            ) : (
              <InboxIcon className="w-12 h-12 text-blue-400 group-hover:text-blue-300 transition-colors" />
            )}
          </div>
        </div>

        {/* Title */}
        <h3 className="text-2xl sm:text-3xl font-bold text-white mb-3 leading-tight">
          {message.title}
        </h3>

        {/* Description */}
        <p className="text-gray-400 text-base sm:text-lg mb-8 leading-relaxed">
          {message.description}
        </p>

        {/* Action Button */}
        {message.button && (
          <Button
            onClick={onAddTask}
            size="lg"
            className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 gap-2 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30 transition-all duration-200 transform hover:scale-105 text-white font-semibold"
          >
            <ListPlus className="w-5 h-5" />
            {message.button}
          </Button>
        )}

        {/* Subtle hint for completed filter */}
        {filter === "completed" && (
          <div className="mt-8 pt-8 border-t border-gray-700/50">
            <p className="text-sm text-gray-500">
              💡 {language === "urdu" ? "Kuch tasks ko complete karne ki koshish karo!" : "Try completing some tasks to see them here!"}
            </p>
          </div>
        )}
      </div>

      {/* Bottom decoration */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-gray-900 to-transparent pointer-events-none" />
    </div>
  )
}
