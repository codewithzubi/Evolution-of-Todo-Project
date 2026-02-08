// [Task]: T050, [From]: specs/002-task-ui-frontend/spec.md#US2
// TaskItem component for displaying individual task in list format

'use client';

import type { Task } from '@/types/task';
import { format } from 'date-fns';

interface TaskItemProps {
  task: Task;
  onComplete?: (taskId: string) => void;
  onEdit?: (taskId: string) => void;
  onDelete?: (taskId: string) => void;
  isCompletingId?: string;
}

/**
 * TaskItem Component
 * Displays a single task with title, description preview, due date, and action buttons
 * [Task]: T050, [From]: specs/002-task-ui-frontend/spec.md#US2
 *
 * @param task - Task object to display
 * @param onComplete - Callback when complete checkbox is clicked
 * @param onEdit - Callback when edit button is clicked
 * @param onDelete - Callback when delete button is clicked
 * @param isCompletingId - ID of task currently being marked complete
 *
 * @example
 * <TaskItem
 *   task={task}
 *   onComplete={handleComplete}
 *   onEdit={handleEdit}
 *   onDelete={handleDelete}
 * />
 */
export function TaskItem({
  task,
  onComplete,
  onEdit,
  onDelete,
  isCompletingId,
}: TaskItemProps): React.ReactNode {
  const isCompleting = isCompletingId === task.id;
  const dueDate = task.dueDate ? new Date(task.dueDate) : null;
  const isDueSoon = dueDate && dueDate < new Date() && !task.completed;

  return (
    <div
      className={`
        group flex gap-3 sm:gap-4 items-start p-4 sm:p-5 rounded-lg border-2
        transition-all duration-200
        ${
          task.completed
            ? 'bg-gray-50 border-gray-200 hover:border-gray-300'
            : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-sm'
        }
      `}
    >
      {/* Checkbox - Improved Interaction */}
      <button
        type="button"
        onClick={() => onComplete?.(task.id)}
        disabled={isCompleting}
        aria-label={task.completed ? 'Mark task incomplete' : 'Mark task complete'}
        className={`
          flex-shrink-0 mt-0.5 p-1 rounded transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-offset-2
          ${task.completed ? 'focus:ring-green-500' : 'focus:ring-blue-500'}
          ${isCompleting ? 'cursor-wait' : 'cursor-pointer'}
        `}
      >
        <div
          className={`
            w-6 h-6 rounded-md border-2 flex items-center justify-center
            transition-all duration-200
            ${
              task.completed
                ? 'bg-green-500 border-green-500 shadow-sm'
                : 'border-gray-300 hover:border-blue-400 hover:shadow-sm'
            }
            ${isCompleting ? 'opacity-70' : ''}
          `}
        >
          {task.completed && (
            <svg
              className="w-4 h-4 text-white animate-in fade-in duration-200"
              fill="currentColor"
              viewBox="0 0 20 20"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </div>
      </button>

      {/* Task Content */}
      <div className="flex-1 min-w-0">
        {/* Title */}
        <h3
          className={`
            font-medium text-base leading-snug mb-1
            transition-all duration-200
            ${
              task.completed
                ? 'line-through text-gray-400'
                : 'text-gray-900 group-hover:text-gray-800'
            }
          `}
        >
          {task.title}
        </h3>

        {/* Description Preview */}
        {task.description && (
          <p
            className={`
              text-sm leading-relaxed mb-2 line-clamp-2
              transition-colors duration-200
              ${task.completed ? 'text-gray-400' : 'text-gray-600'}
            `}
          >
            {task.description}
          </p>
        )}

        {/* Meta Information - Improved Layout */}
        <div className="flex flex-wrap gap-2 sm:gap-3 text-xs leading-relaxed items-center">
          {/* Priority Badge */}
          {task.priority && (
            <span
              className={`
                px-2.5 py-1 rounded-full font-medium transition-colors duration-200
                ${
                  task.priority === 'low'
                    ? 'bg-green-100 text-green-700'
                    : task.priority === 'high'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-gray-100 text-gray-700'
                }
              `}
            >
              {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
            </span>
          )}

          {/* Due Date Badge */}
          {dueDate && (
            <span
              className={`
                px-2 py-1 rounded-full transition-colors duration-200
                ${
                  isDueSoon
                    ? 'bg-red-100 text-red-700 font-medium'
                    : task.completed
                      ? 'bg-gray-100 text-gray-500'
                      : 'bg-blue-50 text-blue-700'
                }
              `}
            >
              Due {format(dueDate, 'MMM d')}
            </span>
          )}

          {/* Created Date */}
          <span
            className={`
              text-gray-500 transition-colors duration-200
              ${task.completed ? 'text-gray-400' : ''}
            `}
          >
            Created {format(new Date(task.createdAt), 'MMM d, yyyy')}
          </span>

          {/* Completed Badge */}
          {task.completed && task.completedAt && (
            <span className="px-2 py-1 rounded-full bg-green-100 text-green-700 font-medium">
              Completed {format(new Date(task.completedAt), 'MMM d, yyyy')}
            </span>
          )}
        </div>

        {/* Tags Section - Display below meta information */}
        {task.tags && task.tags.trim() && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {task.tags.split(',').map((tag) => {
              const trimmedTag = tag.trim();
              return trimmedTag ? (
                <span
                  key={trimmedTag}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-700 transition-colors duration-200"
                >
                  #{trimmedTag}
                </span>
              ) : null;
            })}
          </div>
        )}
      </div>

      {/* Action Buttons - Improved Layout */}
      <div className="flex gap-1.5 sm:gap-2 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <button
          type="button"
          onClick={() => onEdit?.(task.id)}
          disabled={isCompleting}
          aria-label={`Edit ${task.title}`}
          title="Edit task"
          className={`
            px-3 py-1.5 text-sm font-medium rounded-md
            transition-all duration-200
            text-blue-600 hover:bg-blue-50
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
            ${isCompleting ? 'opacity-50 cursor-not-allowed' : 'hover:text-blue-700'}
          `}
        >
          Edit
        </button>
        <button
          type="button"
          onClick={() => onDelete?.(task.id)}
          disabled={isCompleting}
          aria-label={`Delete ${task.title}`}
          title="Delete task"
          className={`
            px-3 py-1.5 text-sm font-medium rounded-md
            transition-all duration-200
            text-red-600 hover:bg-red-50
            focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2
            ${isCompleting ? 'opacity-50 cursor-not-allowed' : 'hover:text-red-700'}
          `}
        >
          Delete
        </button>
      </div>
    </div>
  );
}
