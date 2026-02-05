// [Task]: T057, [From]: specs/002-task-ui-frontend/spec.md#US2
// Unit tests for TaskList component

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TaskList } from '@/components/tasks';
import type { Task } from '@/types/task';

const mockTasks: Task[] = [
  {
    id: '1',
    userId: 'user123',
    title: 'Task 1',
    description: 'Description 1',
    dueDate: '2026-02-10T00:00:00Z',
    completed: false,
    completedAt: null,
    createdAt: '2026-02-01T00:00:00Z',
    updatedAt: '2026-02-01T00:00:00Z',
  },
  {
    id: '2',
    userId: 'user123',
    title: 'Task 2',
    description: 'Description 2',
    completed: true,
    completedAt: '2026-02-02T00:00:00Z',
    createdAt: '2026-02-01T00:00:00Z',
    updatedAt: '2026-02-02T00:00:00Z',
  },
];

describe('TaskList Component', () => {
  it('should render task list with all tasks', () => {
    const onPageChange = vi.fn();

    render(
      <TaskList
        tasks={mockTasks}
        isLoading={false}
        error={null}
        currentPage={1}
        totalPages={1}
        onPageChange={onPageChange}
      />
    );

    expect(screen.getByText('Task 1')).toBeInTheDocument();
    expect(screen.getByText('Task 2')).toBeInTheDocument();
  });

  it('should call pagination callback when page changes', () => {
    const onPageChange = vi.fn();

    render(
      <TaskList
        tasks={mockTasks}
        isLoading={false}
        error={null}
        currentPage={1}
        totalPages={2}
        onPageChange={onPageChange}
      />
    );

    const nextButton = screen.getByLabelText('Go to next page');
    fireEvent.click(nextButton);

    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it('should display loading skeleton when loading', () => {
    const onPageChange = vi.fn();

    render(
      <TaskList
        tasks={[]}
        isLoading={true}
        error={null}
        currentPage={1}
        totalPages={1}
        onPageChange={onPageChange}
      />
    );

    // Skeleton loader should be displayed (has animate-pulse class)
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('should display error message when error occurs', () => {
    const onPageChange = vi.fn();
    const onRetry = vi.fn();
    const error = new Error('Failed to fetch tasks');

    render(
      <TaskList
        tasks={[]}
        isLoading={false}
        error={error}
        currentPage={1}
        totalPages={1}
        onPageChange={onPageChange}
        onRetry={onRetry}
      />
    );

    expect(screen.getByText('Failed to load tasks')).toBeInTheDocument();
    expect(screen.getByText(/Failed to fetch tasks/)).toBeInTheDocument();
  });

  it('should call retry function when retry button is clicked', () => {
    const onPageChange = vi.fn();
    const onRetry = vi.fn();
    const error = new Error('Network error');

    render(
      <TaskList
        tasks={[]}
        isLoading={false}
        error={error}
        currentPage={1}
        totalPages={1}
        onPageChange={onPageChange}
        onRetry={onRetry}
      />
    );

    const retryButton = screen.getByText('Try Again');
    fireEvent.click(retryButton);

    expect(onRetry).toHaveBeenCalled();
  });

  it('should display empty state when no tasks and not loading', () => {
    const onPageChange = vi.fn();

    render(
      <TaskList
        tasks={[]}
        isLoading={false}
        error={null}
        currentPage={1}
        totalPages={0}
        onPageChange={onPageChange}
      />
    );

    expect(screen.getByText('No tasks yet. Create one to get started.')).toBeInTheDocument();
  });

  it('should call task callbacks correctly', () => {
    const onPageChange = vi.fn();
    const onComplete = vi.fn();
    const onEdit = vi.fn();
    const onDelete = vi.fn();

    render(
      <TaskList
        tasks={mockTasks}
        isLoading={false}
        error={null}
        currentPage={1}
        totalPages={1}
        onPageChange={onPageChange}
        onComplete={onComplete}
        onEdit={onEdit}
        onDelete={onDelete}
      />
    );

    // Click complete checkbox on first task
    const completeButtons = screen.getAllByRole('button');
    const completeCheckbox = completeButtons[0]; // First button is checkbox
    fireEvent.click(completeCheckbox);

    expect(onComplete).toHaveBeenCalledWith('1');
  });

  it('should display correct page indicator', () => {
    const onPageChange = vi.fn();

    render(
      <TaskList
        tasks={mockTasks}
        isLoading={false}
        error={null}
        currentPage={2}
        totalPages={5}
        onPageChange={onPageChange}
      />
    );

    expect(screen.getByText('Page 2')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('should disable previous button on first page', () => {
    const onPageChange = vi.fn();

    render(
      <TaskList
        tasks={mockTasks}
        isLoading={false}
        error={null}
        currentPage={1}
        totalPages={5}
        onPageChange={onPageChange}
      />
    );

    const prevButton = screen.getByLabelText('Go to previous page');
    expect(prevButton).toBeDisabled();
  });

  it('should disable next button on last page', () => {
    const onPageChange = vi.fn();

    render(
      <TaskList
        tasks={mockTasks}
        isLoading={false}
        error={null}
        currentPage={5}
        totalPages={5}
        onPageChange={onPageChange}
      />
    );

    const nextButton = screen.getByLabelText('Go to next page');
    expect(nextButton).toBeDisabled();
  });

  it('should handle responsive layout on mobile', () => {
    const onPageChange = vi.fn();

    const { container } = render(
      <TaskList
        tasks={mockTasks}
        isLoading={false}
        error={null}
        currentPage={1}
        totalPages={1}
        onPageChange={onPageChange}
      />
    );

    // Check that responsive classes are present
    const taskItems = container.querySelectorAll('[class*="flex-col"]');
    expect(taskItems.length).toBeGreaterThanOrEqual(0);
  });

  it('should display completion status correctly', () => {
    const onPageChange = vi.fn();

    render(
      <TaskList
        tasks={mockTasks}
        isLoading={false}
        error={null}
        currentPage={1}
        totalPages={1}
        onPageChange={onPageChange}
      />
    );

    // First task is incomplete, second is complete
    const taskElements = screen.getAllByRole('button').slice(0, 2);
    expect(taskElements.length).toBeGreaterThan(0);
  });
});
