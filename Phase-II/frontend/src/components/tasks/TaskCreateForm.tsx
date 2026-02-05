// [Task]: T063, T064, T065, [From]: specs/002-task-ui-frontend/spec.md#US3
// TaskCreateForm component with validation for creating new tasks

'use client';

import { useState, useCallback } from 'react';
import { useCreateTask } from '@/hooks/useTask';
import { useToast } from '@/components/common/Toast';
import { Input } from '@/components/common/Input';
import { formatDateTimeLocal } from '@/utils/format';
import type { Task, CreateTaskRequest, TaskPriority } from '@/types/task';

interface TaskCreateFormProps {
  userId: string;
  onSuccess: (task: Task) => void;
  onError?: (error: string) => void;
}

interface FormErrors {
  title?: string;
  description?: string;
  dueDate?: string;
  tags?: string;
}

/**
 * TaskCreateForm Component
 * Form for creating new tasks with validation for title, description, and due date
 * [Task]: T063, T064, T065, [From]: specs/002-task-ui-frontend/spec.md#US3
 *
 * Features:
 * - Required title field (1-255 characters)
 * - Optional description field (max 2000 characters)
 * - Optional due date picker with past date warning
 * - Real-time validation with inline error messages
 * - Character count display for description
 * - Submit button disabled during submission or invalid state
 * - Form resets after successful submission
 * - Success toast notification
 * - Error toast notification
 *
 * @param userId - The ID of the user creating the task
 * @param onSuccess - Callback invoked when task is successfully created
 * @param onError - Optional callback for error handling
 *
 * @example
 * <TaskCreateForm
 *   userId={user.id}
 *   onSuccess={handleTaskCreated}
 *   onError={handleFormError}
 * />
 */
