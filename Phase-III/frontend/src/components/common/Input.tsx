// [Task]: T018, [From]: specs/002-task-ui-frontend/spec.md#FR-006
// Input component with label and error display

'use client';

import { InputHTMLAttributes, ReactNode } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  /**
   * Label displayed above input
   */
  label?: string;

  /**
   * Error message displayed below input
   */
  error?: string | null;

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Help text displayed below label
   */
  helperText?: ReactNode;
}

/**
 * Input component with label, error display, and helper text
 *
 * @example
 * <Input
 *   label="Email"
 *   type="email"
 *   value={email}
 *   onChange={(e) => setEmail(e.target.value)}
 *   error={emailError}
 * />
 */
export function Input({
  label,
  error,
  className = '',
  helperText,
  disabled = false,
  ...props
}: InputProps) {
  const inputId = props.id || `input-${Math.random().toString(36).substr(2, 9)}`;

  const inputStyles = `px-3 py-2 md:py-3 border rounded-md min-h-12 w-full text-base transition-colors duration-200 ${
    error
      ? 'border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 bg-red-50'
      : 'border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white'
  } ${disabled ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : ''}`;

  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {label}
        </label>
      )}
      {helperText && (
        <p className="text-xs text-gray-500 mb-2">{helperText}</p>
      )}
      <input
        id={inputId}
        className={inputStyles}
        disabled={disabled}
        suppressHydrationWarning
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600 mt-1">{error}</p>
      )}
    </div>
  );
}
