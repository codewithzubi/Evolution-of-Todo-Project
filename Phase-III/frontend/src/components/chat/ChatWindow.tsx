// [Task]: T350, T351, T352, T357, [From]: specs/004-ai-chatbot/spec.md
// ChatWindow Component - Main chat interface

'use client';

import { useEffect, useState } from 'react';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { ConversationList } from './ConversationList';
import { ErrorMessage } from './ErrorMessage';
import type { Message } from '@/types/chat';

interface ChatWindowProps {
  isOpen: boolean;
  conversations: any[];
  activeConversationId: string | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  isDarkMode: boolean;
  onClose: () => void;
  onSelectConversation: (id: string) => void;
  onCreateConversation: () => void;
  onSendMessage: (message: string) => Promise<void>;
  onDeleteConversation: (id: string) => void;
  onClearError: () => void;
}

/**
 * ChatWindow Component
 * Main chat interface with messages, input, and conversation selector
 */
export function ChatWindow({
  isOpen,
  conversations,
  activeConversationId,
  messages,
  isLoading,
  error,
  isDarkMode,
  onClose,
  onSelectConversation,
  onCreateConversation,
  onSendMessage,
  onDeleteConversation,
  onClearError
}: ChatWindowProps) {
  const [showConversations, setShowConversations] = useState(false);

  // Close window on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Chat window */}
      <div
        className={`fixed bottom-24 right-6 w-96 max-h-[600px] rounded-2xl shadow-2xl flex flex-col transition-all duration-300 z-50 ${
          isDarkMode ? 'bg-gray-800' : 'bg-white'
        }`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="chat-window-title"
      >
        {/* Header */}
        <div
          className={`flex items-center justify-between p-4 border-b ${
            isDarkMode ? 'border-gray-700' : 'border-gray-200'
          }`}
        >
          <h2
            id="chat-window-title"
            className={`text-lg font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}
          >
            AI Assistant
          </h2>
          <button
            onClick={onClose}
            className={`p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors`}
            aria-label="Close chat"
          >
            ✕
          </button>
        </div>

        {/* Conversation selector */}
        <ConversationList
          conversations={conversations}
          activeConversationId={activeConversationId}
          onSelectConversation={onSelectConversation}
          onCreateNew={onCreateConversation}
          onDeleteConversation={onDeleteConversation}
          isDarkMode={isDarkMode}
          isOpen={showConversations}
          onToggle={() => setShowConversations(!showConversations)}
        />

        {/* Error message */}
        {error && (
          <div className="px-4 pt-3">
            <ErrorMessage
              error={error}
              isDarkMode={isDarkMode}
              onDismiss={onClearError}
            />
          </div>
        )}

        {/* Messages or empty state */}
        {activeConversationId ? (
          <>
            <MessageList
              messages={messages}
              isDarkMode={isDarkMode}
              hasMore={false}
            />
            <ChatInput
              onSendMessage={onSendMessage}
              isLoading={isLoading}
              isDarkMode={isDarkMode}
              disabled={!activeConversationId}
              placeholder="Type your message..."
            />
          </>
        ) : (
          <div
            className={`flex-1 flex items-center justify-center p-4 text-center ${
              isDarkMode ? 'text-gray-400' : 'text-gray-600'
            }`}
          >
            <p className="text-sm">
              Select a conversation or create a new one to start chatting
            </p>
          </div>
        )}
      </div>
    </>
  );
}
