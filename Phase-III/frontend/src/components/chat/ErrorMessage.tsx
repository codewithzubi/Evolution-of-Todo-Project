// [Task]: T356, T357, [From]: specs/004-ai-chatbot/spec.md
// ErrorMessage Component - Error display with retry button

'use client';

interface ErrorMessageProps {
  error: string;
  isDarkMode: boolean;
  onRetry?: () => void;
  onDismiss?: () => void;
}

/**
 * ErrorMessage Component
 * Displays error with optional retry and dismiss buttons
 */
export function ErrorMessage({
  error,
  isDarkMode,
  onRetry,
  onDismiss
}: ErrorMessageProps) {
  return (
    <div
      role="alert"
      className={`px-4 py-3 rounded-lg border-l-4 ${
        isDarkMode
          ? 'border-red-500 bg-red-900/20 text-red-200'
          : 'border-red-500 bg-red-50 text-red-900'
      }`}
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex-1">
          <p className="text-sm font-medium">{error}</p>
        </div>
        <div className="flex gap-2 whitespace-nowrap">
          {onRetry && (
            <button
              onClick={onRetry}
              className="text-sm px-2 py-1 rounded hover:underline transition-colors"
              aria-label="Retry"
            >
              Retry
            </button>
          )}
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="text-sm px-2 py-1 rounded hover:underline transition-colors"
              aria-label="Dismiss error"
            >
              Dismiss
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
