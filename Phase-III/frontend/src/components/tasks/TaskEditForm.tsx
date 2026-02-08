// [Task]: T061, T062, [From]: specs/002-task-ui-frontend/spec.md#US5
// TaskEditForm component with validation for editing existing tasks

'use client';

import { useState, useCallback } from 'react';
import { useUpdateTask } from '@/hooks/useTask';
import { useToast } from '@/components/common/Toast';
import { Input } from '@/components/common/Input';
import type { Task } from '@/types/task';

interface TaskEditFormProps {
  task: Task;
  userId: string;
  onSuccess?: (task: Task) => void;
  onCancel?: () => void;
  onError?: (error: string) => void;
}

interface FormErrors {
  title?: string;
  description?: string;
  dueDate?: string;
  tags?: string;
}

/**
 * TaskEditForm Component
 * Form for editing existing tasks with validation for title, description, and due date
 * [Task]: T061, T062, [From]: specs/002-task-ui-frontend/spec.md#US5
 *
 * Features:
 * - Pre-filled with current task data
 * - Required title field (1-255 characters)
 * - Optional description field (max 2000 characters)
 * - Optional due date picker with past date warning
 * - Real-time validation with inline error messages
 * - Character count display for description
 * - Submit button disabled during submission or invalid state
 * - Detects unchanged fields and doesn't submit if no changes
 * - Success toast notification
 * - Error toast notification
 * - Cancel button to discard changes
 *
 * @param task - The task object being edited
 * @param userId - The ID of the user editing the task
 * @param onSuccess - Optional callback invoked when task is successfully updated
 * @param onCancel - Optional callback invoked when edit is cancelled
 * @param onError - Optional callback for error handling
 *
 * @example
 * <TaskEditForm
 *   task={task}
 *   userId={user.id}
 *   onSuccess={handleTaskUpdated}
 *   onCancel={handleCancel}
 * />
 */
