// [Task]: T019, [From]: specs/002-task-ui-frontend/spec.md#FR-010
// Card component for grouping related content

'use client';

import { ReactNode } from 'react';

export interface CardProps {
  /**
   * Card content
   */
  children: ReactNode;

  /**
   * Optional title displayed in card header
   */
  title?: string;

  /**
   * Optional description displayed in card header
   */
  description?: string;

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Optional click handler for interactive cards
   */
  onClick?: () => void;

  /**
   * Show hover effect for interactive cards
   */
  interactive?: boolean;
}

/**
 * Card component for displaying grouped content with optional header
 *
 * @example
 * <Card title="Task Details" description="View full task information">
 *   <p>Task content here</p>
 * </Card>
 */
export function Card({
  children,
  title,
  description,
  className = '',
  onClick,
  interactive = false,
}: CardProps) {
  const baseStyles = 'bg-white border border-gray-200 rounded-lg shadow-sm p-4 md:p-6';
  const interactiveStyles = interactive
    ? 'cursor-pointer transition-all duration-200 hover:shadow-md hover:border-gray-300'
    : '';

  return (
    <div
      className={`${baseStyles} ${interactiveStyles} ${className}`}
      onClick={onClick}
      role={interactive ? 'button' : undefined}
      tabIndex={interactive ? 0 : undefined}
      onKeyDown={
        interactive
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                onClick?.();
              }
            }
          : undefined
      }
    >
      {(title || description) && (
        <div className="mb-4">
          {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
          {description && (
            <p className="text-sm text-gray-600 mt-1">{description}</p>
          )}
        </div>
      )}
      {children}
    </div>
  );
}
