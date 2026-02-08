// [Task]: T059, [From]: specs/002-task-ui-frontend/spec.md#US3
// Contract tests for POST /api/users/{id}/tasks endpoint

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { taskService } from '@/services/task.service';
import { apiClient } from '@/services/api';
import type { CreateTaskRequest } from '@/types/task';

// Mock the API client
vi.mock('@/services/api', () => ({
  apiClient: {
    post: vi.fn(),
  },
}));

describe('Task Create Endpoint Contract', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should create task with title and return correct schema', async () => {
    const userId = 'user123';
    const createPayload: CreateTaskRequest = {
      title: 'Buy groceries',
    };

    const mockResponse = {
      data: {
        id: 'task-1',
        userId,
        title: 'Buy groceries',
        description: undefined,
        dueDate: undefined,
        completed: false,
        completedAt: null,
        createdAt: '2026-02-02T10:00:00Z',
        updatedAt: '2026-02-02T10:00:00Z',
      },
      error: null,
    };

    vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

    const result = await taskService.createTask(userId, createPayload);

    expect(result).toEqual(mockResponse.data);
    expect(result.id).toBeDefined();
    expect(result.userId).toBe(userId);
    expect(result.title).toBe('Buy groceries');
    expect(result.completed).toBe(false);
    expect(result.createdAt).toBeDefined();
    expect(result.updatedAt).toBeDefined();
  });

  it('should create task with title, description, and due date', async () => {
    const userId = 'user123';
    const createPayload: CreateTaskRequest = {
      title: 'Project deadline',
      description: 'Complete the Q1 project',
      dueDate: '2026-03-15T00:00:00Z',
    };

    const mockResponse = {
      data: {
        id: 'task-2',
        userId,
        title: 'Project deadline',
        description: 'Complete the Q1 project',
        dueDate: '2026-03-15T00:00:00Z',
        completed: false,
        completedAt: null,
        createdAt: '2026-02-02T10:00:00Z',
        updatedAt: '2026-02-02T10:00:00Z',
      },
      error: null,
    };

    vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

    const result = await taskService.createTask(userId, createPayload);

    expect(result.description).toBe('Complete the Q1 project');
    expect(result.dueDate).toBe('2026-03-15T00:00:00Z');
  });

  it('should verify task creation endpoint is called with correct path', async () => {
    const userId = 'user456';
    const createPayload: CreateTaskRequest = {
      title: 'Test task',
    };

    const mockResponse = {
      data: {
        id: 'task-3',
        userId,
        title: 'Test task',
        completed: false,
        completedAt: null,
        createdAt: '2026-02-02T10:00:00Z',
        updatedAt: '2026-02-02T10:00:00Z',
      },
      error: null,
    };

    vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

    await taskService.createTask(userId, createPayload);

    expect(apiClient.post).toHaveBeenCalledWith(
      `/api/users/${userId}/tasks`,
      createPayload
    );
  });

  it('should return 201 Created status on success', async () => {
    const userId = 'user123';
    const createPayload: CreateTaskRequest = {
      title: 'New task',
    };

    const mockResponse = {
      data: {
        id: 'task-4',
        userId,
        title: 'New task',
        completed: false,
        completedAt: null,
        createdAt: '2026-02-02T10:00:00Z',
        updatedAt: '2026-02-02T10:00:00Z',
      },
      error: null,
    };

    vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

    const result = await taskService.createTask(userId, createPayload);

    expect(result).toBeDefined();
    expect(result.id).toBeDefined();
    expect(result.createdAt).toBeDefined();
  });

  it('should return 400 Bad Request when title is missing', async () => {
    const userId = 'user123';
    const createPayload: CreateTaskRequest = {
      title: '',
    };

    const mockError = new Error('Title is required and cannot be empty');
    vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

    await expect(
      taskService.createTask(userId, createPayload)
    ).rejects.toThrow('Title is required');
  });

  it('should return 400 Bad Request when title exceeds max length', async () => {
    const userId = 'user123';
    const longTitle = 'a'.repeat(256); // Exceeds 255 character limit
    const createPayload: CreateTaskRequest = {
      title: longTitle,
    };

    const mockError = new Error(
      'Title must be less than 255 characters'
    );
    vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

    await expect(
      taskService.createTask(userId, createPayload)
    ).rejects.toThrow('Title must be less than 255 characters');
  });

  it('should return 400 Bad Request when description exceeds max length', async () => {
    const userId = 'user123';
    const longDescription = 'a'.repeat(2001); // Exceeds 2000 character limit
    const createPayload: CreateTaskRequest = {
      title: 'Valid title',
      description: longDescription,
    };

    const mockError = new Error(
      'Description must be less than 2000 characters'
    );
    vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

    await expect(
      taskService.createTask(userId, createPayload)
    ).rejects.toThrow('Description must be less than 2000 characters');
  });

  it('should return 401 Unauthorized when no authentication token provided', async () => {
    const userId = 'user123';
    const createPayload: CreateTaskRequest = {
      title: 'Test task',
    };

    const mockError = new Error('Unauthorized. Please log in again.');
    vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

    await expect(
      taskService.createTask(userId, createPayload)
    ).rejects.toThrow('Unauthorized');
  });

  it('should return 403 Forbidden when creating task for another user', async () => {
    const userId = 'other-user';
    const createPayload: CreateTaskRequest = {
      title: 'Hacked task',
    };

    const mockError = new Error(
      'Forbidden. You do not have permission to create tasks for this user.'
    );
    vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

    await expect(
      taskService.createTask(userId, createPayload)
    ).rejects.toThrow('Forbidden');
  });

  it('should handle 500 Server Error gracefully', async () => {
    const userId = 'user123';
    const createPayload: CreateTaskRequest = {
      title: 'Test task',
    };

    const mockError = new Error('Internal server error');
    vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

    await expect(
      taskService.createTask(userId, createPayload)
    ).rejects.toThrow('Internal server error');
  });
});
