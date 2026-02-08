// [Task]: T351, T357, [From]: specs/004-ai-chatbot/spec.md
// MessageList Component - Displays chat messages with proper formatting

'use client';

import { useRef, useEffect } from 'react';
import type { Message } from '@/types/chat';

interface MessageListProps {
  messages: Message[];
  isDarkMode: boolean;
  onLoadMore?: () => void;
  hasMore?: boolean;
  isLoadingMore?: boolean;
}

/**
 * MessageList Component
 * Displays messages in chronological order with user/assistant distinction
 * Scrolls to latest message on new message
 */
export function MessageList({
  messages,
  isDarkMode,
  onLoadMore,
  hasMore = false,
  isLoadingMore = false
}: MessageListProps) {
  const endRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  return (
    <div
      ref={containerRef}
      className={`flex-1 overflow-y-auto p-4 space-y-4 ${
        isDarkMode ? 'bg-gray-900' : 'bg-white'
      }`}
      role="log"
      aria-label="Chat messages"
    >
      {/* Load more button */}
      {hasMore && (
        <button
          onClick={onLoadMore}
          disabled={isLoadingMore}
          className="mx-auto px-4 py-2 text-sm rounded-lg transition-colors"
          aria-label="Load earlier messages"
        >
          {isLoadingMore ? 'Loading...' : 'Load earlier messages'}
        </button>
      )}

      {/* Messages */}
      {messages.length === 0 ? (
        <div
          className={`flex items-center justify-center h-full text-center p-4 ${
            isDarkMode ? 'text-gray-400' : 'text-gray-600'
          }`}
        >
          <p>Start a conversation by sending a message</p>
        </div>
      ) : (
        messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
            role="article"
            aria-label={`${message.role === 'user' ? 'Your message' : 'Assistant message'}: ${message.content}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white rounded-br-none'
                  : isDarkMode
                    ? 'bg-gray-800 text-gray-100 rounded-bl-none'
                    : 'bg-gray-200 text-gray-900 rounded-bl-none'
              }`}
            >
              {message.isLoading ? (
                <div className="flex items-center space-x-2">
                  <span className="inline-block w-2 h-2 bg-current rounded-full animate-bounce" />
                  <span className="inline-block w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <span className="inline-block w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              ) : (
                <>
                  {/* Task information with IDs */}
                  {message.content.includes('[') && message.content.includes(']') ? (
                    <div className="break-words text-sm space-y-1">
                      {message.content.split('\n').map((line, idx) => (
                        <div key={idx}>
                          {line.includes('[') && line.includes(']') ? (
                            <>
                              {line.split('[').map((part, i) => {
                                if (i === 0) return <span key={i}>{part}</span>;
                                const [taskId, rest] = part.split(']');
                                return (
                                  <span key={i}>
                                    <code className={`px-1.5 py-0.5 rounded text-xs font-mono font-semibold ${
                                      message.role === 'user' ? 'bg-blue-400' : (isDarkMode ? 'bg-gray-700' : 'bg-gray-300')
                                    }`}>
                                      {taskId}
                                    </code>
                                    {rest}
                                  </span>
                                );
                              })}
                            </>
                          ) : (
                            line
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="break-words text-sm">{message.content}</p>
                  )}

                  {/* Tool indicators */}
                  {message.tool_calls && message.tool_calls.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-current border-opacity-20 space-y-1">
                      {message.tool_calls.map((call, idx) => (
                        <div key={idx} className="text-xs opacity-80">
                          🔧 {call.name || 'Tool call'}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Timestamp */}
                  <div className={`text-xs mt-1 ${
                    message.role === 'user'
                      ? 'text-blue-100'
                      : isDarkMode
                        ? 'text-gray-500'
                        : 'text-gray-600'
                  }`}>
                    {message.timestamp?.toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                </>
              )}
            </div>
          </div>
        ))
      )}

      {/* Scroll target */}
      <div ref={endRef} />
    </div>
  );
}
