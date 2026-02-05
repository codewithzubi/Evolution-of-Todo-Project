// [Task]: T-005, [From]: specs/002-task-ui-frontend/spec.md#FR-018
// Date formatting and text utility functions

import { format as dateFnsFormat, parseISO, isValid } from 'date-fns';

/**
 * Format ISO 8601 date string to user-friendly format
 * Example: "2026-03-15T10:30:00Z" -> "Mar 15, 2026"
 */
export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return '';

  try {
    const date = parseISO(dateString);
    if (!isValid(date)) return '';
    return dateFnsFormat(date, 'MMM d, yyyy');
  } catch {
    return '';
  }
}

/**
 * Format date with time
 * Example: "2026-03-15T10:30:00Z" -> "Mar 15, 2026 10:30 AM"
 */
export function formatDateTime(dateString: string | null | undefined): string {
  if (!dateString) return '';

  try {
    const date = parseISO(dateString);
    if (!isValid(date)) return '';
    return dateFnsFormat(date, 'MMM d, yyyy h:mm a');
  } catch {
    return '';
  }
}

/**
 * Format ISO 8601 date string to relative time
 * Example: "2026-03-15T10:30:00Z" -> "2 days ago"
 */
export function formatRelativeTime(dateString: string | null | undefined): string {
  if (!dateString) return '';

  try {
    const date = parseISO(dateString);
    if (!isValid(date)) return '';

    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;

    return formatDate(dateString);
  } catch {
    return '';
  }
}

/**
 * Truncate text to maximum length with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
}

/**
 * Capitalize first letter of string
 */
export function capitalize(text: string): string {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/**
 * Convert text to title case
 */
export function toTitleCase(text: string): string {
  return text
    .split(' ')
    .map((word) => capitalize(word))
    .join(' ');
}

/**
 * Generate a readable initials from name
 */
export function getInitials(name: string | null | undefined): string {
  if (!name) return '?';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 0) return '?';
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

/**
 * Convert ISO 8601 date string to datetime-local format for input elements
 * Example: "2026-03-15T10:30:00Z" -> "2026-03-15T10:30"
 */
export function formatDateTimeLocal(dateString: string | null | undefined): string {
  if (!dateString) return '';

  try {
    const date = parseISO(dateString);
    if (!isValid(date)) return '';

    // Format as YYYY-MM-DDTHH:mm (datetime-local format)
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${year}-${month}-${day}T${hours}:${minutes}`;
  } catch {
    return '';
  }
}

/**
 * Check if date is in the past
 */
export function isPastDate(dateString: string | null | undefined): boolean {
  if (!dateString) return false;

  try {
    const date = parseISO(dateString);
    if (!isValid(date)) return false;
    return date < new Date();
  } catch {
    return false;
  }
}

/**
 * Check if date is today
 */
export function isToday(dateString: string | null | undefined): boolean {
  if (!dateString) return false;

  try {
    const date = parseISO(dateString);
    if (!isValid(date)) return false;

    const today = new Date();
    return (
      date.getFullYear() === today.getFullYear() &&
      date.getMonth() === today.getMonth() &&
      date.getDate() === today.getDate()
    );
  } catch {
    return false;
  }
}

/**
 * Check if date is tomorrow
 */
export function isTomorrow(dateString: string | null | undefined): boolean {
  if (!dateString) return false;

  try {
    const date = parseISO(dateString);
    if (!isValid(date)) return false;

    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);

    return (
      date.getFullYear() === tomorrow.getFullYear() &&
      date.getMonth() === tomorrow.getMonth() &&
      date.getDate() === tomorrow.getDate()
    );
  } catch {
    return false;
  }
}
