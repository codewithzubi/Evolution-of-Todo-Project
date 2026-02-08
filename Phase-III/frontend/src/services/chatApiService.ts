// [Task]: T349, [From]: specs/004-ai-chatbot/spec.md#T329-T345
// Chat API Service - Wrapper for Phase-III chat endpoints with JWT authentication

import { apiClient } from '@/services/api';
import type {
  ChatRequest,
  ChatResponse,
  ConversationResponse,
  ConversationListResponse,
  PaginatedMessagesResponse
} from '@/types/chat';

/**
 * Helper type for API response wrapper
 */
interface ApiResponse<T> {
  data: T | null;
  error: { code: string; message: string; details: any } | null;
}

/**
 * Chat API Service
 * Handles all chat-related API calls with automatic JWT token injection
 * Provides methods for conversations, messages, and error handling
 */
class ChatApiService {
  private baseUrl = '/api/v1/chat';

  /**
   * Create a new conversation
   * POST /api/v1/chat/conversations
   */
  async createConversation(title?: string): Promise<ConversationResponse> {
    const response = await apiClient.post<ApiResponse<ConversationResponse>>(
      `${this.baseUrl}/conversations`,
      { title }
    );
    if (response.error) {
      throw new Error(response.error.message);
    }
    if (!response.data) {
      throw new Error('No data returned from API');
    }
    return response.data;
  }

  /**
   * List user's conversations with pagination
   * GET /api/v1/chat/conversations
   */
  async listConversations(limit = 20, offset = 0): Promise<ConversationListResponse> {
    const response = await apiClient.get<ApiResponse<ConversationListResponse>>(
      `${this.baseUrl}/conversations`,
      { params: { limit, offset } }
    );
    if (response.error) {
      throw new Error(response.error.message);
    }
    if (!response.data) {
      throw new Error('No data returned from API');
    }
    return response.data;
  }

  /**
   * Get a single conversation
   * GET /api/v1/chat/conversations/{id}
   */
  async getConversation(conversationId: string): Promise<ConversationResponse> {
    const response = await apiClient.get<ApiResponse<ConversationResponse>>(
      `${this.baseUrl}/conversations/${conversationId}`
    );
    if (response.error) {
      throw new Error(response.error.message);
    }
    if (!response.data) {
      throw new Error('No data returned from API');
    }
    return response.data;
  }

  /**
   * Send a message and get AI response
   * POST /api/v1/chat/conversations/{id}/messages
   */
  async sendMessage(
    conversationId: string,
    message: string,
    metadata?: Record<string, any>
  ): Promise<ChatResponse> {
    const body: ChatRequest = {
      message,
      ...(metadata && { metadata }),
    };
    const response = await apiClient.post<ApiResponse<ChatResponse>>(
      `${this.baseUrl}/conversations/${conversationId}/messages`,
      body
    );
    if (response.error) {
      throw new Error(response.error.message);
    }
    if (!response.data) {
      throw new Error('No data returned from API');
    }
    return response.data;
  }

  /**
   * Get message history for a conversation with pagination
   * GET /api/v1/chat/conversations/{id}/messages
   * Default: newest first, limit 20
   */
  async getMessageHistory(
    conversationId: string,
    limit = 20,
    offset = 0
  ): Promise<PaginatedMessagesResponse> {
    const response = await apiClient.get<ApiResponse<PaginatedMessagesResponse>>(
      `${this.baseUrl}/conversations/${conversationId}/messages`,
      { params: { limit, offset } }
    );
    if (response.error) {
      throw new Error(response.error.message);
    }
    if (!response.data) {
      throw new Error('No data returned from API');
    }
    return response.data;
  }

  /**
   * Delete a conversation
   * DELETE /api/v1/chat/conversations/{id}
   */
  async deleteConversation(conversationId: string): Promise<void> {
    return apiClient.delete<void>(
      `${this.baseUrl}/conversations/${conversationId}`
    );
  }

  /**
   * Delete a specific message
   * DELETE /api/v1/chat/conversations/{id}/messages/{messageId}
   */
  async deleteMessage(conversationId: string, messageId: string): Promise<void> {
    return apiClient.delete<void>(
      `${this.baseUrl}/conversations/${conversationId}/messages/${messageId}`
    );
  }
}

// Export singleton instance
export const chatApiService = new ChatApiService();
