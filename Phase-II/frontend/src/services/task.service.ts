// [Task]: T046, [From]: specs/002-task-ui-frontend/spec.md#US2
// Task service for handling task CRUD operations with API communication

import { apiClient } from './api';
import type {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
} from '@/types/task';

/**
 * Convert snake_case backend response to camelCase for frontend
 */
function transformTask(rawTask: any): Task {
  return {
    id: rawTask.id,
    userId: rawTask.user_id,
    title: rawTask.title,
    description: rawTask.description,
    dueDate: rawTask.due_date,
    priority: rawTask.priority || 'medium',
    tags: rawTask.tags,
    completed: rawTask.completed,
    completedAt: rawTask.completed_at,
    createdAt: rawTask.created_at,
    updatedAt: rawTask.updated_at,
  };
}

/**
 * Task Service
 * Handles all task-related API operations with proper error handling and typing
 * [Task]: T046, [From]: specs/002-task-ui-frontend/spec.md#US2
 */
class TaskService {
  private readonly API_BASE_PATH = '/api';

  /**
   * Fetch paginated list of tasks for a user
   * @param userId - The user ID
   * @param page - Page number (1-based)
   * @param limit - Items per page (default: 10)
   * @returns Promise resolving to paginated task list
   */
  async getTasks(
    userId: string,
    page: number = 1,
    limit: number = 10
  ): Promise<{
    tasks: Task[];
    total: number;
    page: number;
    pageSize: number;
    hasMore: boolean;
  }> {
    try {
      const offset = (page - 1) * limit;
      const response = await apiClient.get<{
        data: {
          items: Task[];
          pagination: {
            limit: number;
            offset: number;
            total: number;
            has_more: boolean;
          };
        };
        error: null;
      }>(
        `${this.API_BASE_PATH}/${userId}/tasks`,
        {
          params: {
            offset,
            limit,
          },
        }
      );

      // Transform backend response to match frontend expectations
      return {
        tasks: response.data.items.map(transformTask),
        total: response.data.pagination.total,
        page,
        pageSize: limit,
        hasMore: response.data.pagination.has_more,
      };
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
      throw error;
    }
  }

  /**
   * Fetch a single task by ID
   * @param userId - The user ID
   * @param taskId - The task ID
   * @returns Promise resolving to task data
   */
  async getTask(userId: string, taskId: string): Promise<Task> {
    try {
      const response = await apiClient.get<{ data: any; error: null }>(
        `${this.API_BASE_PATH}/${userId}/tasks/${taskId}`
      );
      return transformTask(response.data);
    } catch (error) {
      console.error(`Failed to fetch task ${taskId}:`, error);
      throw error;
    }
  }

  /**
   * Create a new task
   * @param userId - The user ID
   * @param data - Task creation data
   * @returns Promise resolving to created task
   */
  async createTask(userId: string, data: CreateTaskRequest): Promise<Task> {
    try {
      const response = await apiClient.post<{ data: any; error: null }>(
        `${this.API_BASE_PATH}/${userId}/tasks`,
        data
      );
      return transformTask(response.data);
    } catch (error) {
      console.error('Failed to create task:', error);
      throw error;
    }
  }

  /**
   * Update an existing task
   * @param userId - The user ID
   * @param taskId - The task ID
   * @param data - Task update data
   * @returns Promise resolving to updated task
   */
  async updateTask(
    userId: string,
    taskId: string,
    data: UpdateTaskRequest
  ): Promise<Task> {
    try {
      const response = await apiClient.put<{ data: any; error: null }>(
        `${this.API_BASE_PATH}/${userId}/tasks/${taskId}`,
        data
      );
      return transformTask(response.data);
    } catch (error) {
      console.error(`Failed to update task ${taskId}:`, error);
      throw error;
    }
  }

  /**
   * Delete a task
   * @param userId - The user ID
   * @param taskId - The task ID
   * @returns Promise resolving when task is deleted
   */
  async deleteTask(userId: string, taskId: string): Promise<void> {
    try {
      await apiClient.delete(`${this.API_BASE_PATH}/${userId}/tasks/${taskId}`);
    } catch (error) {
      console.error(`Failed to delete task ${taskId}:`, error);
      throw error;
    }
  }

  /**
   * Toggle task completion status
   * @param userId - The user ID
   * @param taskId - The task ID
   * @returns Promise resolving to updated task with toggled completion status
   */
  async toggleTaskComplete(userId: string, taskId: string): Promise<Task> {
    try {
      const response = await apiClient.patch<{ data: any; error: null }>(
        `${this.API_BASE_PATH}/${userId}/tasks/${taskId}/complete`,
        { completed: true } // Backend toggles regardless of value, but requires this field for validation
      );
      return transformTask(response.data);
    } catch (error) {
      console.error(`Failed to toggle task completion for ${taskId}:`, error);
      throw error;
    }
  }
}

// Export singleton instance
export const taskService = new TaskService();
export type { Task, CreateTaskRequest, UpdateTaskRequest };
