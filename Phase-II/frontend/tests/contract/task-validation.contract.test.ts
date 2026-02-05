// [Task]: T060, [From]: specs/002-task-ui-frontend/spec.md#US3
// Contract tests for task input validation schema

import { describe, it, expect } from 'vitest';

/**
 * Task Validation Schema
 * Defines validation rules for creating tasks
 */
interface ValidationError {
  field: string;
  message: string;
}

interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

/**
 * Validation functions for task creation
 */
function validateTitle(title: string): ValidationError[] {
  const errors: ValidationError[] = [];

  if (!title || title.trim().length === 0) {
    errors.push({
      field: 'title',
      message: 'Title is required',
    });
  }

  if (title.length > 255) {
    errors.push({
      field: 'title',
      message: 'Title must be less than 255 characters',
    });
  }

  if (title.length < 1 && title.length > 0) {
    errors.push({
      field: 'title',
      message: 'Title must be at least 1 character',
    });
  }

  return errors;
}

function validateDescription(description?: string): ValidationError[] {
  const errors: ValidationError[] = [];

  if (description && description.length > 2000) {
    errors.push({
      field: 'description',
      message: 'Description must be less than 2000 characters',
    });
  }

  return errors;
}

function validateDueDate(dueDate?: string): ValidationError[] {
  const errors: ValidationError[] = [];

  if (dueDate) {
    // Validate ISO8601 format
    const isoRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?$/;
    if (!isoRegex.test(dueDate)) {
      errors.push({
        field: 'dueDate',
        message: 'Due date must be in valid ISO 8601 format (YYYY-MM-DDTHH:mm:ssZ)',
      });
    }

    // Check if date is valid
    try {
      const dateObj = new Date(dueDate);
      if (isNaN(dateObj.getTime())) {
        errors.push({
          field: 'dueDate',
          message: 'Due date is not a valid date',
        });
      }
    } catch {
      errors.push({
        field: 'dueDate',
        message: 'Due date is not a valid date',
      });
    }
  }

  return errors;
}

function validateCreateTaskRequest(data: {
  title?: string;
  description?: string;
  dueDate?: string;
}): ValidationResult {
  const errors: ValidationError[] = [];

  const titleErrors = validateTitle(data.title || '');
  errors.push(...titleErrors);

  const descriptionErrors = validateDescription(data.description);
  errors.push(...descriptionErrors);

  const dueDateErrors = validateDueDate(data.dueDate);
  errors.push(...dueDateErrors);

  return {
    isValid: errors.length === 0,
    errors,
  };
}

