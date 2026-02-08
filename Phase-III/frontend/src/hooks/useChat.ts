// [Task]: T353, [From]: specs/004-ai-chatbot/spec.md
// useChat Hook - Custom hook for chat state management and API integration

'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { chatApiService } from '@/services/chatApiService';
import type {
  Conversation,
  Message,
  ChatState
} from '@/types/chat';

interface UseChatOptions {
  autoLoadConversations?: boolean;
  autoLoadMessages?: boolean;
  storageKey?: string;
}

/**
 * useChat Hook
 * Manages chat state, conversations, and messages
 * Integrates with ChatApiService for API calls
 */
export function useChat(options: UseChatOptions = {}) {
  const {
    autoLoadConversations = true,
    autoLoadMessages = true,
    storageKey = 'evolution_active_conversation_id'
  } = options;

  const [state, setState] = useState<ChatState>({
    conversations: [],
    activeConversationId: null,
    messages: [],
    isLoading: false,
    error: null,
    isDarkMode: false
  });

  const errorTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const loadingRef = useRef(false);

  // Check for dark mode preference
  useEffect(() => {
    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setState(prev => ({ ...prev, isDarkMode: isDark }));
  }, []);

  /**
   * Clear error message after 5 seconds
   */
  useEffect(() => {
    if (state.error) {
      errorTimeoutRef.current = setTimeout(() => {
        setState(prev => ({ ...prev, error: null }));
      }, 5000);
    }
    return () => {
      if (errorTimeoutRef.current) clearTimeout(errorTimeoutRef.current);
    };
  }, [state.error]);

  /**
   * Load stored conversation ID from localStorage
   */
  useEffect(() => {
    try {
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        setState(prev => ({ ...prev, activeConversationId: stored }));
      }
    } catch (err) {
      console.warn('Failed to load stored conversation ID:', err);
    }
  }, [storageKey]);

  /**
   * Auto-load conversations on mount or when switching conversations
   */
  useEffect(() => {
    if (autoLoadConversations && !loadingRef.current) {
      refetchConversations();
    }
  }, [autoLoadConversations]);

  /**
   * Auto-load messages when active conversation changes
   */
  useEffect(() => {
    if (autoLoadMessages && state.activeConversationId && !loadingRef.current) {
      loadMessages();
    }
  }, [state.activeConversationId, autoLoadMessages]);

  /**
   * Save active conversation ID to localStorage when it changes
   */
  useEffect(() => {
    try {
      if (state.activeConversationId) {
        localStorage.setItem(storageKey, state.activeConversationId);
      } else {
        localStorage.removeItem(storageKey);
      }
    } catch (err) {
      console.warn('Failed to save conversation ID to localStorage:', err);
    }
  }, [state.activeConversationId, storageKey]);

  /**
   * Set error with optional auto-clear
   */
  const setError = useCallback((error: string | null) => {
    setState(prev => ({ ...prev, error }));
  }, []);

  /**
   * Fetch conversations list
   */
  const refetchConversations = useCallback(async (limit = 20) => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    setState(prev => ({ ...prev, isLoading: true }));

    try {
      const response = await chatApiService.listConversations(limit, 0);
      const conversations: Conversation[] = response.conversations.map(conv => ({
        ...conv,
        unreadCount: 0
      }));

      // Validate active conversation ID exists in new list, or select first conversation
      setState(prev => {
        let activeId = prev.activeConversationId;
        if (activeId && !conversations.find(c => c.id === activeId)) {
          // Stored ID doesn't exist in new list, select first conversation or clear
          activeId = conversations.length > 0 ? conversations[0].id : null;
        }
        return {
          ...prev,
          conversations,
          activeConversationId: activeId,
          error: null
        };
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load conversations';
      setError(message);
      console.error('Failed to load conversations:', err);
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
      loadingRef.current = false;
    }
  }, [setError]);

  /**
   * Create a new conversation
   */
  const createConversation = useCallback(async (title?: string) => {
    setState(prev => ({ ...prev, isLoading: true }));

    try {
      const response = await chatApiService.createConversation(title);
      const newConversation: Conversation = {
        ...response,
        unreadCount: 0
      };
      setState(prev => ({
        ...prev,
        conversations: [newConversation, ...prev.conversations],
        activeConversationId: response.id.toString(),
        messages: [],
        error: null
      }));
      try {
        localStorage.setItem(storageKey, response.id.toString());
      } catch (e) {
        console.warn('Failed to save conversation ID:', e);
      }
      return newConversation;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create conversation';
      setError(message);
      console.error('Failed to create conversation:', err);
      throw err;
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, [storageKey, setError]);

  /**
   * Select/load a conversation
   */
  const selectConversation = useCallback(async (conversationId: string) => {
    setState(prev => ({
      ...prev,
      activeConversationId: conversationId,
      messages: []
    }));
    try {
      localStorage.setItem(storageKey, conversationId);
    } catch (e) {
      console.warn('Failed to save conversation ID:', e);
    }
  }, [storageKey]);

  /**
   * Load messages for active conversation
   */
  const loadMessages = useCallback(async (limit = 20) => {
    if (!state.activeConversationId) return;
    if (loadingRef.current) return;

    loadingRef.current = true;
    setState(prev => ({ ...prev, isLoading: true }));

    try {
      const response = await chatApiService.getMessageHistory(
        state.activeConversationId,
        limit,
        0
      );
      const messages: Message[] = response.messages.map(msg => ({
        ...msg,
        timestamp: new Date(msg.created_at),
        isLoading: false
      }));
      setState(prev => ({
        ...prev,
        messages: messages.reverse(),
        error: null
      }));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load messages';
      setError(message);
      console.error('Failed to load messages:', err);
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
      loadingRef.current = false;
    }
  }, [state.activeConversationId, setError]);

  /**
   * Send a message and get AI response
   */
  const sendMessage = useCallback(async (content: string) => {
    if (!state.activeConversationId) {
      setError('No conversation selected');
      return null;
    }

    if (!content.trim()) {
      setError('Message cannot be empty');
      return null;
    }

    // Add optimistic user message
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      conversation_id: state.activeConversationId,
      role: 'user',
      content: content.trim(),
      created_at: new Date().toISOString(),
      timestamp: new Date(),
      isLoading: false
    };

    // Add loading placeholder for assistant response
    const assistantPlaceholder: Message = {
      id: `loading-${Date.now()}`,
      conversation_id: state.activeConversationId,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
      timestamp: new Date(),
      isLoading: true
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage, assistantPlaceholder],
      isLoading: true
    }));

    try {
      const response = await chatApiService.sendMessage(
        state.activeConversationId,
        content
      );

      // Replace loading placeholder with actual response
      const assistantMessage: Message = {
        ...response,
        conversation_id: state.activeConversationId!,
        timestamp: new Date(response.created_at),
        isLoading: false
      };

      setState(prev => ({
        ...prev,
        messages: prev.messages.map(msg =>
          msg.id === assistantPlaceholder.id ? assistantMessage : msg
        ),
        error: null
      }));

      // Update conversation with new message count
      setState(prev => ({
        ...prev,
        conversations: prev.conversations.map(conv =>
          conv.id === state.activeConversationId
            ? { ...conv, message_count: conv.message_count + 2 }
            : conv
        )
      }));

      return assistantMessage;
    } catch (err) {
      // Remove loading placeholder on error
      setState(prev => ({
        ...prev,
        messages: prev.messages.filter(msg => msg.id !== assistantPlaceholder.id)
      }));

      const message = err instanceof Error ? err.message : 'Failed to send message';
      setError(message);
      console.error('Failed to send message:', err);
      throw err;
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, [state.activeConversationId, setError]);

  /**
   * Delete a conversation
   */
  const deleteConversation = useCallback(async (conversationId: string) => {
    try {
      await chatApiService.deleteConversation(conversationId);
      setState(prev => ({
        ...prev,
        conversations: prev.conversations.filter(c => c.id !== conversationId),
        activeConversationId: prev.activeConversationId === conversationId ? null : prev.activeConversationId,
        messages: prev.activeConversationId === conversationId ? [] : prev.messages
      }));
      if (state.activeConversationId === conversationId) {
        localStorage.removeItem(storageKey);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete conversation';
      setError(message);
      console.error('Failed to delete conversation:', err);
      throw err;
    }
  }, [state.activeConversationId, storageKey, setError]);

  /**
   * Delete a message
   */
  const deleteMessage = useCallback(async (messageId: string) => {
    if (!state.activeConversationId) return;

    try {
      await chatApiService.deleteMessage(state.activeConversationId, messageId);
      setState(prev => ({
        ...prev,
        messages: prev.messages.filter(m => m.id !== messageId)
      }));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete message';
      setError(message);
      console.error('Failed to delete message:', err);
      throw err;
    }
  }, [state.activeConversationId, setError]);

  /**
   * Clear error manually
   */
  const clearError = useCallback(() => {
    setError(null);
  }, [setError]);

  return {
    // State
    conversations: state.conversations,
    activeConversationId: state.activeConversationId,
    messages: state.messages,
    isLoading: state.isLoading,
    error: state.error,
    isDarkMode: state.isDarkMode,

    // Actions
    createConversation,
    selectConversation,
    loadMessages,
    sendMessage,
    deleteConversation,
    deleteMessage,
    refetchConversations,
    clearError,
    setError
  };
}
