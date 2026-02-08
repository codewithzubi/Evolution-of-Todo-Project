// [Task]: T072, [From]: specs/002-task-ui-frontend/spec.md#US3
// Unit tests for TaskCreateForm component

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskCreateForm } from '@/components/tasks/TaskCreateForm';
import { ToastProvider } from '@/components/common/Toast';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock useCreateTask hook
vi.mock('@/hooks/useTask', () => ({
  useCreateTask: (userId: string) => {
    return {
      mutate: vi.fn((data, callbacks) => {
        // Simulate successful creation by default
        setTimeout(() => {
          callbacks?.onSuccess?.({
            id: 'task-1',
            userId,
            title: data.title,
            description: data.description,
            dueDate: data.dueDate,
            completed: false,
            completedAt: null,
            createdAt: '2026-02-02T10:00:00Z',
            updatedAt: '2026-02-02T10:00:00Z',
          });
        }, 100);
      }),
      isPending: false,
    };
  },
}));

describe('TaskCreateForm Component', () => {
  let queryClient: QueryClient;

  const renderForm = (props: any = {}) => {
    queryClient = new QueryClient();
    const defaultProps = {
      userId: 'user-123',
      onSuccess: vi.fn(),
      onError: vi.fn(),
      ...props,
    };

    return render(
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <TaskCreateForm {...defaultProps} />
        </ToastProvider>
      </QueryClientProvider>
    );
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Form Rendering', () => {
    it('should render form with all required fields', () => {
      renderForm();

      expect(screen.getByLabelText(/task title/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/due date/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /create task/i })).toBeInTheDocument();
    });

    it('should render title field as required', () => {
      renderForm();

      const titleInput = screen.getByLabelText(/task title/i);
      expect(titleInput).toBeRequired();
    });

    it('should render description field as optional', () => {
      renderForm();

      const descInput = screen.getByLabelText(/description/i);
      expect(descInput).not.toBeRequired();
    });

    it('should render submit button disabled initially', () => {
      renderForm();

      const submitButton = screen.getByRole('button', { name: /create task/i });
      expect(submitButton).toBeDisabled();
    });

    it('should display helper text for optional fields', () => {
      renderForm();

      expect(screen.getByText(/description is optional/i)).toBeInTheDocument();
      expect(screen.getByText(/due date is optional/i)).toBeInTheDocument();
    });
  });

  describe('Form Input Handling', () => {
    it('should update title input on change', async () => {
      const user = userEvent.setup();
      renderForm();

      const titleInput = screen.getByLabelText(/task title/i) as HTMLInputElement;
      await user.type(titleInput, 'Buy groceries');

      expect(titleInput.value).toBe('Buy groceries');
    });

    it('should update description input on change', async () => {
      const user = userEvent.setup();
      renderForm();

      const descInput = screen.getByLabelText(/description/i) as HTMLTextAreaElement;
      await user.type(descInput, 'Milk, eggs, bread');

      expect(descInput.value).toBe('Milk, eggs, bread');
    });

    it('should update due date input on change', async () => {
      const user = userEvent.setup();
      renderForm();

      const dueInput = screen.getByLabelText(/due date/i) as HTMLInputElement;
      await user.type(dueInput, '2026-03-15');

      expect(dueInput.value).toContain('2026-03-15');
    });

    it('should enable submit button when title is filled', async () => {
      const user = userEvent.setup();
      renderForm();

      const titleInput = screen.getByLabelText(/task title/i);
      const submitButton = screen.getByRole('button', { name: /create task/i });

      await user.type(titleInput, 'Valid task');

      expect(submitButton).not.toBeDisabled();
    });

    it('should display character count for title', async () => {
      const user = userEvent.setup();
      renderForm();

      const titleInput = screen.getByLabelText(/task title/i);
      await user.type(titleInput, 'Test');

      expect(screen.getByText('4/255 characters')).toBeInTheDocument();
    });

    it('should display character count for description', async () => {
      const user = userEvent.setup();
      renderForm();

      const descInput = screen.getByLabelText(/description/i);
      await user.type(descInput, 'Test description');

      expect(screen.getByText('16/2000 characters')).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('should show error when title is empty and field is blurred', async () => {
      const user = userEvent.setup();
      renderForm();

      const titleInput = screen.getByLabelText(/task title/i);
      await user.click(titleInput);
      await user.type(titleInput, 'T');
      await user.clear(titleInput);
      await user.click(screen.getByText(/description/i));

      await waitFor(() => {
        expect(screen.getByText(/title is required/i)).toBeInTheDocument();
      });
    });

    it('should show error when title exceeds 255 characters', async () => {
      const user = userEvent.setup();
      renderForm();

      const titleInput = screen.getByLabelText(/task title/i);
      const longTitle = 'a'.repeat(256);

      await user.type(titleInput, longTitle);
      await user.click(screen.getByText(/description/i));

      await waitFor(() => {
        expect(
          screen.getByText(/title must be less than 255 characters/i)
        ).toBeInTheDocument();
      });
    });

    it('should show error when description exceeds 2000 characters', async () => {
      const user = userEvent.setup();
      renderForm();

      const descInput = screen.getByLabelText(/description/i);
      const longDesc = 'a'.repeat(2001);

      await user.type(descInput, longDesc);
      await user.click(screen.getByLabelText(/task title/i));

      await waitFor(() => {
        expect(
          screen.getByText(/description must be less than 2000 characters/i)
        ).toBeInTheDocument();
      });
    });

    it('should clear validation error when user fixes the input', async () => {
      const user = userEvent.setup();
      renderForm();

      const titleInput = screen.getByLabelText(/task title/i);

      // Make it invalid
      await user.click(titleInput);
      await user.click(screen.getByText(/description/i));

      await waitFor(() => {
        expect(screen.getByText(/title is required/i)).toBeInTheDocument();
      });

      // Fix the input
      await user.click(titleInput);
      await user.type(titleInput, 'Valid task');

      await waitFor(() => {
        expect(screen.queryByText(/title is required/i)).not.toBeInTheDocument();
      });
    });

    it('should validate title on blur', async () => {
      const user = userEvent.setup();
      renderForm();

      const titleInput = screen.getByLabelText(/task title/i);
      await user.click(titleInput);
      await user.click(screen.getByText(/description/i));

      await waitFor(() => {
        expect(screen.getByText(/title is required/i)).toBeInTheDocument();
      });
    });
  });

  describe('Form Submission', () => {
    it('should not submit with invalid title', async () => {
      const onSuccess = vi.fn();
      renderForm({ onSuccess });

      const submitButton = screen.getByRole('button', { name: /create task/i });
      fireEvent.click(submitButton);

      // Submit should still be disabled
      expect(submitButton).toBeDisabled();
    });

    it('should reset form after successful submission', async () => {
      const user = userEvent.setup();
      const onSuccess = vi.fn();
      renderForm({ onSuccess });

      const titleInput = screen.getByLabelText(/task title/i) as HTMLInputElement;
      const descInput = screen.getByLabelText(/description/i) as HTMLTextAreaElement;

      await user.type(titleInput, 'New task');
      await user.type(descInput, 'Task description');

      const submitButton = screen.getByRole('button', { name: /create task/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(titleInput.value).toBe('');
        expect(descInput.value).toBe('');
      });
    });

    it('should disable submit button while loading', async () => {
      const user = userEvent.setup();
      renderForm();

      const titleInput = screen.getByLabelText(/task title/i);
      await user.type(titleInput, 'Test task');

      const submitButton = screen.getByRole('button', { name: /create task/i });
      expect(submitButton).not.toBeDisabled();

      await user.click(submitButton);

      // Button should be disabled during submission
      await waitFor(() => {
        expect(submitButton).toBeDisabled();
      });
    });

    it('should call onSuccess callback after successful submission', async () => {
      const user = userEvent.setup();
      const onSuccess = vi.fn();
      renderForm({ onSuccess });

      const titleInput = screen.getByLabelText(/task title/i);
      await user.type(titleInput, 'Success task');

      const submitButton = screen.getByRole('button', { name: /create task/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalled();
      });
    });
  });

  describe('Loading State', () => {
    it('should show loading text while submitting', async () => {
      const user = userEvent.setup();
      renderForm();

      const titleInput = screen.getByLabelText(/task title/i);
      await user.type(titleInput, 'Test task');

      const submitButton = screen.getByRole('button', { name: /create task/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/creating your task/i)).toBeInTheDocument();
      });
    });

    it('should disable inputs while loading', async () => {
      const user = userEvent.setup();
      renderForm();

      const titleInput = screen.getByLabelText(/task title/i) as HTMLInputElement;
      await user.type(titleInput, 'Test task');

      const submitButton = screen.getByRole('button', { name: /create task/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(titleInput).toBeDisabled();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper labels for all inputs', () => {
      renderForm();

      expect(screen.getByLabelText(/task title/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/due date/i)).toBeInTheDocument();
    });

    it('should have proper button labels', () => {
      renderForm();

      expect(screen.getByRole('button', { name: /create task/i })).toBeInTheDocument();
    });

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup();
      renderForm();

      const titleInput = screen.getByLabelText(/task title/i);

      // Tab to title field
      await user.tab();
      expect(titleInput).toHaveFocus();

      // Type in the field
      await user.keyboard('Test task');

      // Tab to description field
      await user.tab();
      expect(screen.getByLabelText(/description/i)).toHaveFocus();
    });
  });

  describe('Optional Fields', () => {
    it('should allow submission with only title', async () => {
      const user = userEvent.setup();
      const onSuccess = vi.fn();
      renderForm({ onSuccess });

      const titleInput = screen.getByLabelText(/task title/i);
      await user.type(titleInput, 'Only title');

      const submitButton = screen.getByRole('button', { name: /create task/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalled();
      });
    });

    it('should allow submission with title and description only', async () => {
      const user = userEvent.setup();
      const onSuccess = vi.fn();
      renderForm({ onSuccess });

      const titleInput = screen.getByLabelText(/task title/i);
      const descInput = screen.getByLabelText(/description/i);

      await user.type(titleInput, 'Title');
      await user.type(descInput, 'Description');

      const submitButton = screen.getByRole('button', { name: /create task/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalled();
      });
    });
  });
});
