// [Task]: T054, [From]: specs/002-task-ui-frontend/spec.md#US2
// TaskListSkeleton component for displaying loading state

'use client';

/**
 * TaskListSkeleton Component
 * Displays animated skeleton loaders while task list is loading
 * [Task]: T054, [From]: specs/002-task-ui-frontend/spec.md#US2
 *
 * @example
 * <TaskListSkeleton />
 */
export function TaskListSkeleton(): React.ReactNode {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, index) => (
        <div
          key={index}
          className="flex gap-4 items-start rounded-lg border border-gray-200 p-4 bg-white animate-pulse"
        >
          {/* Checkbox skeleton */}
          <div className="w-6 h-6 bg-gray-300 rounded flex-shrink-0 mt-1" />

          {/* Content skeleton */}
          <div className="flex-1 min-w-0 space-y-2">
            <div className="h-5 bg-gray-300 rounded w-2/3" />
            <div className="h-4 bg-gray-200 rounded w-full" />
            <div className="flex gap-3">
              <div className="h-3 bg-gray-200 rounded w-32" />
              <div className="h-3 bg-gray-200 rounded w-32" />
            </div>
          </div>

          {/* Actions skeleton */}
          <div className="flex gap-2 flex-shrink-0">
            <div className="h-8 w-16 bg-gray-300 rounded" />
            <div className="h-8 w-16 bg-gray-300 rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}
