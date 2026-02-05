// [Task]: T051, [From]: specs/002-task-ui-frontend/spec.md#US2
// TaskList component for rendering list of tasks with pagination integration

'use client';

import { TaskItem } from './TaskItem';
import { TaskListSkeleton } from './TaskListSkeleton';
import { EmptyState } from './EmptyState';
import { Pagination } from '@/components/common/Pagination';
import type { Task } from '@/types/task';

interface TaskListProps {
  tasks: Task[];
  isLoading: boolean;
  error: Error | null;
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onComplete?: (taskId: string) => void;
  onEdit?: (taskId: string) => void;
  onDelete?: (taskId: string) => void;
  onRetry?: () => void;
  isCompletingId?: string;
}

/**
 * TaskList Component
 * Renders a paginated list of tasks with loading and error states
 * [Task]: T051, [From]: specs/002-task-ui-frontend/spec.md#US2
 *
 * @param tasks - Array of tasks to display
 * @param isLoading - Whether data is loading
 * @param error - Error object if fetch failed
 * @param currentPage - Current page number
 * @param totalPages - Total number of pages
 * @param onPageChange - Callback when page changes
 * @param onComplete - Callback when task is marked complete
 * @param onEdit - Callback when edit is clicked
 * @param onDelete - Callback when delete is clicked
 * @param onRetry - Callback when retry is clicked
 * @param isCompletingId - ID of task being marked complete
 *
 * @example
 * <TaskList
 *   tasks={tasks}
 *   isLoading={isLoading}
 *   error={error}
 *   currentPage={page}
 *   totalPages={Math.ceil(total / 10)}
 *   onPageChange={setPage}
 * />
 */
export function TaskList({
  tasks,
  isLoading,
  error,
  currentPage,
  totalPages,
  onPageChange,
  onComplete,
  onEdit,
  onDelete,
  onRetry,
  isCompletingId,
}: TaskListProps): React.ReactNode {
  // Loading state
  if (isLoading) {
    return <TaskListSkeleton />;
  }

  // Error state
  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6">
        <div className="flex items-start gap-4">
          <div>
            <svg
              className="w-6 h-6 text-red-600 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-red-900 mb-1">Failed to load tasks</h3>
            <p className="text-sm text-red-700 mb-4">
              {error instanceof Error ? error.message : 'An error occurred while fetching tasks'}
            </p>
            {onRetry && (
              <button
                type="button"
                onClick={onRetry}
                className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700 transition-colors"
              >
                Try Again
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Empty state
  if (tasks.length === 0) {
    return <EmptyState />;
  }

  // Task list
  return (
    <div className="space-y-4 sm:space-y-5">
      {/* Task Count Header */}
      <div className="flex items-center justify-between px-1">
        <p className="text-sm text-gray-600">
          {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'} on this page
        </p>
      </div>

      {/* Tasks Container */}
      <div className="space-y-2.5 sm:space-y-3">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onComplete={onComplete}
            onEdit={onEdit}
            onDelete={onDelete}
            isCompletingId={isCompletingId}
          />
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={onPageChange}
            isLoading={false}
          />
        </div>
      )}
    </div>
  );
}