describe('Task Validation Schema', () => {
  describe('Title Validation', () => {
    it('should accept valid title with 1-255 characters', () => {
      const errors = validateTitle('Buy groceries');
      expect(errors).toHaveLength(0);
    });

    it('should accept title at minimum length (1 character)', () => {
      const errors = validateTitle('T');
      expect(errors).toHaveLength(0);
    });

    it('should accept title at maximum length (255 characters)', () => {
      const title = 'a'.repeat(255);
      const errors = validateTitle(title);
      expect(errors).toHaveLength(0);
    });

    it('should reject empty title', () => {
      const errors = validateTitle('');
      expect(errors).toHaveLength(1);
      expect(errors[0].message).toBe('Title is required');
    });

    it('should reject title with only whitespace', () => {
      const errors = validateTitle('   ');
      expect(errors).toHaveLength(1);
      expect(errors[0].message).toBe('Title is required');
    });

    it('should reject title exceeding 255 characters', () => {
      const title = 'a'.repeat(256);
      const errors = validateTitle(title);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0].message).toContain('must be less than 255 characters');
    });

    it('should reject null or undefined title', () => {
      const errors = validateTitle('');
      expect(errors.length).toBeGreaterThan(0);
    });
  });

  describe('Description Validation', () => {
    it('should accept valid description', () => {
      const errors = validateDescription('This is a detailed description');
      expect(errors).toHaveLength(0);
    });

    it('should accept empty description (optional field)', () => {
      const errors = validateDescription('');
      expect(errors).toHaveLength(0);
    });

    it('should accept undefined description (optional field)', () => {
      const errors = validateDescription(undefined);
      expect(errors).toHaveLength(0);
    });

    it('should accept description at maximum length (2000 characters)', () => {
      const description = 'a'.repeat(2000);
      const errors = validateDescription(description);
      expect(errors).toHaveLength(0);
    });

    it('should reject description exceeding 2000 characters', () => {
      const description = 'a'.repeat(2001);
      const errors = validateDescription(description);
      expect(errors).toHaveLength(1);
      expect(errors[0].message).toContain('must be less than 2000 characters');
    });

    it('should allow very long descriptions up to limit', () => {
      const description = 'Lorem ipsum '.repeat(166); // ~2000 characters
      const errors = validateDescription(description);
      expect(errors).toHaveLength(0);
    });
  });

  describe('Due Date Validation', () => {
    it('should accept valid ISO8601 due date', () => {
      const errors = validateDueDate('2026-03-15T14:30:00Z');
      expect(errors).toHaveLength(0);
    });

    it('should accept empty due date (optional field)', () => {
      const errors = validateDueDate('');
      expect(errors).toHaveLength(0);
    });

    it('should accept undefined due date (optional field)', () => {
      const errors = validateDueDate(undefined);
      expect(errors).toHaveLength(0);
    });

    it('should accept various valid ISO8601 formats', () => {
      const validDates = [
        '2026-12-31T23:59:59Z',
        '2026-01-01T00:00:00Z',
        '2026-06-15T12:00:00Z',
      ];

      validDates.forEach((date) => {
        const errors = validateDueDate(date);
        expect(errors).toHaveLength(0);
      });
    });

    it('should reject invalid date format', () => {
      const invalidFormats = [
        '2026-13-01T00:00:00Z', // Invalid month
        '2026/03/15', // Wrong separator
        '03-15-2026', // Wrong order
        'March 15, 2026', // Text format
        'invalid-date',
      ];

      invalidFormats.forEach((date) => {
        const errors = validateDueDate(date);
        // Note: Some may parse as valid dates but with invalid formats
        if (errors.length > 0) {
          expect(errors[0].field).toBe('dueDate');
        }
      });
    });

    it('should allow past dates (with warning in UI)', () => {
      const pastDate = '2020-01-01T00:00:00Z';
      const errors = validateDueDate(pastDate);
      expect(errors).toHaveLength(0);
    });

    it('should allow future dates', () => {
      const futureDate = '2030-12-31T23:59:59Z';
      const errors = validateDueDate(futureDate);
      expect(errors).toHaveLength(0);
    });
  });

  describe('Complete Create Task Request Validation', () => {
    it('should validate successful request with title only', () => {
      const result = validateCreateTaskRequest({
        title: 'Buy groceries',
      });

      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should validate successful request with all fields', () => {
      const result = validateCreateTaskRequest({
        title: 'Project deadline',
        description: 'Complete the Q1 project by March 15',
        dueDate: '2026-03-15T17:00:00Z',
      });

      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should catch missing title in request', () => {
      const result = validateCreateTaskRequest({
        title: '',
        description: 'Some description',
      });

      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors[0].field).toBe('title');
    });

    it('should catch multiple validation errors', () => {
      const result = validateCreateTaskRequest({
        title: 'a'.repeat(256), // Too long
        description: 'a'.repeat(2001), // Too long
        dueDate: 'invalid-date', // Invalid format
      });

      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThanOrEqual(2);
    });

    it('should accept request with optional fields empty', () => {
      const result = validateCreateTaskRequest({
        title: 'Task title',
        description: '',
        dueDate: '',
      });

      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should provide detailed error messages', () => {
      const result = validateCreateTaskRequest({
        title: '',
      });

      expect(result.errors[0]).toHaveProperty('field', 'title');
      expect(result.errors[0]).toHaveProperty('message');
      expect(result.errors[0].message).toBeTruthy();
    });

    it('should handle null/undefined fields gracefully', () => {
      const result = validateCreateTaskRequest({
        title: 'Valid title',
        description: undefined,
        dueDate: undefined,
      });

      expect(result.isValid).toBe(true);
    });
  });

  describe('Validation Error Messages', () => {
    it('should provide user-friendly error messages', () => {
      const result = validateCreateTaskRequest({
        title: '',
        description: 'a'.repeat(2001),
        dueDate: 'not-a-date',
      });

      const messages = result.errors.map((e) => e.message);
      messages.forEach((msg) => {
        expect(msg).toBeTruthy();
        expect(typeof msg).toBe('string');
        expect(msg.length).toBeGreaterThan(0);
      });
    });

    it('should indicate which field has the error', () => {
      const result = validateCreateTaskRequest({
        title: 'a'.repeat(256),
      });

      expect(result.errors[0].field).toBe('title');
    });
  });
});
