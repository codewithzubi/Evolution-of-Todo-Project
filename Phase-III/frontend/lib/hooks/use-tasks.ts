/**
 * TanStack Query hooks for task CRUD operations
 * Handles all server state management and caching
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  fetchTasks,
  createTask,
  toggleTask as toggleTaskAPI,
  updateTask as updateTaskAPI,
  deleteTask as deleteTaskAPI,
  Task,
  CreateTaskPayload,
  UpdateTaskPayload,
} from "@/lib/api/tasks"

/**
 * Query key factory for tasks
 */
const taskQueryKeys = {
  all: ["tasks"],
  status: (status: "all" | "pending" | "completed") => [...taskQueryKeys.all, status],
}

/**
 * Fetch all tasks with optional status filtering
 */
export function useTasksQuery(status: "all" | "pending" | "completed" = "all") {
  return useQuery({
    queryKey: taskQueryKeys.status(status),
    queryFn: () => fetchTasks(status),
  })
}

/**
 * Create a new task
 * Includes optimistic update
 */
export function useCreateTaskMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CreateTaskPayload) => createTask(payload),
    onMutate: async (newTask) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: taskQueryKeys.all })

      // Snapshot the previous value
      const previousTasks = queryClient.getQueryData<Task[]>(taskQueryKeys.all)

      // Optimistically update to the new value
      if (previousTasks) {
        const optimisticTask: Task = {
          id: -1, // Temporary ID
          user_id: "",
          title: newTask.title,
          description: newTask.description || null,
          due_date: newTask.due_date || null,
          priority: newTask.priority || "medium",
          tags: newTask.tags || null,
          is_completed: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }
        queryClient.setQueryData(taskQueryKeys.all, [optimisticTask, ...previousTasks])
      }

      return { previousTasks }
    },
    onSuccess: () => {
      // Invalidate all task queries to refetch
      queryClient.invalidateQueries({ queryKey: taskQueryKeys.all })
    },
    onError: (error, newTask, context) => {
      // Rollback on error
      if (context?.previousTasks) {
        queryClient.setQueryData(taskQueryKeys.all, context.previousTasks)
      }
    },
  })
}

/**
 * Toggle task completion status
 * Includes optimistic update
 */
export function useToggleTaskMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (taskId: number) => toggleTaskAPI(taskId),
    onMutate: async (taskId) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: taskQueryKeys.all })

      // Snapshot previous state
      const previousTasks = queryClient.getQueryData<Task[]>(taskQueryKeys.all)

      // Optimistically update
      if (previousTasks) {
        const updatedTasks = previousTasks.map((task) =>
          task.id === taskId ? { ...task, is_completed: !task.is_completed } : task
        )
        queryClient.setQueryData(taskQueryKeys.all, updatedTasks)
      }

      return { previousTasks }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskQueryKeys.all })
    },
    onError: (error, taskId, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(taskQueryKeys.all, context.previousTasks)
      }
    },
  })
}

/**
 * Update task title and/or description
 * Includes optimistic update
 */
export function useUpdateTaskMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ taskId, payload }: { taskId: number; payload: UpdateTaskPayload }) =>
      updateTaskAPI(taskId, payload),
    onMutate: async ({ taskId, payload }) => {
      await queryClient.cancelQueries({ queryKey: taskQueryKeys.all })

      const previousTasks = queryClient.getQueryData<Task[]>(taskQueryKeys.all)

      if (previousTasks) {
        const updatedTasks = previousTasks.map((task) =>
          task.id === taskId ? { ...task, ...payload, updated_at: new Date().toISOString() } : task
        )
        queryClient.setQueryData(taskQueryKeys.all, updatedTasks)
      }

      return { previousTasks }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskQueryKeys.all })
    },
    onError: (error, variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(taskQueryKeys.all, context.previousTasks)
      }
    },
  })
}

/**
 * Delete a task
 * Includes optimistic update
 */
export function useDeleteTaskMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (taskId: number) => deleteTaskAPI(taskId),
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: taskQueryKeys.all })

      const previousTasks = queryClient.getQueryData<Task[]>(taskQueryKeys.all)

      if (previousTasks) {
        const filteredTasks = previousTasks.filter((task) => task.id !== taskId)
        queryClient.setQueryData(taskQueryKeys.all, filteredTasks)
      }

      return { previousTasks }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskQueryKeys.all })
    },
    onError: (error, taskId, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(taskQueryKeys.all, context.previousTasks)
      }
    },
  })
}
