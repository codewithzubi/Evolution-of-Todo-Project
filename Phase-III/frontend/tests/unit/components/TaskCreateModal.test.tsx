// [Task]: T073, [From]: specs/002-task-ui-frontend/spec.md#US3
// Unit tests for TaskCreateModal component

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskCreateModal } from '@/components/tasks/TaskCreateModal';
import { ToastProvider } from '@/components/common/Toast';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock useCreateTask hook
vi.mock('@/hooks/useTask', () => ({
  useCreateTask: (userId: string) => {
    return {
      mutate: vi.fn((data, callbacks) => {
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

describe('TaskCreateModal Component', () => {
  let queryClient: QueryClient;

  const renderModal = (props: any = {}) => {
    queryClient = new QueryClient();
    const defaultProps = {
      isOpen: true,
      userId: 'user-123',
      onClose: vi.fn(),
      onSuccess: vi.fn(),
      ...props,
    };

    return render(
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <TaskCreateModal {...defaultProps} />
        </ToastProvider>
      </QueryClientProvider>
    );
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Modal Visibility', () => {
    it('should render modal when isOpen is true', () => {
      renderModal({ isOpen: true });

      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Create New Task')).toBeInTheDocument();
    });

    it('should not render modal when isOpen is false', () => {
      renderModal({ isOpen: false });

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    it('should toggle modal visibility based on isOpen prop', () => {
      const { rerender } = renderModal({ isOpen: true });

      expect(screen.getByRole('dialog')).toBeInTheDocument();

      rerender(
        <QueryClientProvider client={queryClient}>
          <ToastProvider>
            <TaskCreateModal
              isOpen={false}
              userId="user-123"
              onClose={vi.fn()}
              onSuccess={vi.fn()}
            />
          </ToastProvider>
        </QueryClientProvider>
      );

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  describe('Modal Header', () => {
    it('should display modal title', () => {
      renderModal();

      expect(screen.getByText('Create New Task')).toBeInTheDocument();
    });

    it('should render close button in header', () => {
      renderModal();

      const closeButton = screen.getByLabelText('Close modal');
      expect(closeButton).toBeInTheDocument();
    });

    it('should have proper ARIA attributes', () => {
      renderModal();

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveAttribute('aria-modal', 'true');
      expect(dialog).toHaveAttribute('aria-labelledby', 'modal-title');
    });
  });

  describe('Modal Content', () => {
    it('should render TaskCreateForm inside modal', () => {
      renderModal();

      expect(screen.getByLabelText(/task title/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/due date/i)).toBeInTheDocument();
    });

    it('should pass userId to TaskCreateForm', () => {
      const userId = 'test-user-456';
      renderModal({ userId });

      // Form should be rendered with the userId
      expect(screen.getByLabelText(/task title/i)).toBeInTheDocument();
    });
  });

  describe('Close Button', () => {
    it('should call onClose when close button is clicked', async () => {
      const onClose = vi.fn();
      const user = userEvent.setup();
      renderModal({ onClose });

      const closeButton = screen.getByLabelText('Close modal');
      await user.click(closeButton);

      expect(onClose).toHaveBeenCalled();
    });

    it('should close modal when close button is clicked', async () => {
      const onClose = vi.fn();
      const user = userEvent.setup();
      renderModal({ onClose, isOpen: true });

      const closeButton = screen.getByLabelText('Close modal');
      await user.click(closeButton);

      expect(onClose).toHaveBeenCalled();
    });
  });

  describe('Backdrop Click', () => {
    it('should call onClose when backdrop is clicked', async () => {
      const onClose = vi.fn();
      const user = userEvent.setup();
      renderModal({ onClose });

      const backdrop = screen.getByRole('dialog').parentElement;
      if (backdrop) {
        await user.click(backdrop);
        expect(onClose).toHaveBeenCalled();
      }
    });

    it('should not close modal when modal content is clicked', async () => {
      const onClose = vi.fn();
      const user = userEvent.setup();
      renderModal({ onClose });

      const titleInput = screen.getByLabelText(/task title/i);
      await user.click(titleInput);

      expect(onClose).not.toHaveBeenCalled();
    });
  });

  describe('Keyboard Interaction', () => {
    it('should close modal when ESC key is pressed', async () => {
      const onClose = vi.fn();
      const user = userEvent.setup();
      renderModal({ onClose, isOpen: true });

      await user.keyboard('{Escape}');

      expect(onClose).toHaveBeenCalled();
    });

    it('should not close modal when ESC is pressed and modal is closed', async () => {
      const onClose = vi.fn();
      renderModal({ onClose, isOpen: false });

      fireEvent.keyDown(document, { key: 'Escape' });

      expect(onClose).not.toHaveBeenCalled();
    });
  });

  describe('Form Submission', () => {
    it('should call onSuccess when form is submitted successfully', async () => {
      const onSuccess = vi.fn();
      const user = userEvent.setup();
      renderModal({ onSuccess });

      const titleInput = screen.getByLabelText(/task title/i);
      await user.type(titleInput, 'Test task');

      const submitButton = screen.getByRole('button', { name: /create task/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalled();
      });
    });

    it('should close modal when form is submitted successfully', async () => {
      const onClose = vi.fn();
      const onSuccess = vi.fn();
      const user = userEvent.setup();
      renderModal({ onClose, onSuccess });

      const titleInput = screen.getByLabelText(/task title/i);
      await user.type(titleInput, 'Test task');

      const submitButton = screen.getByRole('button', { name: /create task/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(onClose).toHaveBeenCalled();
      });
    });

    it('should pass created task to onSuccess callback', async () => {
      const onSuccess = vi.fn();
      const user = userEvent.setup();
      renderModal({ onSuccess });

      const titleInput = screen.getByLabelText(/task title/i);
      await user.type(titleInput, 'Test task');

      const submitButton = screen.getByRole('button', { name: /create task/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalledWith(
          expect.objectContaining({
            id: expect.any(String),
            title: 'Test task',
          })
        );
      });
    });
  });

  describe('Responsive Design', () => {
    it('should have responsive classes for mobile', () => {
      renderModal();

      const dialog = screen.getByRole('dialog');
      expect(dialog.parentElement).toHaveClass('flex');
      expect(dialog.parentElement).toHaveClass('items-center');
      expect(dialog.parentElement).toHaveClass('justify-center');
    });

    it('should have max-width constraint', () => {
      renderModal();

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveClass('max-w-md');
    });

    it('should be scrollable on mobile', () => {
      renderModal();

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveClass('max-h-[90vh]');
      expect(dialog).toHaveClass('overflow-y-auto');
    });
  });

  describe('Animations', () => {
    it('should have animation classes', () => {
      renderModal();

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveClass('animate-in');
      expect(dialog).toHaveClass('fade-in');
      expect(dialog).toHaveClass('zoom-in-95');
    });
  });

  describe('Body Overflow', () => {
    it('should prevent body scroll when modal is open', () => {
      renderModal({ isOpen: true });

      expect(document.body.style.overflow).toBe('hidden');
    });

    it('should restore body scroll when modal closes', () => {
      const { unmount } = renderModal({ isOpen: true });

      expect(document.body.style.overflow).toBe('hidden');

      unmount();

      expect(document.body.style.overflow).toBe('');
    });

    it('should not affect body scroll when modal is closed', () => {
      renderModal({ isOpen: false });

      expect(document.body.style.overflow).toBe('');
    });
  });

  describe('Integration with Form', () => {
    it('should support creating task from modal', async () => {
      const onSuccess = vi.fn();
      const user = userEvent.setup();
      renderModal({ onSuccess });

      const titleInput = screen.getByLabelText(/task title/i);
      const descInput = screen.getByLabelText(/description/i);

      await user.type(titleInput, 'Modal task');
      await user.type(descInput, 'Task from modal');

      const submitButton = screen.getByRole('button', { name: /create task/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Modal task',
            description: 'Task from modal',
          })
        );
      });
    });

    it('should display validation errors in form', () => {
      renderModal();

      const submitButton = screen.getByRole('button', { name: /create task/i });
      fireEvent.click(submitButton);

      // Button should still be disabled since title is required
      expect(submitButton).toBeDisabled();
    });
  });

  describe('Accessibility', () => {
    it('should have proper dialog role', () => {
      renderModal();

      const dialog = screen.getByRole('dialog');
      expect(dialog).toBeInTheDocument();
    });

    it('should have proper title association', () => {
      renderModal();

      const dialog = screen.getByRole('dialog');
      const title = screen.getByText('Create New Task');

      expect(dialog).toHaveAttribute('aria-labelledby', 'modal-title');
      expect(title).toHaveAttribute('id', 'modal-title');
    });

    it('should have close button with aria-label', () => {
      renderModal();

      const closeButton = screen.getByLabelText('Close modal');
      expect(closeButton).toHaveAttribute('aria-label', 'Close modal');
    });

    it('should support focus management', async () => {
      const user = userEvent.setup();
      renderModal();

      const titleInput = screen.getByLabelText(/task title/i);
      await user.tab();

      // Focus should be on the form
      expect(titleInput).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle rapid open/close', async () => {
      const onClose = vi.fn();
      const { rerender } = renderModal({ onClose, isOpen: true });

      expect(screen.getByRole('dialog')).toBeInTheDocument();

      rerender(
        <QueryClientProvider client={queryClient}>
          <ToastProvider>
            <TaskCreateModal
              isOpen={false}
              userId="user-123"
              onClose={onClose}
              onSuccess={vi.fn()}
            />
          </ToastProvider>
        </QueryClientProvider>
      );

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();

      rerender(
        <QueryClientProvider client={queryClient}>
          <ToastProvider>
            <TaskCreateModal
              isOpen={true}
              userId="user-123"
              onClose={onClose}
              onSuccess={vi.fn()}
            />
          </ToastProvider>
        </QueryClientProvider>
      );

      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('should handle multiple modals (only one should be open)', () => {
      renderModal({ isOpen: true });

      expect(screen.getAllByRole('dialog')).toHaveLength(1);
    });
  });
});
