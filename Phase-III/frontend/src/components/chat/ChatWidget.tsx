// [Task]: T346-T358, [From]: specs/004-ai-chatbot/spec.md
// ChatWidget Component - Main floating chat widget with button and window

'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { useChat } from '@/hooks/useChat';
import { useAuth } from '@/hooks/useAuth';

// Dynamically import ChatWindow to reduce bundle size
const ChatWindow = dynamic(() => import('./ChatWindow').then(mod => ({ default: mod.ChatWindow })), {
  loading: () => null,
  ssr: false
});

/**
 * ChatWidget Component
 * Main entry point for the chat widget
 * - Floating button in bottom-right corner
 * - Chat window with conversations and messages
 * - Full authentication and error handling
 */
export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const { user } = useAuth();
  const {
    conversations,
    activeConversationId,
    messages,
    isLoading,
    error,
    isDarkMode,
    createConversation,
    selectConversation,
    sendMessage,
    deleteConversation,
    clearError
  } = useChat({
    autoLoadConversations: isOpen && !!user,
    autoLoadMessages: isOpen && !!user
  });

  // Prevent hydration mismatch
  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) return null;

  // Show sign-in prompt if not authenticated
  if (!user) {
    return (
      <div
        className="fixed bottom-6 right-6 z-50"
        role="region"
        aria-label="Chat widget"
      >
        <button
          disabled
          className="w-16 h-16 rounded-full bg-gray-400 text-white shadow-lg flex items-center justify-center cursor-not-allowed opacity-50"
          title="Sign in to use chat"
        >
          💬
        </button>
      </div>
    );
  }

  // Handle create new conversation
  const handleCreateConversation = async () => {
    try {
      await createConversation('New Conversation');
    } catch (err) {
      console.error('Failed to create conversation:', err);
    }
  };

  // Handle send message
  const handleSendMessage = async (content: string) => {
    try {
      await sendMessage(content);
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  return (
    <div
      className="fixed bottom-6 right-6 z-50 transition-transform duration-300"
      role="region"
      aria-label="Chat widget"
    >
      {/* Chat Window */}
      {isOpen && (
        <ChatWindow
          isOpen={isOpen}
          conversations={conversations}
          activeConversationId={activeConversationId}
          messages={messages}
          isLoading={isLoading}
          error={error}
          isDarkMode={isDarkMode}
          onClose={() => setIsOpen(false)}
          onSelectConversation={selectConversation}
          onCreateConversation={handleCreateConversation}
          onSendMessage={handleSendMessage}
          onDeleteConversation={deleteConversation}
          onClearError={clearError}
        />
      )}

      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-lg hover:shadow-xl flex items-center justify-center transition-all duration-200 transform hover:scale-110 active:scale-95 ${
          isOpen ? 'ring-2 ring-blue-400' : ''
        }`}
        title={isOpen ? 'Close chat' : 'Open chat'}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
        aria-expanded={isOpen}
      >
        <span className="text-2xl">💬</span>
      </button>
    </div>
  );
}
