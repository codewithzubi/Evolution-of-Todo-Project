/**
 * Task API client functions
 * All requests are automatically authenticated via apiClient
 */

import { api } from "@/lib/api-client"

/**
 * Task response from backend
 */
export interface Task {
  id: number
  user_id: string
  title: string
  description: string | null
  due_date: string | null  // ISO date string (YYYY-MM-DD)
  priority: "high" | "medium" | "low"
  tags: string | null  // comma-separated
  is_completed: boolean
  created_at: string
  updated_at: string
}

/**
 * Create task request payload
 */
export interface CreateTaskPayload {
  title: string
  description?: string
  due_date?: string  // ISO date string (YYYY-MM-DD)
  priority?: "high" | "medium" | "low"
  tags?: string  // comma-separated
}

/**
 * Update task request payload
 */
export interface UpdateTaskPayload {
  title?: string
  description?: string
  due_date?: string  // ISO date string (YYYY-MM-DD)
  priority?: "high" | "medium" | "low"
  tags?: string  // comma-separated
}

/**
 * Fetch all tasks for current user
 * Supports optional status filtering
 */
export async function fetchTasks(status: "all" | "pending" | "completed" = "all"): Promise<Task[]> {
  return api.get<Task[]>(`/api/tasks?status=${status}`)
}

/**
 * Create a new task
 */
export async function createTask(payload: CreateTaskPayload): Promise<Task> {
  return api.post<Task>("/api/tasks", payload)
}

/**
 * Toggle task completion status
 */
export async function toggleTask(taskId: number): Promise<Task> {
  return api.patch<Task>(`/api/tasks/${taskId}/toggle`, {})
}

/**
 * Update task title and/or description
 */
export async function updateTask(taskId: number, payload: UpdateTaskPayload): Promise<Task> {
  return api.put<Task>(`/api/tasks/${taskId}`, payload)
}

/**
 * Delete a task
 */
export async function deleteTask(taskId: number): Promise<{ message: string }> {
  return api.delete<{ message: string }>(`/api/tasks/${taskId}`)
}