export function TaskCreateForm({
  userId,
  onSuccess,
  onError,
}: TaskCreateFormProps): React.ReactNode {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [priority, setPriority] = useState<TaskPriority>('medium');
  const [tags, setTags] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const { showToast } = useToast();

  // TanStack Query mutation for creating task
  const { mutate: createTask, isPending } = useCreateTask(userId);

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

    const titleError = validateTitle(title);
    if (titleError) {
      newErrors.title = titleError;
    }

    const descError = validateDescription(description);
    if (descError) {
      newErrors.description = descError;
    }

    const dateError = validateDueDate(dueDate);
    if (dateError) {
      newErrors.dueDate = dateError;
    }

    const tagsError = validateTags(tags);
    if (tagsError) {
      newErrors.tags = tagsError;
    }

    return newErrors;
  }, [title, description, dueDate, tags, validateTitle, validateDescription, validateDueDate, validateTags]);

  /**
   * Handle field changes with real-time validation
   */
  const handleChange = useCallback((
    field: keyof CreateTaskRequest,
    value: string
  ) => {
    // Update specific field based on field name
    switch (field) {
      case 'title':
        setTitle(value);
        break;
      case 'description':
        setDescription(value);
        break;
      case 'dueDate':
        setDueDate(value);
        break;
      case 'priority':
        setPriority(value as TaskPriority);
        break;
      case 'tags':
        setTags(value);
        break;
    }

    // Clear error for this field when user starts typing
    setErrors((prev) => ({
      ...prev,
      [field]: undefined,
    }));
  }, []);

  /**
   * Handle field blur for validation
   */
  const handleBlur = useCallback((field: keyof CreateTaskRequest) => {

    let error: string | undefined;

    switch (field) {
      case 'title':
        error = validateTitle(title);
        break;
      case 'description':
        error = validateDescription(description);
        break;
      case 'dueDate':
        error = validateDueDate(dueDate);
        break;
      case 'tags':
        error = validateTags(tags);
        break;
    }

    if (error) {
      setErrors((prev) => ({
        ...prev,
        [field]: error,
      }));
    }
  }, [title, description, dueDate, tags, validateTitle, validateDescription, validateDueDate, validateTags]);

  /**
   * Check if due date is in the past (warning only)
   */
  const isPastDate = useCallback((): boolean => {
    if (!dueDate) {
      return false;
    }
    try {
      const dueDateObj = new Date(dueDate);
      return dueDateObj < new Date();
    } catch {
      return false;
    }
  }, [dueDate]);

  /**
   * Handle form submission
   */
  const handleSubmit = useCallback(
    (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();

      // Validate form
      const formErrors = validateForm();
      if (Object.keys(formErrors).length > 0) {
        setErrors(formErrors);
        return;
      }

      // Create task payload (exclude empty optional fields)
      const payload: CreateTaskRequest = {
        title: title.trim(),
        ...(description && { description }),
        ...(dueDate && { dueDate }),
        priority,
        ...(tags && { tags }),
      };

      // Submit via mutation
      createTask(payload, {
        onSuccess: (task) => {
          // Show success notification
          showToast(`Task "${task.title}" created successfully`, 'success');

          // Reset form
          setTitle('');
          setDescription('');
          setDueDate('');
          setPriority('medium');
          setTags('');
          setErrors({});

          // Call success callback
          onSuccess(task);
        },
        onError: (error) => {
          const errorMessage =
            error instanceof Error ? error.message : 'Failed to create task';

          // Show error notification
          showToast(errorMessage, 'error');

          // Call error callback if provided
          if (onError) {
            onError(errorMessage);
          }
        },
      });
    },
    [title, description, dueDate, priority, tags, validateForm, createTask, onSuccess, onError, showToast]
  );

  /**
   * Check if form is valid
   */
  const isFormValid = useCallback(() => {
    return title.trim().length > 0 && title.length <= 255;
  }, [title]);

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Title Input */}
      <div>
        <label
          htmlFor="task-title"
          className="block text-sm font-semibold text-gray-900 mb-1.5"
        >
          Task Title <span className="text-red-500" aria-label="required">*</span>
        </label>
        <Input
          id="task-title"
          type="text"
          placeholder="What needs to be done?"
          value={title}
          onChange={(e) => handleChange('title', e.target.value)}
          onBlur={() => handleBlur('title')}
          error={errors.title}
          required
          disabled={isPending}
          helperText="Keep it concise and descriptive (1-255 characters)"
          maxLength={255}
        />
        {/* Character count for title */}
        {title && (
          <div className="mt-1.5 flex items-center justify-between text-xs">
            <span className="text-gray-500">
              {title.length}/255 characters
            </span>
            {title.length > 220 && (
              <span className="text-yellow-600 font-medium">Approaching limit</span>
            )}
          </div>
        )}
      </div>

      {/* Description Input */}
      <div>
        <label
          htmlFor="task-description"
          className="block text-sm font-semibold text-gray-900 mb-1.5"
        >
          Description <span className="font-normal text-gray-500">(Optional)</span>
        </label>
        <textarea
          id="task-description"
          placeholder="Add more details about this task..."
          value={description}
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
                : description
                  ? 'border-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-blue-50/30'
                  : 'border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-white'
            }
            ${isPending ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : ''}
          `}
        />
        {errors.description && (
          <p className="text-sm text-red-600 mt-1.5 font-medium">{errors.description}</p>
        )}
        {description && (
          <div className="mt-1.5 flex items-center justify-between text-xs">
            <span className="text-gray-500">
              {description.length}/2000 characters
            </span>
            {description.length > 1800 && (
              <span className="text-yellow-600 font-medium">Approaching limit</span>
            )}
          </div>
        )}
      </div>

      {/* Due Date Input */}
      <div>
        <label
          htmlFor="task-dueDate"
          className="block text-sm font-semibold text-gray-900 mb-1.5"
        >
          Due Date <span className="font-normal text-gray-500">(Optional)</span>
        </label>
        <input
          id="task-dueDate"
          type="datetime-local"
          value={dueDate ? formatDateTimeLocal(dueDate) : ''}
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
                : dueDate
                  ? 'border-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-blue-50/30'
                  : 'border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-white'
            }
            ${isPending ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : ''}
          `}
        />
        {errors.dueDate && (
          <p className="text-sm text-red-600 mt-1.5 font-medium">{errors.dueDate}</p>
        )}
        {dueDate && isPastDate() && !errors.dueDate && (
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
          htmlFor="task-priority"
          className="block text-sm font-semibold text-gray-900 mb-1.5"
        >
          Priority <span className="font-normal text-gray-500">(Optional)</span>
        </label>
        <select
          id="task-priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value as TaskPriority)}
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
          htmlFor="task-tags"
          className="block text-sm font-semibold text-gray-900 mb-1.5"
        >
          Tags <span className="font-normal text-gray-500">(Optional)</span>
        </label>
        <input
          id="task-tags"
          type="text"
          placeholder="Comma-separated tags (e.g., work,urgent,review)"
          value={tags}
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
                : tags
                  ? 'border-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-blue-50/30'
                  : 'border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-white'
            }
            ${isPending ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : ''}
          `}
        />
        {errors.tags && (
          <p className="text-sm text-red-600 mt-1.5 font-medium">{errors.tags}</p>
        )}
        {tags && (
          <div className="mt-1.5 flex items-center justify-between text-xs">
            <span className="text-gray-500">
              {tags.length}/500 characters
            </span>
            {tags.length > 450 && (
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
            // Reset form
            setTitle('');
            setDescription('');
            setDueDate('');
            setPriority('medium');
            setTags('');
            setErrors({});
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
          Clear Form
        </button>

        <button
          type="submit"
          disabled={isPending || !isFormValid()}
          className={`
            flex-1 px-4 py-2.5 md:py-3 font-semibold rounded-lg
            transition-all duration-200 text-center flex items-center justify-center gap-2
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
            ${
              isPending || !isFormValid()
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
              Creating...
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Create Task
            </>
          )}
        </button>
      </div>
    </form>
  );
}
