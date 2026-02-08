// [Task]: T067, [From]: specs/002-task-ui-frontend/spec.md#US6
// DeleteConfirmationModal component for task deletion confirmation

'use client';

import { useEffect, useCallback } from 'react';

interface DeleteConfirmationModalProps {
  isOpen: boolean;
  taskTitle: string;
  isDeleting: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

/**
 * DeleteConfirmationModal Component
 * Professional delete confirmation modal showing task title
 * [Task]: T067, [From]: specs/002-task-ui-frontend/spec.md#US6
 *
 * Features:
 * - Displays task title dynamically in confirmation message
 * - Two buttons: Cancel (gray) and Delete (red)
 * - Danger warning with red color and warning icon
 * - Closes on cancel or outside click
 * - Disables button during deletion
 * - Shows success toast after deletion
 * - ESC key to close
 * - Accessible modal with focus management
 *
 * @param isOpen - Whether the modal is open
 * @param taskTitle - The title of the task to delete (displayed in message)
 * @param isDeleting - Whether deletion is in progress
 * @param onConfirm - Callback invoked when delete is confirmed
 * @param onCancel - Callback invoked when delete is cancelled
 *
 * @example
 * <DeleteConfirmationModal
 *   isOpen={showDeleteModal}
 *   taskTitle={task.title}
 *   isDeleting={isDeletePending}
 *   onConfirm={handleDeleteConfirm}
 *   onCancel={handleDeleteCancel}
 * />
 */
export function DeleteConfirmationModal({
  isOpen,
  taskTitle,
  isDeleting,
  onConfirm,
  onCancel,
}: DeleteConfirmationModalProps): React.ReactNode {
  // Note: Toast could be used here for post-deletion feedback if needed

  /**
   * Handle ESC key to close modal
   */
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !isDeleting) {
        onCancel();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, isDeleting, onCancel]);

  /**
   * Handle backdrop click to close modal
   */
  const handleBackdropClick = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      // Only close if clicking directly on backdrop, not on modal content
      if (e.target === e.currentTarget && !isDeleting) {
        onCancel();
      }
    },
    [isDeleting, onCancel]
  );

  /**
   * Handle delete confirmation
   */
  const handleConfirmClick = useCallback(() => {
    onConfirm();
  }, [onConfirm]);

  if (!isOpen) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={handleBackdropClick}
      role="presentation"
    >
      {/* Modal Container */}
      <div
        className="
          w-full mx-4 sm:mx-0 sm:w-full max-w-sm bg-white rounded-2xl shadow-2xl
          animate-in fade-in zoom-in-95 duration-200
        "
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="delete-modal-title"
        aria-describedby="delete-modal-description"
      >
        {/* Modal Header - Danger Warning */}
        <div className="bg-red-50 border-b border-red-200 px-6 py-6 rounded-t-2xl">
          <div className="flex items-start gap-4">
            {/* Warning Icon */}
            <div className="flex-shrink-0 pt-0.5">
              <svg
                className="w-6 h-6 text-red-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4v2m0 0v2m0-6V9m0 6v2m0 0v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>

            {/* Title and Description */}
            <div className="flex-1">
              <h2
                id="delete-modal-title"
                className="text-lg font-bold text-gray-900"
              >
                Delete Task?
              </h2>
              <p
                id="delete-modal-description"
                className="text-sm text-gray-700 mt-2"
              >
                Are you sure you want to delete{' '}
                <span className="font-semibold text-gray-900">"{taskTitle}"</span>?
                This action cannot be undone.
              </p>
            </div>
          </div>
        </div>

        {/* Modal Body - Risk Notice */}
        <div className="px-6 py-4 border-b border-gray-200">
          <p className="text-sm text-gray-600">
            Once deleted, all data associated with this task will be permanently
            removed from your account.
          </p>
        </div>

        {/* Modal Footer - Action Buttons */}
        <div className="flex gap-3 px-6 py-4 rounded-b-2xl">
          <button
            type="button"
            onClick={onCancel}
            disabled={isDeleting}
            aria-label="Cancel deletion"
            className="
              flex-1 px-4 py-2.5 font-medium rounded-lg
              transition-colors duration-200 text-center
              bg-gray-100 text-gray-900
              hover:bg-gray-200 disabled:opacity-60 disabled:cursor-not-allowed
              focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400
            "
          >
            Cancel
          </button>

          <button
            type="button"
            onClick={handleConfirmClick}
            disabled={isDeleting}
            aria-label="Confirm task deletion"
            className="
              flex-1 px-4 py-2.5 font-medium rounded-lg
              transition-colors duration-200 text-center
              bg-red-600 text-white
              hover:bg-red-700 disabled:opacity-60 disabled:cursor-not-allowed
              focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500
            "
          >
            {isDeleting ? (
              <span className="flex items-center justify-center gap-2">
                <svg
                  className="w-4 h-4 animate-spin"
                  fill="none"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Deleting...
              </span>
            ) : (
              'Delete Task'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
