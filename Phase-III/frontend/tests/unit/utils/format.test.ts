// [Task]: T-050, [From]: specs/002-task-ui-frontend/spec.md#Testing-Phase
// Unit tests for format utilities

import { describe, it, expect } from 'vitest';
import {
  formatDate,
  formatRelativeTime,
  truncateText,
  capitalize,
  isPastDate,
  isToday,
  isTomorrow,
  getInitials,
} from '@/utils/format';

describe('Format Utilities', () => {
  describe('formatDate', () => {
    it('should format ISO date string to user-friendly format', () => {
      const result = formatDate('2026-03-15T10:30:00Z');
      expect(result).toBe('Mar 15, 2026');
    });

    it('should handle null and undefined values', () => {
      expect(formatDate(null)).toBe('');
      expect(formatDate(undefined)).toBe('');
    });

    it('should handle invalid date strings', () => {
      expect(formatDate('invalid-date')).toBe('');
    });
  });

  describe('truncateText', () => {
    it('should truncate text longer than max length', () => {
      const result = truncateText('This is a long text', 10);
      expect(result).toBe('This is a ...');
    });

    it('should not truncate text shorter than max length', () => {
      const result = truncateText('Short', 10);
      expect(result).toBe('Short');
    });
  });

  describe('capitalize', () => {
    it('should capitalize first letter', () => {
      expect(capitalize('hello')).toBe('Hello');
    });

    it('should handle empty string', () => {
      expect(capitalize('')).toBe('');
    });
  });

  describe('getInitials', () => {
    it('should extract initials from full name', () => {
      expect(getInitials('John Doe')).toBe('JD');
    });

    it('should handle single name', () => {
      expect(getInitials('John')).toBe('JO');
    });

    it('should return ? for null/undefined', () => {
      expect(getInitials(null)).toBe('?');
      expect(getInitials(undefined)).toBe('?');
    });
  });

  describe('isPastDate', () => {
    it('should identify past dates', () => {
      const pastDate = new Date();
      pastDate.setDate(pastDate.getDate() - 1);
      expect(isPastDate(pastDate.toISOString())).toBe(true);
    });

    it('should identify future dates as not past', () => {
      const futureDate = new Date();
      futureDate.setDate(futureDate.getDate() + 1);
      expect(isPastDate(futureDate.toISOString())).toBe(false);
    });

    it('should handle null/undefined', () => {
      expect(isPastDate(null)).toBe(false);
      expect(isPastDate(undefined)).toBe(false);
    });
  });

  describe('isToday', () => {
    it('should identify today', () => {
      expect(isToday(new Date().toISOString())).toBe(true);
    });

    it('should not identify yesterday as today', () => {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      expect(isToday(yesterday.toISOString())).toBe(false);
    });
  });

  describe('isTomorrow', () => {
    it('should identify tomorrow', () => {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      expect(isTomorrow(tomorrow.toISOString())).toBe(true);
    });

    it('should not identify today as tomorrow', () => {
      expect(isTomorrow(new Date().toISOString())).toBe(false);
    });
  });

  describe('formatRelativeTime', () => {
    it('should format recent times as "just now"', () => {
      const justNow = new Date();
      expect(formatRelativeTime(justNow.toISOString())).toBe('just now');
    });

    it('should handle null/undefined', () => {
      expect(formatRelativeTime(null)).toBe('');
      expect(formatRelativeTime(undefined)).toBe('');
    });
  });
});
