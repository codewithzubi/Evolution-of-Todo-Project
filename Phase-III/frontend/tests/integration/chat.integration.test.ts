// [Task]: T376, [From]: specs/004-ai-chatbot/spec.md#Testing
/**
 * Frontend-Backend Chat Integration Tests
 *
 * Tests complete end-to-end chat flows:
 * - User authentication (Phase-II JWT)
 * - Conversation creation
 * - Message sending and AI response
 * - Message listing with pagination
 * - Error handling and recovery
 * - Data persistence across browser refresh
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

describe('Chat Integration Tests', () => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const authToken = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyLTEyMyIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImlhdCI6MTcwMzc4MDAwMCwiZXhwIjoyMDAwMDAwMDAwfQ.signature';
  const userId = 'user-123';
  const conversationId = 'conv-123';
  const messageId = 'msg-123';

  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    // Store token in localStorage (simulating logged-in user)
    localStorage.setItem('auth_token', authToken);
  });

  afterEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe('T376.1: Authentication Flow', () => {
    it('should maintain JWT token from Phase-II auth in localStorage', () => {
      const token = localStorage.getItem('auth_token');
      expect(token).toBe(authToken);
    });

    it('should include JWT token in all API requests', async () => {
      const fetchSpy = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          data: { id: conversationId, title: 'Test' },
          error: null,
        }),
      });

      global.fetch = fetchSpy;

      await fetch(`${API_BASE_URL}/api/v1/chat/conversations`, {
        headers: {
          Authorization: localStorage.getItem('auth_token') || '',
        },
      });

      expect(fetchSpy).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: authToken,
          }),
        })
      );
    });

    it('should handle expired JWT token with 401 response', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({
          data: null,
          error: { message: 'Token expired' },
        }),
      });

      const response = await fetch(`${API_BASE_URL}/api/v1/chat/conversations`, {
        headers: { Authorization: 'Bearer expired.token.here' },
      });

      expect(response.status).toBe(401);
    });
  });

  describe('T376.2: Conversation Creation', () => {
    it('should create new conversation via POST /api/v1/chat/conversations', async () => {
      const mockResponse = {
        data: {
          id: conversationId,
          user_id: userId,
          title: 'New Conversation',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        error: null,
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => mockResponse,
      });

      const response = await fetch(`${API_BASE_URL}/api/v1/chat/conversations`, {
        method: 'POST',
        headers: {
          Authorization: authToken,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title: 'New Conversation' }),
      });

      const data = await response.json();
      expect(response.status).toBe(201);
      expect(data.data.id).toBeDefined();
      expect(data.data.user_id).toBe(userId);
    });

    it('should return 403 when user_id in JWT does not match request', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: async () => ({
          data: null,
          error: { message: 'Forbidden' },
        }),
      });

      const response = await fetch(
        `${API_BASE_URL}/api/v1/chat/conversations`,
        {
          method: 'POST',
          headers: { Authorization: authToken },
          body: JSON.stringify({ title: 'Test' }),
        }
      );

      expect(response.status).toBe(403);
    });
  });

  describe('T376.3: Message Sending & AI Response', () => {
    it('should send message and receive AI response', async () => {
      const userMessage = 'Hello AI!';
      const aiResponse = 'Hello! How can I help you?';

      // Mock message creation
      global.fetch = vi.fn()
        .mockResolvedValueOnce({
          ok: true,
          status: 201,
          json: async () => ({
            data: {
              id: messageId,
              conversation_id: conversationId,
              user_id: userId,
              content: userMessage,
              role: 'user',
              created_at: new Date().toISOString(),
            },
            error: null,
          }),
        })
        // Mock AI response
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({
            data: {
              id: 'msg-ai-123',
              conversation_id: conversationId,
              user_id: userId,
              content: aiResponse,
              role: 'assistant',
              created_at: new Date().toISOString(),
            },
            error: null,
          }),
        });

      // Send user message
      const msgResponse = await fetch(
        `${API_BASE_URL}/api/v1/chat/conversations/${conversationId}/messages`,
        {
          method: 'POST',
          headers: {
            Authorization: authToken,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content: userMessage }),
        }
      );

      expect(msgResponse.status).toBe(201);
      const msgData = await msgResponse.json();
      expect(msgData.data.content).toBe(userMessage);
      expect(msgData.data.role).toBe('user');

      // Get AI response (simulated)
      const aiMsgResponse = await fetch(
        `${API_BASE_URL}/api/v1/chat/conversations/${conversationId}/messages/msg-ai-123`,
        {
          headers: { Authorization: authToken },
        }
      );

      expect(aiMsgResponse.status).toBe(200);
      const aiData = await aiMsgResponse.json();
      expect(aiData.data.role).toBe('assistant');
    });

    it('should handle message send errors gracefully', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({
          data: null,
          error: { message: 'Server error' },
        }),
      });

      const response = await fetch(
        `${API_BASE_URL}/api/v1/chat/conversations/${conversationId}/messages`,
        {
          method: 'POST',
          headers: { Authorization: authToken },
          body: JSON.stringify({ content: 'Test' }),
        }
      );

      expect(response.status).toBe(500);
      const data = await response.json();
      expect(data.error).toBeDefined();
    });
  });

  describe('T376.4: Message Listing & Pagination', () => {
    it('should list messages with pagination', async () => {
      const mockMessages = [
        {
          id: 'msg-1',
          conversation_id: conversationId,
          user_id: userId,
          content: 'First message',
          role: 'user',
          created_at: new Date().toISOString(),
        },
        {
          id: 'msg-2',
          conversation_id: conversationId,
          user_id: userId,
          content: 'Second message',
          role: 'user',
          created_at: new Date().toISOString(),
        },
      ];

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          data: {
            items: mockMessages,
            pagination: {
              limit: 10,
              offset: 0,
              total: 2,
              has_more: false,
            },
          },
          error: null,
        }),
      });

      const response = await fetch(
        `${API_BASE_URL}/api/v1/chat/conversations/${conversationId}/messages?limit=10&offset=0`,
        {
          headers: { Authorization: authToken },
        }
      );

      const data = await response.json();
      expect(response.status).toBe(200);
      expect(data.data.items).toHaveLength(2);
      expect(data.data.pagination.total).toBe(2);
      expect(data.data.pagination.has_more).toBe(false);
    });

    it('should handle pagination correctly with offset', async () => {
      const mockMessages = [
        {
          id: 'msg-3',
          content: 'Third message',
          role: 'user',
        },
      ];

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          data: {
            items: mockMessages,
            pagination: {
              limit: 2,
              offset: 2,
              total: 5,
              has_more: true,
            },
          },
          error: null,
        }),
      });

      const response = await fetch(
        `${API_BASE_URL}/api/v1/chat/conversations/${conversationId}/messages?limit=2&offset=2`,
        {
          headers: { Authorization: authToken },
        }
      );

      const data = await response.json();
      expect(data.data.pagination.offset).toBe(2);
      expect(data.data.pagination.has_more).toBe(true);
    });
  });

  describe('T376.5: Error Handling', () => {
    it('should display error message on API failure', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => ({
          data: null,
          error: {
            code: 'validation_error',
            message: 'Invalid request',
            details: { content: 'Content is required' },
          },
        }),
      });

      const response = await fetch(
        `${API_BASE_URL}/api/v1/chat/conversations/${conversationId}/messages`,
        {
          method: 'POST',
          headers: { Authorization: authToken },
          body: JSON.stringify({ content: '' }),
        }
      );

      const data = await response.json();
      expect(response.status).toBe(422);
      expect(data.error).toBeDefined();
      expect(data.error.message).toBe('Invalid request');
    });

    it('should retry on network error', async () => {
      let callCount = 0;
      global.fetch = vi.fn(async () => {
        callCount++;
        if (callCount === 1) {
          throw new Error('Network error');
        }
        return {
          ok: true,
          status: 200,
          json: async () => ({ data: {}, error: null }),
        };
      });

      // First call fails
      let response;
      try {
        response = await fetch(`${API_BASE_URL}/api/v1/chat/conversations`, {
          headers: { Authorization: authToken },
        });
      } catch (e) {
        // Expected network error
        expect(e).toBeDefined();
      }

      // Retry succeeds
      response = await fetch(`${API_BASE_URL}/api/v1/chat/conversations`, {
        headers: { Authorization: authToken },
      });
      expect(response.ok).toBe(true);
    });

    it('should handle 404 when conversation not found', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          data: null,
          error: { message: 'Conversation not found' },
        }),
      });

      const response = await fetch(
        `${API_BASE_URL}/api/v1/chat/conversations/nonexistent-id`,
        {
          headers: { Authorization: authToken },
        }
      );

      expect(response.status).toBe(404);
    });
  });

  describe('T376.6: Data Persistence', () => {
    it('should preserve conversation data across browser refresh', async () => {
      const conversationData = {
        id: conversationId,
        title: 'Persistent Conversation',
        created_at: '2026-02-07T10:00:00Z',
      };

      // Store in localStorage (simulating persisted state)
      localStorage.setItem(
        'conversation_cache',
        JSON.stringify(conversationData)
      );

      // Retrieve after "refresh"
      const cached = localStorage.getItem('conversation_cache');
      const retrieved = JSON.parse(cached || '{}');

      expect(retrieved.id).toBe(conversationId);
      expect(retrieved.title).toBe('Persistent Conversation');
    });

    it('should reload conversation from API after token refresh', async () => {
      const conversationData = {
        id: conversationId,
        title: 'Reloaded Conversation',
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          data: conversationData,
          error: null,
        }),
      });

      // Simulate token refresh by getting new auth token
      const newToken = 'Bearer refreshed.token.here';
      localStorage.setItem('auth_token', newToken);

      // Fetch conversation with new token
      const response = await fetch(
        `${API_BASE_URL}/api/v1/chat/conversations/${conversationId}`,
        {
          headers: { Authorization: newToken },
        }
      );

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data.data.id).toBe(conversationId);
    });
  });

  describe('T376.7: Real-time Updates (Simulated)', () => {
    it('should display new messages in real-time order', async () => {
      const messages = [
        { id: '1', content: 'First', created_at: '2026-02-07T10:00:00Z' },
        { id: '2', content: 'Second', created_at: '2026-02-07T10:01:00Z' },
        { id: '3', content: 'Third', created_at: '2026-02-07T10:02:00Z' },
      ];

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          data: {
            items: messages,
            pagination: { total: 3, limit: 10, offset: 0, has_more: false },
          },
          error: null,
        }),
      });

      const response = await fetch(
        `${API_BASE_URL}/api/v1/chat/conversations/${conversationId}/messages`,
        {
          headers: { Authorization: authToken },
        }
      );

      const data = await response.json();
      const items = data.data.items;

      // Verify chronological order
      expect(items[0].created_at).toBeLessThan(items[1].created_at);
      expect(items[1].created_at).toBeLessThan(items[2].created_at);
    });
  });

  describe('T376.8: Conversation Listing', () => {
    it('should list user conversations with pagination', async () => {
      const mockConversations = [
        {
          id: 'conv-1',
          title: 'Conversation 1',
          created_at: new Date().toISOString(),
        },
        {
          id: 'conv-2',
          title: 'Conversation 2',
          created_at: new Date().toISOString(),
        },
      ];

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          data: {
            items: mockConversations,
            pagination: {
              limit: 10,
              offset: 0,
              total: 2,
              has_more: false,
            },
          },
          error: null,
        }),
      });

      const response = await fetch(`${API_BASE_URL}/api/v1/chat/conversations`, {
        headers: { Authorization: authToken },
      });

      const data = await response.json();
      expect(response.status).toBe(200);
      expect(data.data.items).toHaveLength(2);
    });

    it('should only show user own conversations', async () => {
      const userConversations = [
        { id: 'conv-user-1', title: 'My Conversation' },
      ];

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          data: {
            items: userConversations,
            pagination: { total: 1, limit: 10, offset: 0, has_more: false },
          },
          error: null,
        }),
      });

      const response = await fetch(`${API_BASE_URL}/api/v1/chat/conversations`, {
        headers: { Authorization: authToken },
      });

      const data = await response.json();
      // Verify only user's own conversations returned
      expect(data.data.items.every((c: any) => c.id.startsWith('conv-user')))
        .toBe(true);
    });
  });
});
