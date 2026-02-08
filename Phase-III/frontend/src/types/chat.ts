// [Task]: T348-T349, [From]: specs/004-ai-chatbot/spec.md
// Chat type definitions for API responses and component props

import type { UUID } from 'crypto';

/**
 * Chat Request
 * POST body for sending messages
 */
export interface ChatRequest {
  message: string;
  metadata?: Record<string, any>;
}

/**
 * Chat Response
 * AI assistant response from POST /messages
 */
export interface ChatResponse {
  id: string | UUID;
  role: 'assistant';
  content: string;
  tool_calls?: Array<Record<string, any>>;
  tool_results?: Record<string, any>;
  created_at: string | Date;
}

/**
 * Conversation Response
 * Conversation metadata from GET /conversations/{id}
 */
export interface ConversationResponse {
  id: string | UUID;
  user_id: string | UUID;
  title?: string;
  message_count: number;
  last_message_at?: string | Date;
  created_at: string | Date;
  updated_at: string | Date;
}

/**
 * Conversation List Response
 * Paginated conversations from GET /conversations
 */
export interface ConversationListResponse {
  conversations: ConversationResponse[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * Message Response
 * Single message from GET /messages or POST /messages
 */
export interface MessageResponse {
  id: string | UUID;
  conversation_id: string | UUID;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tool_calls?: Array<Record<string, any>>;
  tool_results?: Record<string, any>;
  created_at: string | Date;
}

/**
 * Paginated Messages Response
 * Message history from GET /conversations/{id}/messages
 */
export interface PaginatedMessagesResponse {
  messages: MessageResponse[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * Message Display Model
 * Extended message for UI display with additional properties
 */
export interface Message extends MessageResponse {
  timestamp: Date;
  isLoading?: boolean;
}

/**
 * Conversation Display Model
 * Extended conversation for UI display
 */
export interface Conversation extends ConversationResponse {
  unreadCount?: number;
}

/**
 * Chat State
 * Application state for chat hook
 */
export interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  isDarkMode: boolean;
}

/**
 * Chat Error
 * Error information for error handling
 */
export interface ChatError {
  code: string;
  message: string;
  statusCode?: number;
  timestamp: Date;
}
