// [Task]: T020, [From]: specs/002-task-ui-frontend/spec.md#FR-012
// Loading spinner component with optional full-page overlay

'use client';

import { ReactNode } from 'react';

export interface LoadingProps {
  /**
   * Text displayed below spinner
   */
  text?: string;

  /**
   * Show as full-page overlay with dimmed background
   */
  fullPage?: boolean;

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Size of the spinner in pixels
   */
  size?: 'sm' | 'md' | 'lg';

  /**
   * Additional content to display below text
   */
  children?: ReactNode;
}

/**
 * Loading component showing animated spinner
 *
 * @example
 * <Loading text="Loading tasks..." />
 * <Loading fullPage text="Please wait..." />
 */
export function Loading({
  text,
  fullPage = false,
  className = '',
  size = 'md',
  children,
}: LoadingProps) {
  const sizeClasses = {
    sm: 'w-6 h-6 border-2',
    md: 'w-8 h-8 border-2',
    lg: 'w-12 h-12 border-3',
  };

  const spinner = (
    <div className="flex flex-col items-center justify-center gap-3">
      <div
        className={`${sizeClasses[size]} border-blue-600 border-t-transparent rounded-full animate-spin`}
      />
      {text && <p className="text-gray-700 font-medium">{text}</p>}
      {children}
    </div>
  );

  if (fullPage) {
    return (
      <div className="fixed inset-0 bg-white/50 backdrop-blur-sm flex items-center justify-center z-50">
        {spinner}
      </div>
    );
  }

  return <div className={`flex items-center justify-center py-8 ${className}`}>{spinner}</div>;
}
