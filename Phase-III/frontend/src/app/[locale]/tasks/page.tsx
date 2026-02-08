// [Task]: T049, T067, T068, [From]: specs/002-task-ui-frontend/spec.md#US2
// Task list page with pagination support, task management, and create modal
// [Task]: T067, T068, [From]: specs/002-task-ui-frontend/spec.md#US3

'use client';

import { useState, useEffect, useCallback } from 'react';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { useTasks, useToggleTaskComplete, useDeleteTask } from '@/hooks/useTask';
import { useToast } from '@/components/common/Toast';
import { TaskList } from '@/components/tasks';
import { TaskCreateModal } from '@/components/tasks/TaskCreateModal';
import { TaskEditModal } from '@/components/tasks/TaskEditModal';
import { DeleteConfirmationModal } from '@/components/tasks/DeleteConfirmationModal';
import { Header } from '@/components/layout';
import type { Task } from '@/types/task';

const ITEMS_PER_PAGE = 10;

/**
 * TaskListPage Component
 * Displays paginated list of user's tasks with ability to toggle completion, delete, and create new tasks
 * [Task]: T049, [From]: specs/002-task-ui-frontend/spec.md#US2
 * [Task]: T067, T068, [From]: specs/002-task-ui-frontend/spec.md#US3
 *
 * Features:
 * - Fetches and displays tasks with pagination (10 per page)
 * - Shows loading skeleton while fetching
 * - Shows error state with retry option
 * - Shows empty state when no tasks exist
 * - Allows marking tasks as complete/incomplete
 * - Allows deleting tasks
 * - "Create Task" button opens modal for creating new tasks
 * - Modal closes on successful task creation
 * - Task list refreshes after successful creation
 * - Responsive design for mobile/tablet/desktop
 *
 * @example
 * <TaskListPage />
 */
