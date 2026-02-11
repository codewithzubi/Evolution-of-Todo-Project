"use client"

import { Task } from "@/lib/api/tasks"
import { Button } from "@/components/ui/button"
import { useDeleteTaskMutation } from "@/lib/hooks/use-tasks"
import { toast } from "sonner"
import { AlertCircle } from "lucide-react"

interface DeleteConfirmDialogProps {
  isOpen: boolean
  task: Task | null
  onClose: () => void
}

export function DeleteConfirmDialog({ isOpen, task, onClose }: DeleteConfirmDialogProps) {
  const deleteMutation = useDeleteTaskMutation()

  const handleConfirmDelete = async () => {
    if (!task) return

    try {
      await deleteMutation.mutateAsync(task.id)
      toast.success("Task deleted successfully")
      onClose()
    } catch (error: any) {
      toast.error(error.message || "Failed to delete task")
    }
  }

  if (!isOpen || !task) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 border border-red-900/30 rounded-xl shadow-2xl w-full max-w-md mx-4 p-6 animate-in zoom-in-95 duration-200">
        {/* Icon and Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className="flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-900/20 ring-2 ring-red-900/50">
            <AlertCircle className="h-6 w-6 text-red-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Delete Task</h2>
            <p className="text-xs text-gray-400">This action cannot be undone</p>
          </div>
        </div>

        {/* Message */}
        <div className="mb-6">
          <p className="text-gray-300 mb-3">
            Are you sure you want to delete this task?
          </p>
          <div className="bg-gray-900/50 border border-gray-700/50 rounded-lg p-4 space-y-2">
            <p className="text-sm font-semibold text-white">{task.title}</p>
            {task.description && (
              <p className="text-xs text-gray-400 line-clamp-2">
                {task.description}
              </p>
            )}
          </div>
        </div>

        {/* Buttons */}
        <div className="flex gap-3 justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={deleteMutation.isPending}
            className="border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
          >
            Cancel
          </Button>
          <Button
            type="button"
            onClick={handleConfirmDelete}
            disabled={deleteMutation.isPending}
            className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 shadow-lg shadow-red-500/20 transition-all"
          >
            {deleteMutation.isPending ? "Deleting..." : "Delete Task"}
          </Button>
        </div>
      </div>
    </div>
  )
}
