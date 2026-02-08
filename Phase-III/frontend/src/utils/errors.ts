// [Task]: T-005, [From]: specs/002-task-ui-frontend/spec.md#FR-013
// Error handling and parsing utilities

import { ApiError, ApiErrorCode } from '@/types/api';

/**
 * Get user-friendly error message from ApiError
 */
export function getUserFriendlyErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    // Map specific error codes to user-friendly messages
    switch (error.code) {
      case ApiErrorCode.NETWORK_ERROR:
        return 'Network error. Please check your connection and try again.';
      case ApiErrorCode.TIMEOUT:
        return 'Request timed out. Please try again.';
      case ApiErrorCode.UNAUTHORIZED:
        return 'Your session has expired. Please log in again.';
      case ApiErrorCode.FORBIDDEN:
        return 'You do not have permission to perform this action.';
      case ApiErrorCode.NOT_FOUND:
        return 'The requested resource was not found.';
      case ApiErrorCode.VALIDATION_ERROR:
        return `Invalid input: ${error.message}`;
      case ApiErrorCode.SERVER_ERROR:
        return 'A server error occurred. Please try again later.';
      default:
        return error.message || 'An unknown error occurred.';
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'An unknown error occurred. Please try again.';
}

/**
 * Check if error is authentication-related (401)
 */
export function isAuthenticationError(error: unknown): boolean {
  if (error instanceof ApiError) {
    return error.code === ApiErrorCode.UNAUTHORIZED || error.status === 401;
  }
  return false;
}

/**
 * Check if error is authorization-related (403)
 */
export function isAuthorizationError(error: unknown): boolean {
  if (error instanceof ApiError) {
    return error.code === ApiErrorCode.FORBIDDEN || error.status === 403;
  }
  return false;
}

/**
 * Check if error is network-related
 */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof ApiError) {
    return error.code === ApiErrorCode.NETWORK_ERROR;
  }
  return false;
}

/**
 * Check if error is validation-related
 */
export function isValidationError(error: unknown): boolean {
  if (error instanceof ApiError) {
    return error.code === ApiErrorCode.VALIDATION_ERROR || error.status === 400;
  }
  return false;
}

/**
 * Extract validation errors from API response
 */
export function extractValidationErrors(
  error: unknown
): Record<string, string> | null {
  if (error instanceof ApiError && error.details) {
    const details = error.details as Record<string, unknown>;
    if (details.fields && typeof details.fields === 'object') {
      return details.fields as Record<string, string>;
    }
  }
  return null;
}

/**
 * Log error for debugging
 */
export function logError(
  context: string,
  error: unknown,
  shouldThrow: boolean = false
): void {
  if (process.env.NEXT_PUBLIC_ENABLE_DEBUG_MODE === 'true') {
    console.error(`[${context}]`, error);
  }

  if (shouldThrow) {
    throw error;
  }
}
