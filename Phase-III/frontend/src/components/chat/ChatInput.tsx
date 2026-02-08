// [Task]: T351, T357, [From]: specs/004-ai-chatbot/spec.md
// ChatInput Component - Text input and send button with loading state

'use client';

import { useState, useRef } from 'react';

interface ChatInputProps {
  onSendMessage: (message: string) => Promise<void>;
  isLoading: boolean;
  isDarkMode: boolean;
  disabled?: boolean;
  placeholder?: string;
}

/**
 * ChatInput Component
 * Allows user to type and send messages
 * Shows loading state during send
 */
export function ChatInput({
  onSendMessage,
  isLoading,
  isDarkMode,
  disabled = false,
  placeholder = 'Type your message...'
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSendClick = async () => {
    if (!message.trim() || isLoading || isSending || disabled) return;

    setIsSending(true);
    try {
      await onSendMessage(message);
      setMessage('');
      if (inputRef.current) {
        inputRef.current.focus();
      }
    } catch (err) {
      console.error('Failed to send message:', err);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendClick();
    }
  };

  return (
    <div
      className={`border-t p-4 ${
        isDarkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'
      }`}
    >
      <div className="flex gap-2">
        <input
          ref={inputRef}
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading || isSending || disabled}
          placeholder={placeholder}
          className={`flex-1 px-4 py-2 rounded-lg border outline-none transition-all ${
            isDarkMode
              ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400'
              : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
          } focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:opacity-50`}
          aria-label="Chat message input"
          autoComplete="off"
        />
        <button
          onClick={handleSendClick}
          disabled={!message.trim() || isLoading || isSending || disabled}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium whitespace-nowrap"
          aria-label="Send message"
          aria-busy={isSending}
        >
          {isSending ? (
            <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            'Send'
          )}
        </button>
      </div>
    </div>
  );
}
