"use client"

import { useState } from "react"
import { Task } from "@/lib/api/tasks"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Edit2, Trash2, Calendar, Tag } from "lucide-react"
import { useToggleTaskMutation } from "@/lib/hooks/use-tasks"
import { toast } from "sonner"

interface TaskCardProps {
  task: Task
  onEdit: (task: Task) => void
  onDelete: (task: Task) => void
}

const priorityConfig = {
  high: { variant: "destructive" as const, label: "High" },
  medium: { variant: "warning" as const, label: "Medium" },
  low: { variant: "info" as const, label: "Low" },
}

// Simple hash function to assign consistent colors to tags
const getTagColor = (tag: string): "purple" | "pink" | "info" | "gray" | "secondary" => {
  const colors: Array<"purple" | "pink" | "info" | "gray" | "secondary"> = ["purple", "pink", "info", "gray", "secondary"]
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

  return (
    <Card
      className="p-4 bg-gray-800/80 backdrop-blur-sm border-gray-700/50 hover:border-blue-500/50 hover:shadow-xl hover:shadow-blue-500/10 transition-all duration-300 group"
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <input
          type="checkbox"
          checked={task.is_completed}
          onChange={handleToggle}
          disabled={toggleMutation.isPending}
          className="mt-1.5 w-4 h-4 accent-blue-500 cursor-pointer flex-shrink-0 transition-transform hover:scale-110"
          aria-label={`Toggle ${task.title}`}
        />

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3
            className={`text-base font-semibold transition-all duration-200 ${
              task.is_completed
                ? "line-through text-gray-500"
                : "text-white group-hover:text-blue-100"
            }`}
          >
            {task.title}
          </h3>

          {task.description && (
            <p className="text-sm text-gray-400 mt-1.5 line-clamp-2">
              {task.description}
            </p>
          )}

          {/* Metadata Row */}
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {/* Status Badge */}
            <Badge variant={task.is_completed ? "success" : "warning"}>
              {task.is_completed ? "Completed" : "Pending"}
            </Badge>

            {/* Priority Badge */}
            <Badge variant={priorityConfig[task.priority].variant}>
              {priorityConfig[task.priority].label}
            </Badge>

            {/* Due Date */}
            {dueDate && (
              <Badge
                variant={isOverdue ? "destructive" : "gray"}
                className="gap-1"
              >
                <Calendar className="w-3 h-3" />
                Due: {dueDate}
              </Badge>
            )}
          </div>

          {/* Tags */}
          {tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-2.5">
              {tags.map((tag, idx) => (
                <Badge
                  key={idx}
                  variant={getTagColor(tag)}
                  className="gap-1 text-xs"
                >
                  <Tag className="w-2.5 h-2.5" />
                  {tag}
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* Action Buttons - Always visible on mobile, on hover on desktop */}
        <div
          className={`flex items-center gap-2 flex-shrink-0 transition-all duration-200 ${
            isHovering || (typeof window !== "undefined" && window.innerWidth < 768)
              ? "opacity-100 translate-x-0"
              : "opacity-0 translate-x-2 pointer-events-none"
          }`}
        >
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onEdit(task)}
            className="h-8 w-8 p-0 hover:bg-blue-600/20 hover:text-blue-400 transition-colors"
            disabled={toggleMutation.isPending}
          >
            <Edit2 className="w-4 h-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onDelete(task)}
            className="h-8 w-8 p-0 hover:bg-red-600/20 hover:text-red-400 transition-colors"
            disabled={toggleMutation.isPending}
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </Card>
  )
}
