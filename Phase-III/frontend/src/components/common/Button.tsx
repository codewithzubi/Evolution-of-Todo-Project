// [Task]: T017, [From]: specs/002-task-ui-frontend/spec.md#FR-015
// Button component with multiple variants and states

'use client';

import { ButtonHTMLAttributes, ReactNode } from 'react';

export type ButtonVariant = 'primary' | 'secondary' | 'danger';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * Button label or content
   */
  children: ReactNode;

  /**
   * Visual variant style
   */
  variant?: ButtonVariant;

  /**
   * Show loading spinner and disable interaction
   */
  isLoading?: boolean;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Button component with support for multiple variants and loading states
 *
 * @example
 * <Button variant="primary" onClick={handleClick}>Click me</Button>
 * <Button variant="danger" isLoading>Deleting...</Button>
 */
export function Button({
  children,
  variant = 'primary',
  isLoading = false,
  disabled = false,
  className = '',
  ...props
}: ButtonProps) {
  const baseStyles = 'px-4 py-2 md:py-3 rounded-md font-medium transition-all duration-200 inline-flex items-center justify-center gap-2 min-h-12 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantStyles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 active:bg-gray-400',
    danger: 'bg-red-600 text-white hover:bg-red-700 active:bg-red-800',
  };

  const combinedClassName = `${baseStyles} ${variantStyles[variant]} ${className}`;

  return (
    <button
      disabled={isLoading || disabled}
      className={combinedClassName}
      suppressHydrationWarning
      {...props}
    >
      {isLoading && (
        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      )}
      {children}
    </button>
  );
}
