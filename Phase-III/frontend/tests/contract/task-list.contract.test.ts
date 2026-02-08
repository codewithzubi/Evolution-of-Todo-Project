// [Task]: T043, [From]: specs/002-task-ui-frontend/spec.md#US2
// Contract tests for GET /api/users/{id}/tasks endpoint

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { taskService } from '@/services/task.service';
import { apiClient } from '@/services/api';

// Mock the API client
vi.mock('@/services/api', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

describe('Task List Endpoint Contract', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should return paginated tasks list with correct schema', async () => {
    const mockResponse = {
      data: {
        tasks: [
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
            description: null,
            dueDate: null,
            completed: true,
            completedAt: '2026-02-02T00:00:00Z',
            createdAt: '2026-02-01T00:00:00Z',
            updatedAt: '2026-02-02T00:00:00Z',
          },
        ],
        total: 15,
        page: 1,
        pageSize: 10,
        hasMore: true,
      },
      error: null,
    };

    vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

    const result = await taskService.getTasks('user123', 1, 10);

    expect(result).toEqual(mockResponse.data);
    expect(result.tasks).toHaveLength(2);
    expect(result.total).toBe(15);
    expect(result.page).toBe(1);
    expect(result.pageSize).toBe(10);
    expect(result.hasMore).toBe(true);
  });

  it('should verify task data structure contains all required fields', async () => {
    const mockResponse = {
      data: {
        tasks: [
          {
            id: '1',
            userId: 'user123',
            title: 'Sample Task',
            description: 'Sample Description',
            dueDate: '2026-02-10T00:00:00Z',
            completed: false,
            completedAt: null,
            createdAt: '2026-02-01T00:00:00Z',
            updatedAt: '2026-02-01T00:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        pageSize: 10,
        hasMore: false,
      },
      error: null,
    };

    vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

    const result = await taskService.getTasks('user123', 1, 10);
    const task = result.tasks[0];

    // Verify all required fields are present
    expect(task).toHaveProperty('id');
    expect(task).toHaveProperty('userId');
    expect(task).toHaveProperty('title');
    expect(task).toHaveProperty('description');
    expect(task).toHaveProperty('dueDate');
    expect(task).toHaveProperty('completed');
    expect(task).toHaveProperty('completedAt');
    expect(task).toHaveProperty('createdAt');
    expect(task).toHaveProperty('updatedAt');
  });

  it('should pass offset and limit parameters correctly to API', async () => {
    const mockResponse = {
      data: {
        tasks: [],
        total: 100,
        page: 2,
        pageSize: 10,
        hasMore: true,
      },
      error: null,
    };

    vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

    await taskService.getTasks('user123', 2, 10);

    expect(apiClient.get).toHaveBeenCalledWith('/api/users/user123/tasks', {
      params: {
        offset: 10, // (2-1) * 10
        limit: 10,
      },
    });
  });

  it('should handle pagination with different page numbers', async () => {
    const mockResponse = {
      data: {
        tasks: [],
        total: 50,
        page: 3,
        pageSize: 10,
        hasMore: false,
      },
      error: null,
    };

    vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

    await taskService.getTasks('user123', 3, 10);

    expect(apiClient.get).toHaveBeenCalledWith('/api/users/user123/tasks', {
      params: {
        offset: 20, // (3-1) * 10
        limit: 10,
      },
    });
  });

  it('should return empty list when user has no tasks', async () => {
    const mockResponse = {
      data: {
        tasks: [],
        total: 0,
        page: 1,
        pageSize: 10,
        hasMore: false,
      },
      error: null,
    };

    vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

    const result = await taskService.getTasks('user123', 1, 10);

    expect(result.tasks).toHaveLength(0);
    expect(result.total).toBe(0);
    expect(result.hasMore).toBe(false);
  });

  it('should handle 401 Unauthorized error when no token is provided', async () => {
    const mockError = new Error('Unauthorized. Please log in again.');
    vi.mocked(apiClient.get).mockRejectedValueOnce(mockError);

    await expect(taskService.getTasks('user123', 1, 10)).rejects.toThrow(
      'Unauthorized'
    );
  });

  it('should handle 403 Forbidden error when accessing another user\'s tasks', async () => {
    const mockError = new Error(
      'Forbidden. You do not have permission to access this resource.'
    );
    vi.mocked(apiClient.get).mockRejectedValueOnce(mockError);

    await expect(taskService.getTasks('other-user', 1, 10)).rejects.toThrow(
      'Forbidden'
    );
  });
});
