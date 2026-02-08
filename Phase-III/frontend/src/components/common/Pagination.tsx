// [Task]: T052, [From]: specs/002-task-ui-frontend/spec.md#US2
// Pagination component for navigating through paginated results

'use client';

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  isLoading?: boolean;
}

/**
 * Pagination Component
 * Displays page navigation controls with previous/next buttons and page indicator
 * [Task]: T052, [From]: specs/002-task-ui-frontend/spec.md#US2
 *
 * @param currentPage - Current active page (1-based)
 * @param totalPages - Total number of pages available
 * @param onPageChange - Callback fired when page changes
 * @param isLoading - Whether data is currently loading
 *
 * @example
 * <Pagination
 *   currentPage={1}
 *   totalPages={5}
 *   onPageChange={handlePageChange}
 *   isLoading={isLoading}
 * />
 */
export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  isLoading = false,
}: PaginationProps): React.ReactNode {
  const canGoPrevious = currentPage > 1;
  const canGoNext = currentPage < totalPages;

  return (
    <div
      className="flex items-center justify-center gap-2 mt-8"
      role="navigation"
      aria-label="Pagination"
    >
      {/* Previous Button */}
      <button
        type="button"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={!canGoPrevious || isLoading}
        aria-label="Go to previous page"
        className={`
          px-4 py-2 rounded-lg font-medium text-sm
          transition-all
          ${
            canGoPrevious && !isLoading
              ? 'bg-blue-500 text-white hover:bg-blue-600'
              : 'bg-gray-200 text-gray-500 cursor-not-allowed'
          }
        `}
      >
        Previous
      </button>

      {/* Page Indicator */}
      <div className="flex items-center gap-2 px-4">
        <span className="text-gray-700 font-medium">
          Page {currentPage}
        </span>
        <span className="text-gray-500">of</span>
        <span className="text-gray-700 font-medium">{totalPages}</span>
      </div>

      {/* Next Button */}
      <button
        type="button"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={!canGoNext || isLoading}
        aria-label="Go to next page"
        className={`
          px-4 py-2 rounded-lg font-medium text-sm
          transition-all
          ${
            canGoNext && !isLoading
              ? 'bg-blue-500 text-white hover:bg-blue-600'
              : 'bg-gray-200 text-gray-500 cursor-not-allowed'
          }
        `}
      >
        Next
      </button>
    </div>
  );
}
