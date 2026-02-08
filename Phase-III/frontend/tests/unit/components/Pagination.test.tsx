// [Task]: T058, [From]: specs/002-task-ui-frontend/spec.md#US2
// Unit tests for Pagination component

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Pagination } from '@/components/common/Pagination';

describe('Pagination Component', () => {
  it('should render with correct page numbers', () => {
    const onPageChange = vi.fn();

    render(
      <Pagination
        currentPage={1}
        totalPages={5}
        onPageChange={onPageChange}
      />
    );

    expect(screen.getByText('Page 1')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('should call onPageChange with correct page when next is clicked', () => {
    const onPageChange = vi.fn();

    render(
      <Pagination
        currentPage={2}
        totalPages={5}
        onPageChange={onPageChange}
      />
    );

    const nextButton = screen.getByLabelText('Go to next page');
    fireEvent.click(nextButton);

    expect(onPageChange).toHaveBeenCalledWith(3);
  });

  it('should call onPageChange with correct page when previous is clicked', () => {
    const onPageChange = vi.fn();

    render(
      <Pagination
        currentPage={3}
        totalPages={5}
        onPageChange={onPageChange}
      />
    );

    const prevButton = screen.getByLabelText('Go to previous page');
    fireEvent.click(prevButton);

    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it('should disable previous button on first page', () => {
    const onPageChange = vi.fn();

    render(
      <Pagination
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
      <Pagination
        currentPage={5}
        totalPages={5}
        onPageChange={onPageChange}
      />
    );

    const nextButton = screen.getByLabelText('Go to next page');
    expect(nextButton).toBeDisabled();
  });

  it('should enable both buttons on middle page', () => {
    const onPageChange = vi.fn();

    render(
      <Pagination
        currentPage={3}
        totalPages={5}
        onPageChange={onPageChange}
      />
    );

    const prevButton = screen.getByLabelText('Go to previous page');
    const nextButton = screen.getByLabelText('Go to next page');

    expect(prevButton).not.toBeDisabled();
    expect(nextButton).not.toBeDisabled();
  });

  it('should handle single page scenario', () => {
    const onPageChange = vi.fn();

    render(
      <Pagination
        currentPage={1}
        totalPages={1}
        onPageChange={onPageChange}
      />
    );

    const prevButton = screen.getByLabelText('Go to previous page');
    const nextButton = screen.getByLabelText('Go to next page');

    expect(prevButton).toBeDisabled();
    expect(nextButton).toBeDisabled();
  });

  it('should display "of" separator between current and total pages', () => {
    const onPageChange = vi.fn();

    render(
      <Pagination
        currentPage={2}
        totalPages={10}
        onPageChange={onPageChange}
      />
    );

    expect(screen.getByText('of')).toBeInTheDocument();
  });

  it('should disable buttons when isLoading is true', () => {
    const onPageChange = vi.fn();

    render(
      <Pagination
        currentPage={2}
        totalPages={5}
        onPageChange={onPageChange}
        isLoading={true}
      />
    );

    const prevButton = screen.getByLabelText('Go to previous page');
    const nextButton = screen.getByLabelText('Go to next page');

    expect(prevButton).toBeDisabled();
    expect(nextButton).toBeDisabled();
  });

  it('should handle large page numbers', () => {
    const onPageChange = vi.fn();

    render(
      <Pagination
        currentPage={50}
        totalPages={100}
        onPageChange={onPageChange}
      />
    );

    expect(screen.getByText('Page 50')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
  });

  it('should not trigger onPageChange when disabled button is clicked', () => {
    const onPageChange = vi.fn();

    render(
      <Pagination
        currentPage={1}
        totalPages={5}
        onPageChange={onPageChange}
      />
    );

    const prevButton = screen.getByLabelText('Go to previous page');
    fireEvent.click(prevButton);

    expect(onPageChange).not.toHaveBeenCalled();
  });

  it('should have correct aria labels for accessibility', () => {
    const onPageChange = vi.fn();

    render(
      <Pagination
        currentPage={2}
        totalPages={5}
        onPageChange={onPageChange}
      />
    );

    const nav = screen.getByRole('navigation', { name: 'Pagination' });
    expect(nav).toBeInTheDocument();

    expect(screen.getByLabelText('Go to previous page')).toBeInTheDocument();
    expect(screen.getByLabelText('Go to next page')).toBeInTheDocument();
  });

  it('should have correct styling for buttons', () => {
    const onPageChange = vi.fn();

    const { container } = render(
      <Pagination
        currentPage={2}
        totalPages={5}
        onPageChange={onPageChange}
      />
    );

    const buttons = container.querySelectorAll('button');
    expect(buttons.length).toBe(2);

    // Enabled buttons should have blue styling
    buttons.forEach((button) => {
      if (!button.disabled) {
        expect(button).toHaveClass('bg-blue-500');
      }
    });
  });

  it('should handle rapid page changes', () => {
    const onPageChange = vi.fn();

    render(
      <Pagination
        currentPage={1}
        totalPages={10}
        onPageChange={onPageChange}
      />
    );

    const nextButton = screen.getByLabelText('Go to next page');

    fireEvent.click(nextButton);
    fireEvent.click(nextButton);
    fireEvent.click(nextButton);

    expect(onPageChange).toHaveBeenCalledTimes(3);
    expect(onPageChange).toHaveBeenNthCalledWith(1, 2);
    expect(onPageChange).toHaveBeenNthCalledWith(2, 2);
    expect(onPageChange).toHaveBeenNthCalledWith(3, 2);
  });

  it('should be responsive on different screen sizes', () => {
    const onPageChange = vi.fn();

    const { container } = render(
      <Pagination
        currentPage={1}
        totalPages={5}
        onPageChange={onPageChange}
      />
    );

    // Check for responsive padding classes
    const buttons = container.querySelectorAll('button');
    expect(buttons.length).toBeGreaterThan(0);

    buttons.forEach((button) => {
      // Buttons should have padding
      expect(button).toHaveClass('px-4', 'py-2');
    });
  });
});
