// [Task]: T048, [From]: specs/002-task-ui-frontend/spec.md#US2
// Custom React Query hooks for task management with proper typing and error handling

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { taskService } from '@/services/task.service';
import type { CreateTaskRequest, UpdateTaskRequest } from '@/types/task';

/**
 * Query keys for React Query cache management
 */
const taskQueryKeys = {
  all: ['tasks'] as const,
  lists: () => [...taskQueryKeys.all, 'list'] as const,
  list: (userId: string, page: number, limit: number) =>
    [...taskQueryKeys.lists(), { userId, page, limit }] as const,
  details: () => [...taskQueryKeys.all, 'detail'] as const,
  detail: (userId: string, taskId: string) =>
    [...taskQueryKeys.details(), { userId, taskId }] as const,
};

/**
 * Hook to fetch paginated list of tasks
 * [Task]: T048, [From]: specs/002-task-ui-frontend/spec.md#US2
 *
 * @param userId - The user ID
 * @param page - Current page number (1-based)
 * @param limit - Items per page (default: 10)
 * @returns useQuery result with tasks, loading state, error state, and refetch function
 *
 * @example
 * const { data, isLoading, error, refetch } = useTasks(userId, 1, 10);
 */
export function useTasks(userId: string, page: number = 1, limit: number = 10) {
  return useQuery({
    queryKey: taskQueryKeys.list(userId, page, limit),
    queryFn: () => taskService.getTasks(userId, page, limit),
    enabled: !!userId,
    staleTime: 1000 * 60, // 1 minute
  });
}

/**
 * Hook to fetch a single task by ID
 * [Task]: T048, [From]: specs/002-task-ui-frontend/spec.md#US2
 *
 * @param userId - The user ID
 * @param taskId - The task ID
 * @returns useQuery result with task data and loading/error states
 *
 * @example
 * const { data: task, isLoading, error } = useTaskDetail(userId, taskId);
 */
export function useTaskDetail(userId: string, taskId: string) {
  return useQuery({
    queryKey: taskQueryKeys.detail(userId, taskId),
    queryFn: () => taskService.getTask(userId, taskId),
    enabled: !!userId && !!taskId,
  });
}

/**
 * Hook to create a new task
 * [Task]: T048, [From]: specs/002-task-ui-frontend/spec.md#US2
 *
 * @param userId - The user ID
 * @returns useMutation result with mutate function and loading/error states
 *
 * @example
 * const { mutate: createTask, isPending } = useCreateTask(userId);
 * createTask({ title: 'New Task', description: 'Details' });
 */
export function useCreateTask(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateTaskRequest) => taskService.createTask(userId, data),
    onSuccess: () => {
      // Invalidate all task lists for this user to trigger refetch
      queryClient.invalidateQueries({
        queryKey: taskQueryKeys.lists(),
      });
    },
    onError: (error) => {
      console.error('Failed to create task:', error);
    },
  });
}

/**
 * Hook to update an existing task
 * [Task]: T048, [From]: specs/002-task-ui-frontend/spec.md#US2
 *
 * @param userId - The user ID
 * @returns useMutation result with mutate function
 *
 * @example
 * const { mutate: updateTask, isPending } = useUpdateTask(userId);
 * updateTask({ taskId: '123', data: { title: 'Updated Title' } });
 */
export function useUpdateTask(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      taskId,
      data,
    }: {
      taskId: string;
      data: UpdateTaskRequest;
    }) => taskService.updateTask(userId, taskId, data),
    onSuccess: (updatedTask) => {
      // Update specific task detail in cache
      queryClient.setQueryData(
        taskQueryKeys.detail(userId, updatedTask.id),
        updatedTask
      );

      // Invalidate all task lists to trigger refetch
      queryClient.invalidateQueries({
        queryKey: taskQueryKeys.lists(),
      });
    },
    onError: (error) => {
      console.error('Failed to update task:', error);
    },
  });
}

/**
 * Hook to delete a task
 * [Task]: T048, [From]: specs/002-task-ui-frontend/spec.md#US2
 *
 * @param userId - The user ID
 * @returns useMutation result with mutate function
 *
 * @example
 * const { mutate: deleteTask, isPending } = useDeleteTask(userId);
 * deleteTask(taskId);
 */
export function useDeleteTask(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => taskService.deleteTask(userId, taskId),
    onSuccess: () => {
      // Invalidate all task lists to trigger refetch
      queryClient.invalidateQueries({
        queryKey: taskQueryKeys.lists(),
      });
    },
    onError: (error) => {
      console.error('Failed to delete task:', error);
    },
  });
}

/**
 * Hook to toggle task completion status
 * [Task]: T048, [From]: specs/002-task-ui-frontend/spec.md#US2
 *
 * @param userId - The user ID
 * @returns useMutation result with mutate function
 *
 * @example
 * const { mutate: toggleComplete, isPending } = useToggleTaskComplete(userId);
 * toggleComplete(taskId);
 */
export function useToggleTaskComplete(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => taskService.toggleTaskComplete(userId, taskId),
    onSuccess: (updatedTask) => {
      // Update specific task detail in cache
      queryClient.setQueryData(
        taskQueryKeys.detail(userId, updatedTask.id),
        updatedTask
      );

      // Invalidate all task lists to trigger refetch
      queryClient.invalidateQueries({
        queryKey: taskQueryKeys.lists(),
      });
    },
    onError: (error) => {
      console.error('Failed to toggle task completion:', error);
    },
  });
}
