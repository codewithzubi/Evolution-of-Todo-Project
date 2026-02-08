// [Task]: T024, [From]: specs/002-task-ui-frontend/spec.md#FR-006
// Form component collection for structured form inputs

'use client';

import { InputHTMLAttributes, TextareaHTMLAttributes, ReactNode } from 'react';
import { Input } from './Input';

// FormInput component - wrapper around Input for consistent form styling
export interface FormInputProps extends InputHTMLAttributes<HTMLInputElement> {
  /**
   * Label displayed above input
   */
  label?: string;

  /**
   * Error message displayed below input
   */
  error?: string | null;

  /**
   * Help text displayed below label
   */
  helperText?: ReactNode;

  /**
   * Container class for styling
   */
  containerClassName?: string;
}

/**
 * Form input component with label, error, and helper text
 *
 * @example
 * <FormInput
 *   label="Email"
 *   type="email"
 *   value={email}
 *   onChange={(e) => setEmail(e.target.value)}
 *   error={emailError}
 * />
 */
export function FormInput({
  label,
  error,
  helperText,
  containerClassName = '',
  ...props
}: FormInputProps) {
  return (
    <Input
      label={label}
      error={error}
      helperText={helperText}
      className={containerClassName}
      {...props}
    />
  );
}

// FormTextarea component
export interface FormTextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  /**
   * Label displayed above textarea
   */
  label?: string;

  /**
   * Error message displayed below textarea
   */
  error?: string | null;

  /**
   * Help text displayed below label
   */
  helperText?: ReactNode;

  /**
   * Number of visible rows
   */
  rows?: number;

  /**
   * Container class for styling
   */
  containerClassName?: string;
}

/**
 * Form textarea component with label, error, and helper text
 *
 * @example
 * <FormTextarea
 *   label="Description"
 *   value={description}
 *   onChange={(e) => setDescription(e.target.value)}
 *   rows={4}
 *   error={descError}
 * />
 */
export function FormTextarea({
  label,
  error,
  helperText,
  rows = 3,
  disabled = false,
  containerClassName = '',
  ...props
}: FormTextareaProps) {
  const textareaId = props.id || `textarea-${Math.random().toString(36).substr(2, 9)}`;

  const textareaStyles = `px-3 py-2 border rounded-md w-full text-base transition-colors duration-200 resize-vertical min-h-24 ${
    error
      ? 'border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 bg-red-50'
      : 'border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white'
  } ${disabled ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : ''}`;

  return (
    <div className={`w-full ${containerClassName}`}>
      {label && (
        <label
          htmlFor={textareaId}
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {label}
        </label>
      )}
      {helperText && (
        <p className="text-xs text-gray-500 mb-2">{helperText}</p>
      )}
      <textarea
        id={textareaId}
        className={textareaStyles}
        rows={rows}
        disabled={disabled}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600 mt-1">{error}</p>
      )}
    </div>
  );
}

// FormDatePicker component
export interface FormDatePickerProps extends InputHTMLAttributes<HTMLInputElement> {
  /**
   * Label displayed above date picker
   */
  label?: string;

  /**
   * Error message displayed below date picker
   */
  error?: string | null;

  /**
   * Help text displayed below label
   */
  helperText?: ReactNode;

  /**
   * Minimum date in ISO format (YYYY-MM-DD)
   */
  min?: string;

  /**
   * Maximum date in ISO format (YYYY-MM-DD)
   */
  max?: string;

  /**
   * Container class for styling
   */
  containerClassName?: string;
}

/**
 * Form date picker component with label, error, and constraints
 *
 * @example
 * <FormDatePicker
 *   label="Due Date"
 *   value={dueDate}
 *   onChange={(e) => setDueDate(e.target.value)}
 *   min={today}
 *   error={dueDateError}
 * />
 */
export function FormDatePicker({
  label,
  error,
  helperText,
  min,
  max,
  containerClassName = '',
  disabled = false,
  ...props
}: FormDatePickerProps) {
  const dateId = props.id || `date-${Math.random().toString(36).substr(2, 9)}`;

  const dateStyles = `px-3 py-2 md:py-3 border rounded-md min-h-12 w-full text-base transition-colors duration-200 ${
    error
      ? 'border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 bg-red-50'
      : 'border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white'
  } ${disabled ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : ''}`;

  return (
    <div className={`w-full ${containerClassName}`}>
      {label && (
        <label
          htmlFor={dateId}
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {label}
        </label>
      )}
      {helperText && (
        <p className="text-xs text-gray-500 mb-2">{helperText}</p>
      )}
      <input
        id={dateId}
        type="date"
        className={dateStyles}
        min={min}
        max={max}
        disabled={disabled}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600 mt-1">{error}</p>
      )}
    </div>
  );
}
