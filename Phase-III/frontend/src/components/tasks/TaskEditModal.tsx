// [Task]: T061, T062, [From]: specs/002-task-ui-frontend/spec.md#US5
// TaskEditModal component for task editing form

'use client';

import { useEffect, useCallback, useRef } from 'react';
import { TaskEditForm } from './TaskEditForm';
import type { Task } from '@/types/task';

interface TaskEditModalProps {
  isOpen: boolean;
  task: Task;
  userId: string;
  onClose: () => void;
  onSuccess?: (task: Task) => void;
}

/**
 * TaskEditModal Component
 * Modal dialog for editing existing tasks with embedded TaskEditForm
 * [Task]: T061, T062, [From]: specs/002-task-ui-frontend/spec.md#US5
 *
 * Features:
 * - Modal opens when isOpen is true
 * - Close button (X) in top-right corner
 * - Click outside (backdrop) to close
 * - Responsive design: full-width on mobile, centered on desktop
 * - Smooth fade animations (fade-in, zoom-in-95)
 * - ESC key to close
 * - Focus trap (keyboard focus stays in modal)
 * - Proper focus restoration on close
 * - Embedded TaskEditForm component
 * - Form submission closes modal and calls onSuccess
 * - Pre-fills form with current task data
 * - ARIA attributes for accessibility
 * - Proper z-index stacking
 *
 * @param isOpen - Whether the modal is open
 * @param task - The task to edit
 * @param userId - The ID of the user editing the task
 * @param onClose - Callback invoked when modal should close
 * @param onSuccess - Optional callback invoked when task is successfully updated
 *
 * @example
 * <TaskEditModal
 *   isOpen={isEditModalOpen}
 *   task={selectedTask}
 *   userId={user.id}
 *   onClose={() => setIsEditModalOpen(false)}
 *   onSuccess={handleTaskUpdated}
 * />
 */
export function TaskEditModal({
  isOpen,
  task,
  userId,
  onClose,
  onSuccess,
}: TaskEditModalProps): React.ReactNode {
  const dialogRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  /**
   * Handle ESC key to close modal and manage focus
   */
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      // Store the currently focused element so we can restore focus later
      previousActiveElement.current = document.activeElement as HTMLElement;

      // Add event listener
      document.addEventListener('keydown', handleEscape);

      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';

      // Focus the modal dialog
      setTimeout(() => {
        if (dialogRef.current) {
          const firstFocusableElement = dialogRef.current.querySelector(
            'input, textarea, button, [tabindex]:not([tabindex="-1"])'
          ) as HTMLElement;
          if (firstFocusableElement) {
            firstFocusableElement.focus();
          }
        }
      }, 0);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';

      // Restore focus to the previously focused element
      if (previousActiveElement.current && !isOpen) {
        setTimeout(() => {
          previousActiveElement.current?.focus();
        }, 0);
      }
    };
  }, [isOpen, onClose]);

  /**
   * Handle backdrop click to close modal
   */
  const handleBackdropClick = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      // Only close if clicking directly on backdrop, not on modal content
      if (e.target === e.currentTarget) {
        onClose();
      }
    },
    [onClose]
  );

  /**
   * Handle successful task update
   */
  const handleSuccess = useCallback(
    (updatedTask: Task) => {
      onClose();
      if (onSuccess) {
        onSuccess(updatedTask);
      }
    },
    [onClose, onSuccess]
  );

  if (!isOpen) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 sm:p-0"
      onClick={handleBackdropClick}
      role="presentation"
      aria-hidden={!isOpen}
    >
      {/* Modal Container */}
      <div
        ref={dialogRef}
        className="
          w-full sm:w-full max-w-md bg-white rounded-2xl shadow-2xl
          max-h-[90vh] overflow-y-auto
          animate-in fade-in zoom-in-95 duration-200
        "
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-modal-title"
      >
        {/* Modal Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-50 to-white border-b border-gray-200 px-6 py-4 flex items-center justify-between rounded-t-2xl">
          <h2
            id="edit-modal-title"
            className="text-lg sm:text-xl font-bold text-gray-900"
          >
            Edit Task
          </h2>

          {/* Close Button */}
          <button
            type="button"
            onClick={onClose}
            aria-label="Close modal"
            title="Close (ESC)"
            className="
              p-2 text-gray-500 hover:text-gray-700
              hover:bg-gray-100 rounded-lg transition-colors
              focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
              flex-shrink-0
            "
          >
            <svg
              className="w-5 h-5 sm:w-6 sm:h-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Modal Body */}
        <div className="px-6 py-6 sm:py-8">
          <TaskEditForm
            task={task}
            userId={userId}
            onSuccess={handleSuccess}
            onCancel={onClose}
            onError={(error) => {
              console.error('Task update error:', error);
            }}
          />
        </div>
      </div>
    </div>
  );
}