export function TaskEditForm({
  task,
  userId,
  onSuccess,
  onCancel,
  onError,
}: TaskEditFormProps): React.ReactNode {
  const [formData, setFormData] = useState({
    title: task.title,
    description: task.description || '',
    dueDate: task.dueDate || '',
    priority: task.priority || 'medium',
    tags: task.tags || '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const { showToast } = useToast();

  // TanStack Query mutation for updating task
  const { mutate: updateTask, isPending } = useUpdateTask(userId);

  /**
   * Validate title field
   */
  const validateTitle = useCallback((title: string): string | undefined => {
    if (!title || title.trim().length === 0) {
      return 'Title is required';
    }
    if (title.length > 255) {
      return 'Title must be less than 255 characters';
    }
    return undefined;
  }, []);

  /**
   * Validate description field
   */
  const validateDescription = useCallback((description?: string): string | undefined => {
    if (description && description.length > 2000) {
      return 'Description must be less than 2000 characters';
    }
    return undefined;
  }, []);

  /**
   * Validate due date field
   */
  const validateDueDate = useCallback((dueDate?: string): string | undefined => {
    if (!dueDate) {
      return undefined;
    }

    // Validate ISO8601 format (with optional milliseconds)
    const isoRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$/;
    if (!isoRegex.test(dueDate)) {
      return 'Due date must be in valid ISO 8601 format';
    }

    // Check if date is valid
    try {
      const dateObj = new Date(dueDate);
      if (isNaN(dateObj.getTime())) {
        return 'Due date is not a valid date';
      }
    } catch {
      return 'Due date is not a valid date';
    }

    return undefined;
  }, []);

  /**
   * Validate tags field
   */
  const validateTags = useCallback((tags?: string): string | undefined => {
    if (!tags) {
      return undefined;
    }

    if (tags.length > 500) {
      return 'Tags must be less than 500 characters';
    }

    return undefined;
  }, []);

  /**
   * Validate all form fields
   */
  const validateForm = useCallback((): FormErrors => {
    const newErrors: FormErrors = {};

    const titleError = validateTitle(formData.title);
    if (titleError) {
      newErrors.title = titleError;
    }

    const descError = validateDescription(formData.description);
    if (descError) {
      newErrors.description = descError;
    }

    const dateError = validateDueDate(formData.dueDate);
    if (dateError) {
      newErrors.dueDate = dateError;
    }

    const tagsError = validateTags(formData.tags);
    if (tagsError) {
      newErrors.tags = tagsError;
    }

    return newErrors;
  }, [formData, validateTitle, validateDescription, validateDueDate, validateTags]);

  /**
   * Handle field changes with real-time validation
   */
  const handleChange = useCallback((
    field: keyof typeof formData,
    value: string
  ) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));

    // Clear error for this field when user starts typing
    setErrors((prev) => ({
      ...prev,
      [field]: undefined,
    }));
  }, []);

  /**
   * Handle field blur for validation
   */
  const handleBlur = useCallback((field: keyof typeof formData) => {
    let error: string | undefined;

    switch (field) {
      case 'title':
        error = validateTitle(formData.title);
        break;
      case 'description':
        error = validateDescription(formData.description);
        break;
      case 'dueDate':
        error = validateDueDate(formData.dueDate);
        break;
      case 'tags':
        error = validateTags(formData.tags);
        break;
    }

    if (error) {
      setErrors((prev) => ({
        ...prev,
        [field]: error,
      }));
    }
  }, [formData, validateTitle, validateDescription, validateDueDate, validateTags]);

  /**
   * Check if due date is in the past (warning only)
   */
  const isPastDate = useCallback((): boolean => {
    if (!formData.dueDate) {
      return false;
    }
    try {
      const dueDate = new Date(formData.dueDate);
      return dueDate < new Date();
    } catch {
      return false;
    }
  }, [formData.dueDate]);

  /**
   * Check if form has any changes from original task data
   */
  const hasChanges = useCallback((): boolean => {
    return (
      formData.title !== task.title ||
      formData.description !== (task.description || '') ||
      formData.dueDate !== (task.dueDate || '') ||
      formData.priority !== (task.priority || 'medium') ||
      formData.tags !== (task.tags || '')
    );
  }, [formData, task]);

  /**
   * Handle form submission
   */
  const handleSubmit = useCallback(
    (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();

      // Check if there are any changes
      if (!hasChanges()) {
        showToast('No changes to save', 'info');
        return;
      }

      // Validate form
      const formErrors = validateForm();
      if (Object.keys(formErrors).length > 0) {
        setErrors(formErrors);
        return;
      }

      // Update task payload
      const payload = {
        title: formData.title.trim(),
        ...(formData.description && { description: formData.description }),
        ...(formData.dueDate && { dueDate: formData.dueDate }),
        priority: formData.priority || 'medium',
        ...(formData.tags && { tags: formData.tags }),
      };

      // Submit via mutation
      updateTask(
        { taskId: task.id, data: payload },
        {
          onSuccess: (updatedTask) => {
            // Show success notification
            showToast(`Task "${updatedTask.title}" updated successfully`, 'success');

            // Call success callback
            if (onSuccess) {
              onSuccess(updatedTask);
            }
          },
          onError: (error) => {
            const errorMessage =
              error instanceof Error ? error.message : 'Failed to update task';

            // Show error notification
            showToast(errorMessage, 'error');

            // Call error callback if provided
            if (onError) {
              onError(errorMessage);
            }
          },
        }
      );
    },
    [formData, hasChanges, validateForm, updateTask, task, onSuccess, onError, showToast]
  );

  /**
   * Check if form is valid
   */
  const isFormValid = useCallback(() => {
    const formErrors = validateForm();
    return Object.keys(formErrors).length === 0;
  }, [validateForm]);

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Title Input */}
      <div>
        <label
          htmlFor="task-title-edit"
          className="block text-sm font-semibold text-gray-900 mb-1.5"
        >
          Task Title <span className="text-red-500" aria-label="required">*</span>
        </label>
        <Input
          id="task-title-edit"
          type="text"
          placeholder="What needs to be done?"
          value={formData.title}
          onChange={(e) => handleChange('title', e.target.value)}
          onBlur={() => handleBlur('title')}
          error={errors.title}
          required
          disabled={isPending}
          helperText="Keep it concise and descriptive (1-255 characters)"
          maxLength={255}
        />
        {/* Character count for title */}
        {formData.title && (
          <div className="mt-1.5 flex items-center justify-between text-xs">
            <span className="text-gray-500">
              {formData.title.length}/255 characters
            </span>
            {formData.title.length > 220 && (
              <span className="text-yellow-600 font-medium">Approaching limit</span>
            )}
          </div>
        )}
      </div>

      {/* Description Input */}
      <div>
        <label
          htmlFor="task-description-edit"
          className="block text-sm font-semibold text-gray-900 mb-1.5"
        >
          Description <span className="font-normal text-gray-500">(Optional)</span>
        </label>
        <textarea
          id="task-description-edit"
          placeholder="Add more details about this task..."
          value={formData.description}
          onChange={(e) => handleChange('description', e.target.value)}
          onBlur={() => handleBlur('description')}
          disabled={isPending}
          rows={4}
          maxLength={2000}
          className={`
            w-full px-3 py-2 md:py-3 border-2 rounded-lg resize-none
            text-base transition-all duration-200 font-normal
            ${
              errors.description
                ? 'border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 bg-red-50'
                : formData.description
                  ? 'border-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-blue-50/30'
                  : 'border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-white'
            }
            ${isPending ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : ''}
          `}
        />
        {errors.description && (
          <p className="text-sm text-red-600 mt-1.5 font-medium">{errors.description}</p>
        )}
        {formData.description && (
          <div className="mt-1.5 flex items-center justify-between text-xs">
            <span className="text-gray-500">
              {formData.description.length}/2000 characters
            </span>
            {formData.description.length > 1800 && (
              <span className="text-yellow-600 font-medium">Approaching limit</span>
            )}
          </div>
        )}
      </div>

      {/* Due Date Input */}
      <div>
        <label
          htmlFor="task-dueDate-edit"
          className="block text-sm font-semibold text-gray-900 mb-1.5"
        >
          Due Date <span className="font-normal text-gray-500">(Optional)</span>
        </label>
        <input
          id="task-dueDate-edit"
          type="datetime-local"
          value={formData.dueDate ? formatDateTimeLocal(formData.dueDate) : ''}
          onChange={(e) => {
            const localDateTime = e.target.value;
            if (localDateTime) {
              // Convert from datetime-local to ISO8601
              const isoDate = new Date(localDateTime).toISOString();
              handleChange('dueDate', isoDate);
            } else {
              handleChange('dueDate', '');
            }
          }}
          onBlur={() => handleBlur('dueDate')}
          disabled={isPending}
          className={`
            w-full px-3 py-2 md:py-3 border-2 rounded-lg min-h-12
            text-base transition-all duration-200 font-normal
            ${
              errors.dueDate
                ? 'border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 bg-red-50'
                : formData.dueDate
                  ? 'border-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-blue-50/30'
                  : 'border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-white'
            }
            ${isPending ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : ''}
          `}
        />
        {errors.dueDate && (
          <p className="text-sm text-red-600 mt-1.5 font-medium">{errors.dueDate}</p>
        )}
        {formData.dueDate && isPastDate() && !errors.dueDate && (
          <div className="mt-1.5 p-2 bg-yellow-50 border border-yellow-200 rounded-md flex items-start gap-2">
            <svg className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span className="text-sm text-yellow-800">This due date is in the past. You can still save it if needed.</span>
          </div>
        )}
      </div>

      {/* Priority Select */}
      <div>
        <label
          htmlFor="task-priority-edit"
          className="block text-sm font-semibold text-gray-900 mb-1.5"
        >
          Priority <span className="font-normal text-gray-500">(Optional)</span>
        </label>
        <select
          id="task-priority-edit"
          value={formData.priority || 'medium'}
          onChange={(e) => handleChange('priority', e.target.value as any)}
          disabled={isPending}
          className="
            w-full px-3 py-2 md:py-3 border-2 border-gray-300 rounded-lg min-h-12
            text-base transition-all duration-200 font-normal
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-white
            disabled:bg-gray-100 disabled:text-gray-500 disabled:cursor-not-allowed
          "
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      {/* Tags Input */}
      <div>
        <label
          htmlFor="task-tags-edit"
          className="block text-sm font-semibold text-gray-900 mb-1.5"
        >
          Tags <span className="font-normal text-gray-500">(Optional)</span>
        </label>
        <input
          id="task-tags-edit"
          type="text"
          placeholder="Comma-separated tags (e.g., work,urgent,review)"
          value={formData.tags || ''}
          onChange={(e) => handleChange('tags', e.target.value)}
          onBlur={() => handleBlur('tags')}
          disabled={isPending}
          maxLength={500}
          className={`
            w-full px-3 py-2 md:py-3 border-2 rounded-lg
            text-base transition-all duration-200 font-normal
            ${
              errors.tags
                ? 'border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 bg-red-50'
                : formData.tags
                  ? 'border-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-blue-50/30'
                  : 'border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-white'
            }
            ${isPending ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : ''}
          `}
        />
        {errors.tags && (
          <p className="text-sm text-red-600 mt-1.5 font-medium">{errors.tags}</p>
        )}
        {formData.tags && (
          <div className="mt-1.5 flex items-center justify-between text-xs">
            <span className="text-gray-500">
              {formData.tags.length}/500 characters
            </span>
            {formData.tags.length > 450 && (
              <span className="text-yellow-600 font-medium">Approaching limit</span>
            )}
          </div>
        )}
      </div>

      {/* Form Actions */}
      <div className="flex flex-col-reverse sm:flex-row gap-2 sm:gap-3 mt-8 pt-6 border-t border-gray-200">
        <button
          type="button"
          disabled={isPending}
          onClick={() => {
            // Reset form to original values
            setFormData({
              title: task.title,
              description: task.description || '',
              dueDate: task.dueDate || '',
              priority: task.priority || 'medium',
              tags: task.tags || '',
            });
            setErrors({});
            if (onCancel) {
              onCancel();
            }
          }}
          className={`
            flex-1 px-4 py-2.5 md:py-3 font-medium rounded-lg
            transition-colors duration-200 text-center
            border-2 border-gray-300 text-gray-700
            hover:bg-gray-50 hover:border-gray-400
            disabled:opacity-50 disabled:cursor-not-allowed
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500
          `}
        >
          Cancel
        </button>

        <button
          type="submit"
          disabled={isPending || !isFormValid() || !hasChanges()}
          className={`
            flex-1 px-4 py-2.5 md:py-3 font-semibold rounded-lg
            transition-all duration-200 text-center flex items-center justify-center gap-2
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
            ${
              isPending || !isFormValid() || !hasChanges()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800'
            }
          `}
        >
          {isPending ? (
            <>
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Saving...
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Save Changes
            </>
          )}
        </button>
      </div>
    </form>
  );
}

/**
 * Helper function to format ISO date to datetime-local format
 */
function formatDateTimeLocal(isoDate: string): string {
  try {
    const date = new Date(isoDate);
    const year = date.getUTCFullYear();
    const month = String(date.getUTCMonth() + 1).padStart(2, '0');
    const day = String(date.getUTCDate()).padStart(2, '0');
    const hours = String(date.getUTCHours()).padStart(2, '0');
    const minutes = String(date.getUTCMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  } catch {
    return '';
  }
}
