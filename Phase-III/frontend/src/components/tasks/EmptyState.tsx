// [Task]: T053, [From]: specs/002-task-ui-frontend/spec.md#US2
// EmptyState component for displaying when no tasks exist

'use client';

interface EmptyStateProps {
  message?: string;
  actionLabel?: string;
  onAction?: () => void;
}

/**
 * EmptyState Component
 * Displays a friendly message when no tasks exist
 * [Task]: T053, [From]: specs/002-task-ui-frontend/spec.md#US2
 *
 * @param message - Custom message to display (default: no tasks message)
 * @param actionLabel - Label for action button
 * @param onAction - Callback when action button is clicked
 *
 * @example
 * <EmptyState
 *   message="No tasks yet"
 *   actionLabel="Create one"
 *   onAction={handleCreate}
 * />
 */
export function EmptyState({
  message = 'No tasks yet. Create one to get started.',
  actionLabel,
  onAction,
}: EmptyStateProps): React.ReactNode {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      {/* Icon */}
      <div className="mb-4">
        <svg
          className="w-16 h-16 text-gray-300"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
          />
        </svg>
      </div>

      {/* Message */}
      <p className="text-center text-gray-600 text-lg mb-6 max-w-md">
        {message}
      </p>

      {/* Action Button */}
      {actionLabel && onAction && (
        <button
          type="button"
          onClick={onAction}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
