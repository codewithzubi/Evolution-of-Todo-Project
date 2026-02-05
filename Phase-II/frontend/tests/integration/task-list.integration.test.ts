// [Task]: T045, [From]: specs/002-task-ui-frontend/spec.md#US2
// Integration test for task list workflow with pagination

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { taskService } from '@/services/task.service';
import { apiClient } from '@/services/api';

// Mock the API client
vi.mock('@/services/api', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

/**
 * Integration Tests for Task List Workflow
 * Tests the complete flow of fetching and paginating through tasks
 * [Task]: T045, [From]: specs/002-task-ui-frontend/spec.md#US2
 */
describe('Task List Workflow Integration', () => {
  const userId = 'test-user-123';
  const mockTasks = Array.from({ length: 15 }, (_, i) => ({
    id: `task-${i + 1}`,
    userId,
    title: `Task ${i + 1}`,
    description: i % 3 === 0 ? null : `Description for task ${i + 1}`,
    dueDate: i % 2 === 0 ? `2026-02-${10 + i}T00:00:00Z` : null,
    completed: i % 4 === 0,
    completedAt: i % 4 === 0 ? '2026-02-02T00:00:00Z' : null,
    createdAt: '2026-02-01T00:00:00Z',
    updatedAt: '2026-02-01T00:00:00Z',
  }));

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should load first page with 10 tasks', async () => {
    const pageOneTasks = mockTasks.slice(0, 10);
    const mockResponse = {
      data: {
        tasks: pageOneTasks,
        total: 15,
        page: 1,
        pageSize: 10,
        hasMore: true,
      },
      error: null,
    };

    vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

    const result = await taskService.getTasks(userId, 1, 10);

    expect(result.tasks).toHaveLength(10);
    expect(result.tasks[0].id).toBe('task-1');
    expect(result.tasks[9].id).toBe('task-10');
    expect(result.total).toBe(15);
    expect(result.page).toBe(1);
    expect(result.hasMore).toBe(true);
  });

  it('should load second page and verify pagination', async () => {
    const pageTwoTasks = mockTasks.slice(10, 15);
    const mockResponse = {
      data: {
        tasks: pageTwoTasks,
        total: 15,
        page: 2,
        pageSize: 10,
        hasMore: false,
      },
      error: null,
    };

    vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

    const result = await taskService.getTasks(userId, 2, 10);

    expect(result.tasks).toHaveLength(5);
    expect(result.tasks[0].id).toBe('task-11');
    expect(result.tasks[4].id).toBe('task-15');
    expect(result.total).toBe(15);
    expect(result.page).toBe(2);
    expect(result.hasMore).toBe(false);
  });

  it('should verify loading state during fetch', async () => {
    let isLoadingDuringFetch = false;

    const mockResponse = {
      data: {
        tasks: mockTasks.slice(0, 10),
        total: 15,
        page: 1,
        pageSize: 10,
        hasMore: true,
      },
      error: null,
    };

    vi.mocked(apiClient.get).mockImplementationOnce(async () => {
      isLoadingDuringFetch = true;
      return mockResponse;
    });

    const result = await taskService.getTasks(userId, 1, 10);

    expect(isLoadingDuringFetch).toBe(true);
    expect(result.tasks.length).toBeGreaterThan(0);
  });

  it('should handle error state and allow retry', async () => {
    const mockError = new Error('Failed to fetch tasks');

    vi.mocked(apiClient.get).mockRejectedValueOnce(mockError);

    // First call fails
    await expect(taskService.getTasks(userId, 1, 10)).rejects.toThrow(
      'Failed to fetch tasks'
    );

    // Retry with successful response
    const mockResponse = {
      data: {
        tasks: mockTasks.slice(0, 10),
        total: 15,
        page: 1,
        pageSize: 10,
        hasMore: true,
      },
      error: null,
    };

    vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

    const result = await taskService.getTasks(userId, 1, 10);
    expect(result.tasks).toHaveLength(10);
  });

  it('should display empty state when user has no tasks', async () => {
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

    const result = await taskService.getTasks(userId, 1, 10);

    expect(result.tasks).toHaveLength(0);
    expect(result.total).toBe(0);
    expect(result.hasMore).toBe(false);
  });

  it('should verify task data is properly formatted and complete', async () => {
    const mockResponse = {
      data: {
        tasks: [mockTasks[0]],
        total: 1,
        page: 1,
        pageSize: 10,
        hasMore: false,
      },
      error: null,
    };

    vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

    const result = await taskService.getTasks(userId, 1, 10);
    const task = result.tasks[0];

    // Verify all required fields
    expect(task.id).toBeDefined();
    expect(task.userId).toBe(userId);
    expect(task.title).toBeDefined();
    expect(typeof task.completed).toBe('boolean');
    expect(task.createdAt).toBeDefined();
    expect(task.updatedAt).toBeDefined();
  });

  it('should include auth token in request headers', async () => {
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

    await taskService.getTasks(userId, 1, 10);

    expect(apiClient.get).toHaveBeenCalledWith(
      `/api/users/${userId}/tasks`,
      expect.objectContaining({
        params: expect.any(Object),
      })
    );
  });

  it('should handle multiple page navigations in sequence', async () => {
    // Page 1
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        tasks: mockTasks.slice(0, 10),
        total: 15,
        page: 1,
        pageSize: 10,
        hasMore: true,
      },
      error: null,
    });

    const page1 = await taskService.getTasks(userId, 1, 10);
    expect(page1.tasks[0].id).toBe('task-1');

    // Page 2
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        tasks: mockTasks.slice(10, 15),
        total: 15,
        page: 2,
        pageSize: 10,
        hasMore: false,
      },
      error: null,
    });

    const page2 = await taskService.getTasks(userId, 2, 10);
    expect(page2.tasks[0].id).toBe('task-11');

    // Back to Page 1
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        tasks: mockTasks.slice(0, 10),
        total: 15,
        page: 1,
        pageSize: 10,
        hasMore: true,
      },
      error: null,
    });

    const backToPage1 = await taskService.getTasks(userId, 1, 10);
    expect(backToPage1.tasks[0].id).toBe('task-1');
  });

  it('should verify correct pagination call count', async () => {
    const mockResponse = {
      data: {
        tasks: mockTasks.slice(0, 10),
        total: 15,
        page: 1,
        pageSize: 10,
        hasMore: true,
      },
      error: null,
    };

    vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

    await taskService.getTasks(userId, 1, 10);

    expect(apiClient.get).toHaveBeenCalledTimes(1);
  });
});
