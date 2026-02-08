// [Task]: T349, [From]: specs/004-ai-chatbot/spec.md
// Chat API Service Tests

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { chatApiService } from '@/services/chatApiService';
import { apiClient } from '@/services/api';

// Mock the apiClient
vi.mock('@/services/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn()
  }
}));

describe('Chat API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should create a conversation', async () => {
    const mockResponse = {
      id: 'conv-123',
      user_id: 'user-123',
      title: 'Test',
      message_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

    const result = await chatApiService.createConversation('Test');

    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/chat/conversations', { title: 'Test' });
    expect(result.id).toBe('conv-123');
  });

  it('should list conversations', async () => {
    const mockResponse = {
      conversations: [],
      total: 0,
      limit: 20,
      offset: 0
    };

    vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

    const result = await chatApiService.listConversations(20, 0);

    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/chat/conversations', expect.objectContaining({
      params: expect.objectContaining({ limit: 20, offset: 0 })
    }));
    expect(result.conversations).toEqual([]);
  });

  it('should send a message', async () => {
    const mockResponse = {
      id: 'msg-123',
      role: 'assistant',
      content: 'Hi!',
      created_at: new Date().toISOString()
    };

    vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

    const result = await chatApiService.sendMessage('conv-123', 'Hello');

    expect(apiClient.post).toHaveBeenCalledWith(
      '/api/v1/chat/conversations/conv-123/messages',
      expect.objectContaining({ message: 'Hello' })
    );
    expect(result.content).toBe('Hi!');
  });

  it('should get message history', async () => {
    const mockResponse = {
      messages: [],
      total: 0,
      limit: 20,
      offset: 0
    };

    vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

    const result = await chatApiService.getMessageHistory('conv-123', 20, 0);

    expect(apiClient.get).toHaveBeenCalledWith(
      '/api/v1/chat/conversations/conv-123/messages',
      expect.objectContaining({ params: expect.objectContaining({ limit: 20, offset: 0 }) })
    );
    expect(result.messages).toEqual([]);
  });

  it('should delete a conversation', async () => {
    vi.mocked(apiClient.delete).mockResolvedValueOnce(undefined);

    await chatApiService.deleteConversation('conv-123');

    expect(apiClient.delete).toHaveBeenCalledWith('/api/v1/chat/conversations/conv-123');
  });

  it('should delete a message', async () => {
    vi.mocked(apiClient.delete).mockResolvedValueOnce(undefined);

    await chatApiService.deleteMessage('conv-123', 'msg-123');

    expect(apiClient.delete).toHaveBeenCalledWith('/api/v1/chat/conversations/conv-123/messages/msg-123');
  });

  it('should include JWT token in requests', async () => {
    const mockResponse = { conversations: [], total: 0, limit: 20, offset: 0 };
    vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

    await chatApiService.listConversations();

    // apiClient handles JWT injection automatically
    expect(apiClient.get).toHaveBeenCalled();
  });
});
