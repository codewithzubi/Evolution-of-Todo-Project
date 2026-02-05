// [Task]: T-010, [From]: specs/002-task-ui-frontend/spec.md#Key-Entities
// Task-related TypeScript type definitions

export type TaskPriority = 'low' | 'medium' | 'high';

export interface Task {
  id: string;
  userId: string;
  title: string;
  description?: string;
  dueDate?: string; // ISO 8601 format
  priority: TaskPriority;
  tags?: string; // Comma-separated values
  completed: boolean;
  completedAt?: string | null; // ISO 8601 format, nullable
  createdAt: string;
  updatedAt: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  dueDate?: string;
  priority?: TaskPriority;
  tags?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  dueDate?: string;
  priority?: TaskPriority;
  tags?: string;
  completed?: boolean;
}

export interface TaskListResponse {
  data: {
    tasks: Task[];
    total: number;
    page: number;
    pageSize: number;
    hasMore: boolean;
  };
  error: null;
}

export interface TaskResponse {
  data: Task;
  error: null;
}

export interface TaskError {
  data: null;
  error: {
    code: string;
    message: string;
  };
}

export interface PaginationParams {
  page: number;
  limit: number;
  offset?: number;
}

export interface TaskQueryOptions {
  page?: number;
  limit?: number;
  sortBy?: 'createdAt' | 'dueDate' | 'title';
  sortOrder?: 'asc' | 'desc';
}