export default function TaskListPage(): React.ReactNode {
  const pathname = usePathname();
  const { user, isLoading: authLoading } = useAuth();
  const { showToast } = useToast();
  const [currentPage, setCurrentPage] = useState(1);
  const [isCompletingId, setIsCompletingId] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [deleteTaskId, setDeleteTaskId] = useState<string | null>(null);
  const [isDeletingId, setIsDeletingId] = useState<string | null>(null);
  const [editTaskId, setEditTaskId] = useState<string | null>(null);
  const [lastDeletedTaskId, setLastDeletedTaskId] = useState<string | null>(null);

  // Extract locale from pathname (format: /[locale]/tasks)
  const locale = pathname.split('/')[1] || 'en';

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      // Redirect to login with locale
      window.location.href = `/${locale}/auth/login`;
    }
  }, [user, authLoading, locale]);

  // Fetch tasks for current page
  const {
    data: tasksData,
    isLoading: isLoadingTasks,
    error: tasksError,
    refetch: refetchTasks,
  } = useTasks(user?.id || '', currentPage, ITEMS_PER_PAGE);

  // Mutation for toggling task completion
  const { mutate: toggleComplete } = useToggleTaskComplete(user?.id || '');

  // Mutation for deleting task
  const deleteTaskMutation = useDeleteTask(user?.id || '');
  const { mutate: deleteTask, isSuccess: isDeleteSuccess } = deleteTaskMutation;

  // Show toast when task is deleted successfully
  useEffect(() => {
    if (isDeleteSuccess && lastDeletedTaskId) {
      console.log('Delete success detected for task:', lastDeletedTaskId);
      showToast('✓ Task deleted successfully!', 'success', 5000);
      setLastDeletedTaskId(null);
      setIsDeletingId(null);
      // Refetch to update the list
      refetchTasks();
    }
  }, [isDeleteSuccess, lastDeletedTaskId, showToast, refetchTasks]);

  // Handle task completion toggle
  const handleToggleComplete = (taskId: string) => {
    setIsCompletingId(taskId);
    toggleComplete(taskId, {
      onSettled: () => {
        setIsCompletingId(null);
      },
      onError: () => {
        // Error is handled by the mutation hook
      },
    });
  };

  // Handle task deletion - open confirmation modal
  const handleDeleteTask = (taskId: string) => {
    setDeleteTaskId(taskId);
  };

  // Handle delete confirmation
  const handleConfirmDelete = useCallback(() => {
    if (deleteTaskId) {
      setIsDeletingId(deleteTaskId);
      setLastDeletedTaskId(deleteTaskId);
      console.log('Deleting task:', deleteTaskId);
      deleteTask(deleteTaskId);
      setDeleteTaskId(null);
    }
  }, [deleteTaskId, deleteTask]);

  // Handle delete cancellation
  const handleCancelDelete = useCallback(() => {
    setDeleteTaskId(null);
  }, []);

  // Handle task edit - open edit modal
  const handleEditTask = (taskId: string) => {
    setEditTaskId(taskId);
  };

  // Handle edit modal close
  const handleCloseEditModal = useCallback(() => {
    setEditTaskId(null);
  }, []);

  // Handle successful task edit
  const handleTaskUpdated = useCallback((_task: Task) => {
    setEditTaskId(null);
    // Refetch task list to show updated data
    refetchTasks();
  }, [refetchTasks]);

  // Handle page change
  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
    // Scroll to top for better UX
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Handle retry on error
  const handleRetry = () => {
    refetchTasks();
  };

  // Handle create modal open
  const handleOpenCreateModal = useCallback(() => {
    setIsCreateModalOpen(true);
  }, []);

  // Handle create modal close
  const handleCloseCreateModal = useCallback(() => {
    setIsCreateModalOpen(false);
  }, []);

  // Handle successful task creation
  const handleTaskCreated = useCallback((_task: Task) => {
    // Reset to page 1 to see newly created task
    setCurrentPage(1);
    // Close modal (already closed by modal component)
    handleCloseCreateModal();
    // Refetch task list
    refetchTasks();
  }, [refetchTasks, handleCloseCreateModal]);

  if (authLoading) {
    return (
      <div className="min-h-screen bg-white">
        <Header />
        <div className="flex items-center justify-center h-96">
          <div className="text-gray-500">Loading...</div>
        </div>
      </div>
    );
  }

  const tasks = tasksData?.tasks || [];
  const total = tasksData?.total || 0;
  const totalPages = Math.ceil(total / ITEMS_PER_PAGE);

  // Find the task being deleted to get its title
  const taskBeingDeleted = deleteTaskId ? tasks.find((t) => t.id === deleteTaskId) : null;

  // Find the task being edited
  const taskBeingEdited = editTaskId ? tasks.find((t) => t.id === editTaskId) : null;

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <Header />

      {/* Create Task Modal */}
      {user && (
        <TaskCreateModal
          isOpen={isCreateModalOpen}
          userId={user.id}
          onClose={handleCloseCreateModal}
          onSuccess={handleTaskCreated}
        />
      )}

      {/* Delete Confirmation Modal */}
      <DeleteConfirmationModal
        isOpen={deleteTaskId !== null}
        taskTitle={taskBeingDeleted?.title || ''}
        isDeleting={isDeletingId === deleteTaskId}
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
      />

      {/* Edit Task Modal */}
      {user && taskBeingEdited && (
        <TaskEditModal
          isOpen={editTaskId !== null}
          task={taskBeingEdited}
          userId={user.id}
          onClose={handleCloseEditModal}
          onSuccess={handleTaskUpdated}
        />
      )}

      {/* Main Content */}
      <main className="container mx-auto max-w-4xl px-4 py-8">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
            <p className="text-gray-600 mt-1">
              {total === 0 ? 'No tasks yet' : `${total} task${total !== 1 ? 's' : ''}`}
            </p>
          </div>
          <button
            type="button"
            onClick={handleOpenCreateModal}
            className="w-full sm:w-auto px-6 py-2.5 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 transition-colors text-center focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            aria-label="Open create task modal"
          >
            Create Task
          </button>
        </div>

        {/* Task List */}
        <TaskList
          tasks={tasks}
          isLoading={isLoadingTasks}
          error={tasksError}
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={handlePageChange}
          onComplete={handleToggleComplete}
          onEdit={handleEditTask}
          onDelete={handleDeleteTask}
          onRetry={handleRetry}
          isCompletingId={isCompletingId || undefined}
        />
      </main>
    </div>
  );
}
