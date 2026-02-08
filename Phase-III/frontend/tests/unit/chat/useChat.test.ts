// [Task]: T353, [From]: specs/004-ai-chatbot/spec.md
// useChat Hook Tests

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useChat } from '@/hooks/useChat';
import * as chatApiService from '@/services/chatApiService';

// Mock the chatApiService
vi.mock('@/services/chatApiService', () => ({
  chatApiService: {
    createConversation: vi.fn(),
    listConversations: vi.fn(),
    getMessageHistory: vi.fn(),
    sendMessage: vi.fn(),
    deleteConversation: vi.fn(),
    deleteMessage: vi.fn()
  }
}));

describe('useChat Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('should initialize with empty state', () => {
    const { result } = renderHook(() => useChat({ autoLoadConversations: false, autoLoadMessages: false }));

    expect(result.current.conversations).toEqual([]);
    expect(result.current.activeConversationId).toBeNull();
    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should create a new conversation', async () => {
    const mockConversation = {
      id: '123',
      user_id: '456',
      title: 'Test Conversation',
      message_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    vi.mocked(chatApiService.chatApiService.createConversation).mockResolvedValueOnce(mockConversation);

    const { result } = renderHook(() => useChat({ autoLoadConversations: false, autoLoadMessages: false }));

    let newConv;
    await act(async () => {
      newConv = await result.current.createConversation('Test Conversation');
    });

    expect(newConv).toBeDefined();
    expect(result.current.activeConversationId).toBe('123');
    expect(result.current.conversations[0].title).toBe('Test Conversation');
  });

  it('should load conversations', async () => {
    const mockResponse = {
      conversations: [
        {
          id: '123',
          user_id: '456',
          title: 'Conv 1',
          message_count: 5,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ],
      total: 1,
      limit: 20,
      offset: 0
    };

    vi.mocked(chatApiService.chatApiService.listConversations).mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => useChat({ autoLoadConversations: false, autoLoadMessages: false }));

    await act(async () => {
      await result.current.refetchConversations();
    });

    expect(result.current.conversations).toHaveLength(1);
    expect(result.current.conversations[0].title).toBe('Conv 1');
  });

  it('should select a conversation', async () => {
    const { result } = renderHook(() => useChat({ autoLoadConversations: false, autoLoadMessages: false }));

    await act(async () => {
      await result.current.selectConversation('123');
    });

    expect(result.current.activeConversationId).toBe('123');
  });

  it('should send a message', async () => {
    const mockResponse = {
      id: 'msg-123',
      role: 'assistant',
      content: 'Hello!',
      created_at: new Date().toISOString()
    };

    vi.mocked(chatApiService.chatApiService.sendMessage).mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => useChat({ autoLoadConversations: false, autoLoadMessages: false }));

    await act(async () => {
      await result.current.selectConversation('conv-123');
    });

    let response;
    await act(async () => {
      response = await result.current.sendMessage('Test message');
    });

    expect(response).toBeDefined();
    expect(response?.content).toBe('Hello!');
  });

  it('should delete a conversation', async () => {
    vi.mocked(chatApiService.chatApiService.deleteConversation).mockResolvedValueOnce(undefined);

    const mockConversation = {
      id: '123',
      user_id: '456',
      title: 'To Delete',
      message_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    vi.mocked(chatApiService.chatApiService.listConversations).mockResolvedValueOnce({
      conversations: [mockConversation],
      total: 1,
      limit: 20,
      offset: 0
    });

    const { result } = renderHook(() => useChat({ autoLoadConversations: false, autoLoadMessages: false }));

    await act(async () => {
      await result.current.refetchConversations();
    });

    expect(result.current.conversations).toHaveLength(1);

    await act(async () => {
      await result.current.deleteConversation('123');
    });

    expect(result.current.conversations).toHaveLength(0);
  });

  it('should handle API errors', async () => {
    const error = new Error('API Error');
    vi.mocked(chatApiService.chatApiService.listConversations).mockRejectedValueOnce(error);

    const { result } = renderHook(() => useChat({ autoLoadConversations: false, autoLoadMessages: false }));

    await act(async () => {
      await result.current.refetchConversations();
    });

    expect(result.current.error).toBeDefined();
    expect(result.current.conversations).toEqual([]);
  });

  it('should clear error after timeout', async () => {
    vi.useFakeTimers();
    const { result } = renderHook(() => useChat({ autoLoadConversations: false, autoLoadMessages: false }));

    await act(async () => {
      result.current.setError('Test error');
    });

    expect(result.current.error).toBe('Test error');

    await act(async () => {
      vi.advanceTimersByTime(5000);
    });

    expect(result.current.error).toBeNull();

    vi.useRealTimers();
  });

  it('should persist active conversation ID to localStorage', async () => {
    const { result } = renderHook(() => useChat({ autoLoadConversations: false, autoLoadMessages: false }));

    await act(async () => {
      await result.current.selectConversation('stored-conv-123');
    });

    expect(localStorage.getItem('evolution_active_conversation_id')).toBe('stored-conv-123');
  });
});
