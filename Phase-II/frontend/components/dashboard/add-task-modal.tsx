"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { useCreateTaskMutation } from "@/lib/hooks/use-tasks"
import { toast } from "sonner"
import { X, Tag } from "lucide-react"

interface AddTaskModalProps {
  isOpen: boolean
  onClose: () => void
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

export function AddTaskModal({ isOpen, onClose }: AddTaskModalProps) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [dueDate, setDueDate] = useState("")
  const [priority, setPriority] = useState<"high" | "medium" | "low">("medium")
  const [tagsInput, setTagsInput] = useState("")
  const createMutation = useCreateTaskMutation()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validation
    if (!title.trim()) {
      toast.error("Title is required")
      return
    }

    if (title.length > 200) {
      toast.error("Title must be 200 characters or less")
      return
    }

    if (description.length > 1000) {
      toast.error("Description must be 1000 characters or less")
      return
    }

    if (tagsInput.length > 500) {
      toast.error("Tags must be 500 characters or less")
      return
    }

    try {
      await createMutation.mutateAsync({
        title: title.trim(),
        description: description.trim() || undefined,
        due_date: dueDate || undefined,
        priority,
        tags: tagsInput.trim() || undefined,
      })
      toast.success("Task created successfully")
      // Reset form
      setTitle("")
      setDescription("")
      setDueDate("")
      setPriority("medium")
      setTagsInput("")
      onClose()
    } catch (error: any) {
      toast.error(error.message || "Failed to create task")
    }
  }

  if (!isOpen) return null

  const tags = tagsInput
    .split(",")
    .map((tag) => tag.trim())
    .filter((tag) => tag.length > 0)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700/50 rounded-xl shadow-2xl w-full max-w-2xl mx-4 p-6 max-h-[90vh] overflow-y-auto animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white">Create New Task</h2>
            <p className="text-sm text-gray-400 mt-1">Add a new task to your list</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors rounded-lg p-1 hover:bg-gray-700/50"
            aria-label="Close"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Title Input */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-300 mb-2">
              Title <span className="text-red-400">*</span>
            </label>
            <Input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="What needs to be done?"
              maxLength={200}
              disabled={createMutation.isPending}
              className="bg-gray-900/50 border-gray-700 text-white placeholder-gray-500 text-base focus:border-blue-500 transition-colors"
            />
            <p className="text-xs text-gray-500 mt-1.5">
              {title.length}/200 characters
            </p>
          </div>

          {/* Description Input */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-2">
              Description <span className="text-gray-500 font-normal">(optional)</span>
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add more details about this task..."
              maxLength={1000}
              disabled={createMutation.isPending}
              rows={3}
              className="w-full px-3 py-2 bg-gray-900/50 border border-gray-700 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 resize-none text-sm transition-all"
            />
            <p className="text-xs text-gray-500 mt-1.5">
              {description.length}/1000 characters
            </p>
          </div>

          {/* Row: Due Date and Priority */}
          <div className="grid grid-cols-2 gap-4">
            {/* Due Date */}
            <div>
              <label htmlFor="dueDate" className="block text-sm font-medium text-gray-300 mb-2">
                Due Date <span className="text-gray-500 font-normal">(optional)</span>
              </label>
              <Input
                id="dueDate"
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                disabled={createMutation.isPending}
                className="bg-gray-900/50 border-gray-700 text-white text-sm focus:border-blue-500 transition-colors"
              />
            </div>

            {/* Priority */}
            <div>
              <label htmlFor="priority" className="block text-sm font-medium text-gray-300 mb-2">
                Priority <span className="text-red-400">*</span>
              </label>
              <Select
                id="priority"
                value={priority}
                onChange={(e) => setPriority(e.target.value as "high" | "medium" | "low")}
                disabled={createMutation.isPending}
                className="text-sm"
              >
                <option value="low">Low Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="high">High Priority</option>
              </Select>
            </div>
          </div>

          {/* Priority Badge Preview */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400">Preview:</span>
            <Badge variant={priorityConfig[priority].variant}>
              {priorityConfig[priority].label}
            </Badge>
          </div>

          {/* Tags Input */}
          <div>
            <label htmlFor="tags" className="block text-sm font-medium text-gray-300 mb-2">
              Tags <span className="text-gray-500 font-normal">(optional, comma-separated)</span>
            </label>
            <Input
              id="tags"
              type="text"
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
              placeholder="e.g. work, urgent, home"
              maxLength={500}
              disabled={createMutation.isPending}
              className="bg-gray-900/50 border-gray-700 text-white placeholder-gray-500 text-sm focus:border-blue-500 transition-colors"
            />
            <p className="text-xs text-gray-500 mt-1.5">
              {tagsInput.length}/500 characters
            </p>

            {/* Tags Preview */}
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3 p-3 bg-gray-900/30 rounded-lg border border-gray-700/50">
                {tags.map((tag, idx) => (
                  <Badge
                    key={idx}
                    variant={getTagColor(tag)}
                    className="gap-1"
                  >
                    <Tag className="w-3 h-3" />
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Buttons */}
          <div className="flex gap-3 justify-end pt-4 border-t border-gray-700/50">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={createMutation.isPending}
              className="border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createMutation.isPending}
              className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 gap-2 shadow-lg shadow-blue-500/20 transition-all"
            >
              {createMutation.isPending ? "Creating..." : "Create Task"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
