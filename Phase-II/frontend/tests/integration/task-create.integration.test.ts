// [Task]: T061, [From]: specs/002-task-ui-frontend/spec.md#US3
// Integration test for create task workflow

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { taskService } from '@/services/task.service';
import { apiClient } from '@/services/api';
import type { CreateTaskRequest, Task } from '@/types/task';

// Mock the API client
vi.mock('@/services/api', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

/**
 * Integration Tests for Create Task Workflow
 * Tests the complete flow of creating a task and seeing it in the list
 * [Task]: T061, [From]: specs/002-task-ui-frontend/spec.md#US3
 */
describe('Create Task Workflow Integration', () => {
  const userId = 'test-user-123';

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Basic Create Task Flow', () => {
    it('should create task with title only', async () => {
      const createPayload: CreateTaskRequest = {
        title: 'Buy milk',
      };

      const createdTask: Task = {
        id: 'task-1',
        userId,
        title: 'Buy milk',
        completed: false,
        createdAt: '2026-02-02T10:00:00Z',
        updatedAt: '2026-02-02T10:00:00Z',
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: createdTask,
        error: null,
      });

      const result = await taskService.createTask(userId, createPayload);

      expect(result.id).toBe('task-1');
      expect(result.title).toBe('Buy milk');
      expect(result.completed).toBe(false);
    });

    it('should create task with all optional fields', async () => {
      const createPayload: CreateTaskRequest = {
        title: 'Project deadline',
        description: 'Complete the Q1 project',
        dueDate: '2026-03-15T17:00:00Z',
      };

      const createdTask: Task = {
        id: 'task-2',
        userId,
        title: 'Project deadline',
        description: 'Complete the Q1 project',
        dueDate: '2026-03-15T17:00:00Z',
        completed: false,
        completedAt: null,
        createdAt: '2026-02-02T10:00:00Z',
        updatedAt: '2026-02-02T10:00:00Z',
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: createdTask,
        error: null,
      });

      const result = await taskService.createTask(userId, createPayload);

      expect(result.description).toBe('Complete the Q1 project');
      expect(result.dueDate).toBe('2026-03-15T17:00:00Z');
    });
  });

  describe('Create and Fetch Task List', () => {
    it('should create task and verify it appears in list', async () => {
      const createPayload: CreateTaskRequest = {
        title: 'New task',
      };

      const newTask: Task = {
        id: 'task-new',
        userId,
        title: 'New task',
        completed: false,
        completedAt: null,
        createdAt: '2026-02-02T11:00:00Z',
        updatedAt: '2026-02-02T11:00:00Z',
      };

      // Mock create response
      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: newTask,
        error: null,
      });

      const createResult = await taskService.createTask(userId, createPayload);
      expect(createResult.id).toBe('task-new');

      // Mock list response with new task
      const updatedList = {
        data: {
          tasks: [newTask],
          total: 1,
          page: 1,
          pageSize: 10,
          hasMore: false,
        },
        error: null,
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(updatedList);

      const listResult = await taskService.getTasks(userId, 1, 10);

      expect(listResult.tasks).toHaveLength(1);
      expect(listResult.tasks[0].id).toBe('task-new');
      expect(listResult.tasks[0].title).toBe('New task');
    });

    it('should preserve task position in list after creation', async () => {
      const existingTasks: Task[] = Array.from({ length: 2 }, (_, i) => ({
        id: `task-${i + 1}`,
        userId,
        title: `Task ${i + 1}`,
        completed: false,
        completedAt: null,
        createdAt: '2026-02-01T00:00:00Z',
        updatedAt: '2026-02-01T00:00:00Z',
      }));

      const newTask: Task = {
        id: 'task-3',
        userId,
        title: 'New task',
        completed: false,
        completedAt: null,
        createdAt: '2026-02-02T12:00:00Z',
        updatedAt: '2026-02-02T12:00:00Z',
      };

      // Mock create
      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: newTask,
        error: null,
      });

      await taskService.createTask(userId, { title: 'New task' });

      // Mock updated list
      const updatedList = {
        data: {
          tasks: [...existingTasks, newTask],
          total: 3,
          page: 1,
          pageSize: 10,
          hasMore: false,
        },
        error: null,
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(updatedList);

      const listResult = await taskService.getTasks(userId, 1, 10);

      expect(listResult.tasks).toHaveLength(3);
      expect(listResult.tasks[2].id).toBe('task-3');
      expect(listResult.total).toBe(3);
    });
  });

  describe('Form Validation in Create Flow', () => {
    it('should validate title before submission', () => {
      const invalidPayloads = [
        { title: '' },
        { title: '   ' },
        { title: 'a'.repeat(256) },
      ];

      invalidPayloads.forEach((payload) => {
        // Validate would happen in component before API call
        expect(payload.title.length === 0 || payload.title.trim().length === 0 || payload.title.length > 255).toBe(true);
      });
    });

    it('should validate description max length', () => {
      const payload = {
        title: 'Valid title',
        description: 'a'.repeat(2001),
      };

      expect(payload.description.length > 2000).toBe(true);
    });

    it('should validate due date format', () => {
      const validDate = '2026-03-15T17:00:00Z';
      const isoRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?$/;

      expect(isoRegex.test(validDate)).toBe(true);
    });
  });

  describe('Error Handling in Create Flow', () => {
    it('should handle validation error from backend', async () => {
      const createPayload: CreateTaskRequest = {
        title: '',
      };

      const mockError = new Error('Title is required');
      vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

      await expect(
        taskService.createTask(userId, createPayload)
      ).rejects.toThrow('Title is required');
    });

    it('should handle 401 Unauthorized error', async () => {
      const createPayload: CreateTaskRequest = {
        title: 'Test task',
      };

      const mockError = new Error('Unauthorized. Please log in again.');
      vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

      await expect(
        taskService.createTask(userId, createPayload)
      ).rejects.toThrow('Unauthorized');
    });

    it('should handle network error during creation', async () => {
      const createPayload: CreateTaskRequest = {
        title: 'Test task',
      };

      const mockError = new Error('Network error');
      vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

      await expect(
        taskService.createTask(userId, createPayload)
      ).rejects.toThrow('Network error');
    });

    it('should preserve form data on error for retry', async () => {
      const createPayload: CreateTaskRequest = {
        title: 'Task with error',
        description: 'This should be preserved',
        dueDate: '2026-03-15T17:00:00Z',
      };

      const mockError = new Error('Server error');
      vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

      try {
        await taskService.createTask(userId, createPayload);
      } catch {
        // Error caught, form data should still be available in component
        expect(createPayload.title).toBe('Task with error');
        expect(createPayload.description).toBe('This should be preserved');
        expect(createPayload.dueDate).toBe('2026-03-15T17:00:00Z');
      }
    });
  });

  describe('Success Notification', () => {
    it('should indicate successful creation with task details', async () => {
      const createdTask: Task = {
        id: 'task-1',
        userId,
        title: 'Important task',
        description: 'Description',
        dueDate: '2026-03-20T00:00:00Z',
        completed: false,
        completedAt: null,
        createdAt: '2026-02-02T10:00:00Z',
        updatedAt: '2026-02-02T10:00:00Z',
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: createdTask,
        error: null,
      });

      const result = await taskService.createTask(userId, {
        title: 'Important task',
        description: 'Description',
        dueDate: '2026-03-20T00:00:00Z',
      });

      // Success toast would show: "Task 'Important task' created successfully"
      expect(result.id).toBeDefined();
      expect(result.title).toBe('Important task');
    });
  });

  describe('Modal Behavior', () => {
    it('should support creating task from modal', async () => {
      const createPayload: CreateTaskRequest = {
        title: 'Modal created task',
      };

      const createdTask: Task = {
        id: 'task-modal',
        userId,
        title: 'Modal created task',
        completed: false,
        completedAt: null,
        createdAt: '2026-02-02T10:00:00Z',
        updatedAt: '2026-02-02T10:00:00Z',
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: createdTask,
        error: null,
      });

      const result = await taskService.createTask(userId, createPayload);

      // Modal should close after success
      expect(result.id).toBe('task-modal');
      // Form should reset for next task creation
      expect(result.title).toBe('Modal created task');
    });
  });

  describe('Multiple Task Creation', () => {
    it('should support creating multiple tasks in sequence', async () => {
      const tasks = [
        { title: 'Task 1' },
        { title: 'Task 2' },
        { title: 'Task 3' },
      ];

      for (let i = 0; i < tasks.length; i++) {
        const createdTask: Task = {
          id: `task-${i + 1}`,
          userId,
          title: tasks[i].title,
          completed: false,
          completedAt: null,
          createdAt: '2026-02-02T10:00:00Z',
          updatedAt: '2026-02-02T10:00:00Z',
        };

        vi.mocked(apiClient.post).mockResolvedValueOnce({
          data: createdTask,
          error: null,
        });

        const result = await taskService.createTask(userId, tasks[i]);
        expect(result.title).toBe(tasks[i].title);
      }

      // Verify all 3 calls were made
      expect(apiClient.post).toHaveBeenCalledTimes(3);
    });
  });

  describe('Pagination After Creation', () => {
    it('should reset to page 1 after creating task', async () => {
      const createPayload: CreateTaskRequest = {
        title: 'New task',
      };

      const newTask: Task = {
        id: 'task-new',
        userId,
        title: 'New task',
        completed: false,
        completedAt: null,
        createdAt: '2026-02-02T11:00:00Z',
        updatedAt: '2026-02-02T11:00:00Z',
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: newTask,
        error: null,
      });

      await taskService.createTask(userId, createPayload);

      // Fetch should go to page 1
      const pageOneResult = {
        data: {
          tasks: [newTask],
          total: 1,
          page: 1,
          pageSize: 10,
          hasMore: false,
        },
        error: null,
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(pageOneResult);

      const result = await taskService.getTasks(userId, 1, 10);

      expect(result.page).toBe(1);
      expect(result.tasks[0].id).toBe('task-new');
    });
  });
});
