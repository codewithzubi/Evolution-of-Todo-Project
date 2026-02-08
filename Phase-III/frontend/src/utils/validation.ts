// [Task]: T-005, [From]: specs/002-task-ui-frontend/spec.md#FR-006
// Form validation utility functions

export interface ValidationError {
  field: string;
  message: string;
}

/**
 * Validate email format
 */
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate password minimum length (8 characters)
 * [Task]: T-005, [From]: specs/002-task-ui-frontend/spec.md#US1
 */
export function validatePassword(password: string): { valid: boolean; message?: string } {
  if (password.length < 8) {
    return {
      valid: false,
      message: 'Password must be at least 8 characters long',
    };
  }
  return { valid: true };
}

/**
 * Validate task title
 * Must be 1-255 characters
 * [Task]: T-005, [From]: specs/002-task-ui-frontend/spec.md#FR-006
 */
export function validateTaskTitle(title: string): { valid: boolean; message?: string } {
  if (!title || title.trim().length === 0) {
    return {
      valid: false,
      message: 'Title is required',
    };
  }

  if (title.length > 255) {
    return {
      valid: false,
      message: 'Title must be less than 255 characters',
    };
  }

  return { valid: true };
}

/**
 * Validate task description
 * Must be max 2000 characters
 * [Task]: T-005, [From]: specs/002-task-ui-frontend/spec.md#FR-006
 */
export function validateTaskDescription(description: string | undefined): {
  valid: boolean;
  message?: string;
} {
  if (!description) return { valid: true };

  if (description.length > 2000) {
    return {
      valid: false,
      message: 'Description must be less than 2000 characters',
    };
  }

  return { valid: true };
}

/**
 * Validate ISO 8601 date format
 * [Task]: T-005, [From]: specs/002-task-ui-frontend/spec.md#FR-006
 */
export function validateISODate(dateString: string | undefined): { valid: boolean; message?: string } {
  if (!dateString) return { valid: true };

  // Check ISO 8601 format
  const isoRegex = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?)?$/;
  if (!isoRegex.test(dateString)) {
    return {
      valid: false,
      message: 'Invalid date format. Use ISO 8601 (e.g., 2026-03-15)',
    };
  }

  // Verify it's a valid date
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return {
        valid: false,
        message: 'Invalid date',
      };
    }
  } catch {
    return {
      valid: false,
      message: 'Invalid date',
    };
  }

  return { valid: true };
}

/**
 * Validate task due date
 * May be in the past (with warning) but must be valid
 * [Task]: T-005, [From]: specs/002-task-ui-frontend/spec.md#US3
 */
export function validateTaskDueDate(
  dateString: string | undefined
): { valid: boolean; message?: string; warning?: string } {
  const dateValidation = validateISODate(dateString);
  if (!dateValidation.valid) {
    return dateValidation;
  }

  if (dateString) {
    const dueDate = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (dueDate < today) {
      return {
        valid: true,
        warning: 'This due date is in the past',
      };
    }
  }

  return { valid: true };
}

/**
 * Validate login form data
 */
export function validateLoginForm(email: string, password: string): ValidationError[] {
  const errors: ValidationError[] = [];

  if (!email || email.trim().length === 0) {
    errors.push({
      field: 'email',
      message: 'Email is required',
    });
  } else if (!validateEmail(email)) {
    errors.push({
      field: 'email',
      message: 'Invalid email format',
    });
  }

  if (!password || password.length === 0) {
    errors.push({
      field: 'password',
      message: 'Password is required',
    });
  }

  return errors;
}

/**
 * Validate signup form data
 */
export function validateSignupForm(
  email: string,
  password: string,
  confirmPassword: string
): ValidationError[] {
  const errors: ValidationError[] = [];

  if (!email || email.trim().length === 0) {
    errors.push({
      field: 'email',
      message: 'Email is required',
    });
  } else if (!validateEmail(email)) {
    errors.push({
      field: 'email',
      message: 'Invalid email format',
    });
  }

  const passwordValidation = validatePassword(password);
  if (!passwordValidation.valid) {
    errors.push({
      field: 'password',
      message: passwordValidation.message || 'Invalid password',
    });
  }

  if (password !== confirmPassword) {
    errors.push({
      field: 'confirmPassword',
      message: 'Passwords do not match',
    });
  }

  return errors;
}

/**
 * Validate task creation form data
 */
export function validateCreateTaskForm(
  title: string,
  description?: string,
  dueDate?: string
): ValidationError[] {
  const errors: ValidationError[] = [];

  const titleValidation = validateTaskTitle(title);
  if (!titleValidation.valid) {
    errors.push({
      field: 'title',
      message: titleValidation.message || 'Invalid title',
    });
  }

  if (description) {
    const descriptionValidation = validateTaskDescription(description);
    if (!descriptionValidation.valid) {
      errors.push({
        field: 'description',
        message: descriptionValidation.message || 'Invalid description',
      });
    }
  }

  if (dueDate) {
    const dueDateValidation = validateTaskDueDate(dueDate);
    if (!dueDateValidation.valid) {
      errors.push({
        field: 'dueDate',
        message: dueDateValidation.message || 'Invalid due date',
      });
    }
  }

  return errors;
}
