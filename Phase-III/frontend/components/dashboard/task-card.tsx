"use client"

import { useState } from "react"
import { Task } from "@/lib/api/tasks"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Edit2, Trash2, Calendar, Tag } from "lucide-react"
import { useToggleTaskMutation } from "@/lib/hooks/use-tasks"
import { toast } from "sonner"
import { cn } from "@/lib/utils"

interface TaskCardProps {
  task: Task
  onEdit: (task: Task) => void
  onDelete: (task: Task) => void
}

const priorityConfig = {
  high: { variant: "destructive" as const, label: "High", icon: "🔴" },
  medium: { variant: "warning" as const, label: "Medium", icon: "🟡" },
  low: { variant: "info" as const, label: "Low", icon: "🟢" },
}

// Semantic tag colors - maps specific tags to colors
const getTagColor = (tag: string): { bg: string; text: string; border: string } => {
  const tagLower = tag.toLowerCase()

  // Semantic tags
  if (tagLower.includes("work") || tagLower.includes("office")) {
    return { bg: "bg-blue-500/20", text: "text-blue-300", border: "border-blue-500/30" }
  }
  if (tagLower.includes("urgent") || tagLower.includes("critical") || tagLower.includes("asap")) {
    return { bg: "bg-red-500/20", text: "text-red-300", border: "border-red-500/30" }
  }
  if (tagLower.includes("home") || tagLower.includes("personal")) {
    return { bg: "bg-green-500/20", text: "text-green-300", border: "border-green-500/30" }
  }
  if (tagLower.includes("shopping") || tagLower.includes("buy")) {
    return { bg: "bg-amber-500/20", text: "text-amber-300", border: "border-amber-500/30" }
  }
  if (tagLower.includes("health") || tagLower.includes("medical")) {
    return { bg: "bg-pink-500/20", text: "text-pink-300", border: "border-pink-500/30" }
  }
  if (tagLower.includes("learn") || tagLower.includes("study") || tagLower.includes("education")) {
    return { bg: "bg-purple-500/20", text: "text-purple-300", border: "border-purple-500/30" }
  }

  // Default color rotation for other tags
  const colors = [
    { bg: "bg-indigo-500/20", text: "text-indigo-300", border: "border-indigo-500/30" },
    { bg: "bg-cyan-500/20", text: "text-cyan-300", border: "border-cyan-500/30" },
    { bg: "bg-orange-500/20", text: "text-orange-300", border: "border-orange-500/30" },
    { bg: "bg-teal-500/20", text: "text-teal-300", border: "border-teal-500/30" },
  ]

  let hash = 0
  for (let i = 0; i < tag.length; i++) {
    hash = tag.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

export function TaskCard({ task, onEdit, onDelete }: TaskCardProps) {
  const [isHovering, setIsHovering] = useState(false)
  const toggleMutation = useToggleTaskMutation()

  const handleToggle = async () => {
    try {
      await toggleMutation.mutateAsync(task.id)
      toast.success(
        task.is_completed ? "Task marked as pending" : "Task completed! 🎉"
      )
    } catch (error) {
      toast.error("Failed to update task")
    }
  }

  const tags = task.tags
    ? task.tags.split(",").map((tag) => tag.trim())
    : []

  const dueDate = task.due_date
    ? new Date(task.due_date).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      })
    : null

  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && !task.is_completed
  const isMobile = typeof window !== "undefined" && window.innerWidth < 768

  return (
    <Card
      className={cn(
        "relative overflow-hidden transition-all duration-300",
        "bg-gradient-to-br from-gray-800 to-gray-900/80 backdrop-blur-sm",
        "border border-gray-700/50 hover:border-blue-500/50",
        "hover:shadow-2xl hover:shadow-blue-500/20",
        isMobile ? "hover:shadow-lg hover:shadow-blue-500/10" : "",
        "group"
      )}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      {/* Background gradient on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

      <div className="relative p-5 space-y-4">
        {/* Top Row: ID + Checkbox */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2.5 flex-shrink-0">
            {/* Checkbox - Green when completed */}
            <div
              className={cn(
                "w-5 h-5 rounded border-2 flex items-center justify-center cursor-pointer transition-all duration-200",
                task.is_completed
                  ? "bg-green-500/80 border-green-400 shadow-lg shadow-green-500/30"
                  : "border-gray-500 hover:border-blue-400 hover:bg-blue-500/10"
              )}
            >
              <input
                type="checkbox"
                checked={task.is_completed}
                onChange={handleToggle}
                disabled={toggleMutation.isPending}
                className="w-4 h-4 cursor-pointer opacity-0 absolute"
                aria-label={`Toggle ${task.title}`}
              />
              {task.is_completed && (
                <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              )}
            </div>

            {/* Task ID - Bold and prominent */}
            <div className="px-2.5 py-1 bg-gradient-to-r from-blue-600/40 to-blue-500/20 rounded-md border border-blue-500/30 backdrop-blur-sm">
              <span className="text-xs font-extrabold text-blue-200">#{task.id}</span>
            </div>
          </div>

          {/* Action Buttons - Always visible on mobile, on hover on desktop */}
          <div
            className={cn(
              "flex items-center gap-1.5 flex-shrink-0 transition-all duration-200",
              isMobile || isHovering ? "opacity-100 scale-100" : "opacity-0 scale-90 pointer-events-none"
            )}
          >
            <Button
              size="sm"
              variant="ghost"
              onClick={() => onEdit(task)}
              className="h-8 w-8 p-0 hover:bg-blue-600/30 hover:text-blue-300 text-gray-400 transition-all duration-200"
              disabled={toggleMutation.isPending}
            >
              <Edit2 className="w-3.5 h-3.5" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => onDelete(task)}
              className="h-8 w-8 p-0 hover:bg-red-600/30 hover:text-red-300 text-gray-400 transition-all duration-200"
              disabled={toggleMutation.isPending}
            >
              <Trash2 className="w-3.5 h-3.5" />
            </Button>
          </div>
        </div>

        {/* Title - Bigger and more prominent */}
        <div className="space-y-1">
          <h3
            className={cn(
              "text-lg font-bold leading-snug transition-all duration-200 group-hover:text-blue-100",
              task.is_completed
                ? "line-through text-gray-500"
                : "text-white"
            )}
          >
            {task.title}
          </h3>

          {/* Description - Smaller and secondary */}
          {task.description && (
            <p className={cn(
              "text-xs leading-relaxed line-clamp-2 transition-colors duration-200",
              task.is_completed ? "text-gray-600" : "text-gray-400 group-hover:text-gray-300"
            )}>
              {task.description}
            </p>
          )}
        </div>

        {/* Status & Priority Badges Row */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          {/* Status Badge - Orange (Pending) or Green (Completed) */}
          <Badge
            className={cn(
              "text-xs font-semibold px-2.5 py-1 rounded-full",
              task.is_completed
                ? "bg-green-500/30 text-green-300 border border-green-500/50 shadow-lg shadow-green-500/20"
                : "bg-orange-500/30 text-orange-300 border border-orange-500/50 shadow-lg shadow-orange-500/20"
            )}
          >
            {task.is_completed ? "✓ Completed" : "○ Pending"}
          </Badge>

          {/* Priority Badge */}
          <Badge
            variant={priorityConfig[task.priority].variant}
            className="text-xs font-semibold px-2.5 py-1 rounded-full"
          >
            {priorityConfig[task.priority].icon} {priorityConfig[task.priority].label}
          </Badge>
        </div>

        {/* Due Date - Red if past */}
        {dueDate && (
          <div className={cn(
            "flex items-center gap-2 text-xs font-medium px-2.5 py-1.5 rounded-lg border",
            isOverdue
              ? "bg-red-500/20 text-red-300 border-red-500/40 shadow-lg shadow-red-500/20"
              : "bg-gray-700/50 text-gray-300 border-gray-600/50"
          )}>
            <Calendar className="w-3.5 h-3.5" />
            <span>
              {isOverdue && "🚨 Overdue: "}
              {dueDate}
            </span>
          </div>
        )}

        {/* Tags - Colored badges with semantic meanings */}
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2 pt-1">
            {tags.map((tag, idx) => {
              const colors = getTagColor(tag)
              return (
                <div
                  key={idx}
                  className={cn(
                    "flex items-center gap-1.5 px-2.5 py-1.5 rounded-full border text-xs font-medium",
                    colors.bg,
                    colors.text,
                    colors.border
                  )}
                >
                  <Tag className="w-2.5 h-2.5" />
                  <span>{tag}</span>
                </div>
              )
            })}
          </div>
        )}

        {/* No due date message */}
        {!dueDate && (
          <div className="flex items-center gap-2 text-xs text-gray-500 px-2.5 py-1">
            <Calendar className="w-3.5 h-3.5" />
            <span>No due date</span>
          </div>
        )}
      </div>
    </Card>
  )
}
