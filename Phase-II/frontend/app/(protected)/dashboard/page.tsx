"use client"

/**
 * Dashboard page - Task CRUD interface
 *
 * Features:
 * - View tasks with status filtering (All, Pending, Completed)
 * - Add new tasks
 * - Edit existing tasks
 * - Toggle task completion
 * - Delete tasks
 * - User logout
 */

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useUser } from "@/hooks/use-user"
import { useAuth } from "@/hooks/use-auth"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { ThemeToggle } from "@/components/theme-toggle"
import { toast } from "sonner"
import { Plus, CheckCircle2, ListTodo, AlertCircle } from "lucide-react"

import { Task } from "@/lib/api/tasks"
import { useTasksQuery } from "@/lib/hooks/use-tasks"
import { Sidebar } from "@/components/dashboard/sidebar"
import { TaskCard } from "@/components/dashboard/task-card"
import { AddTaskModal } from "@/components/dashboard/add-task-modal"
import { EditTaskModal } from "@/components/dashboard/edit-task-modal"
import { DeleteConfirmDialog } from "@/components/dashboard/delete-confirm-dialog"

export default function DashboardPage() {
  const router = useRouter()
  const { user } = useUser()
  const { logout, isLoggingOut } = useAuth()

  // State for filters and modals
  const [activeFilter, setActiveFilter] = useState<"all" | "pending" | "completed">("all")
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [deletingTask, setDeletingTask] = useState<Task | null>(null)

  // Fetch tasks with filtering
  const { data: tasks = [], isLoading, error } = useTasksQuery(activeFilter)

  const handleLogout = async () => {
    try {
      await logout()
      toast.success("Logged out successfully")
      router.push("/")
    } catch (error) {
      toast.error("Logout failed")
      console.error("Logout failed:", error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800 flex flex-col">
      {/* Navbar */}
      <nav className="bg-gray-800/80 backdrop-blur-sm border-b border-gray-700/50 sticky top-0 z-40">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-semibold text-white">My Tasks</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                onClick={() => setIsAddModalOpen(true)}
                className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 gap-2 shadow-lg shadow-blue-500/20 transition-all duration-200"
              >
                <Plus className="w-4 h-4" />
                Add Task
              </Button>
              <ThemeToggle />
              <span className="text-sm text-gray-400 hidden sm:inline">{user?.email}</span>
              <Button
                onClick={handleLogout}
                disabled={isLoggingOut}
                variant="outline"
                size="sm"
                className="border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
              >
                {isLoggingOut ? "Logging out..." : "Logout"}
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar activeFilter={activeFilter} onFilterChange={setActiveFilter} />

        {/* Tasks area */}
        <main className="flex-1 overflow-auto p-6">
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="p-4 bg-gray-800 border border-gray-700 rounded-lg space-y-3">
                  <div className="flex items-start gap-3">
                    <Skeleton className="w-4 h-4 rounded mt-1" />
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-5 w-3/4" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-2/3" />
                      <div className="flex gap-2 mt-3">
                        <Skeleton className="h-6 w-20 rounded-full" />
                        <Skeleton className="h-6 w-16 rounded-full" />
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 rounded-full bg-red-900/20 flex items-center justify-center mb-4">
                <AlertCircle className="w-8 h-8 text-red-400" />
              </div>
              <p className="text-red-400 text-lg font-medium">Failed to load tasks</p>
              <p className="text-gray-500 text-sm mt-2">Please try refreshing the page</p>
            </div>
          ) : tasks.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-4 animate-in fade-in duration-500">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500/10 to-purple-500/10 flex items-center justify-center mb-6">
                <ListTodo className="w-12 h-12 text-blue-400" />
              </div>
              <h3 className="text-2xl font-semibold text-white mb-2">
                {activeFilter === "completed"
                  ? "No completed tasks yet"
                  : activeFilter === "pending"
                  ? "No pending tasks"
                  : "No tasks yet"}
              </h3>
              <p className="text-gray-400 text-base mb-6 max-w-md">
                {activeFilter === "all"
                  ? "Start organizing your life by creating your first task"
                  : activeFilter === "pending"
                  ? "All caught up! No pending tasks at the moment"
                  : "Complete some tasks to see them here"}
              </p>
              {activeFilter !== "completed" && (
                <Button
                  onClick={() => setIsAddModalOpen(true)}
                  className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 gap-2 shadow-lg shadow-blue-500/20"
                >
                  <Plus className="w-4 h-4" />
                  Create your first task
                </Button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 animate-in fade-in duration-300">
              {tasks.map((task, index) => (
                <div
                  key={task.id}
                  className="animate-in fade-in slide-in-from-bottom-4"
                  style={{ animationDelay: `${index * 50}ms`, animationFillMode: "backwards" }}
                >
                  <TaskCard
                    task={task}
                    onEdit={setEditingTask}
                    onDelete={setDeletingTask}
                  />
                </div>
              ))}
            </div>
          )}
        </main>
      </div>

      {/* Modals */}
      <AddTaskModal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} />
      <EditTaskModal
        isOpen={editingTask !== null}
        task={editingTask}
        onClose={() => setEditingTask(null)}
      />
      <DeleteConfirmDialog
        isOpen={deletingTask !== null}
        task={deletingTask}
        onClose={() => setDeletingTask(null)}
      />
    </div>
  )
}
