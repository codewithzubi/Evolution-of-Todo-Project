// [Task]: T352, [From]: specs/004-ai-chatbot/spec.md
// ConversationList Component - Dropdown with recent conversations

'use client';

import { useState } from 'react';
import type { Conversation } from '@/types/chat';

interface ConversationListProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onCreateNew: () => void;
  onDeleteConversation: (id: string) => void;
  isDarkMode: boolean;
  isOpen: boolean;
  onToggle: () => void;
}

/**
 * ConversationList Component
 * Shows dropdown with recent conversations
 * Allows selection, deletion, and creation of new conversations
 */
export function ConversationList({
  conversations,
  activeConversationId,
  onSelectConversation,
  onCreateNew,
  onDeleteConversation,
  isDarkMode,
  isOpen,
  onToggle
}: ConversationListProps) {
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  const handleDelete = (id: string) => {
    setDeleteConfirmId(null);
    onDeleteConversation(id);
  };

  const recentConversations = conversations.slice(0, 5);

  return (
    <div className="relative">
      {/* Header with toggle button */}
      <button
        onClick={onToggle}
        className={`w-full px-4 py-3 flex items-center justify-between border-b ${
          isDarkMode
            ? 'border-gray-700 bg-gray-800 text-white hover:bg-gray-700'
            : 'border-gray-200 bg-white text-gray-900 hover:bg-gray-50'
        } transition-colors`}
        aria-label="Toggle conversations list"
        aria-expanded={isOpen}
      >
        <span className="font-medium">Conversations</span>
        <span className={`transition-transform ${isOpen ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>

      {/* Dropdown content */}
      {isOpen && (
        <div
          className={`absolute top-full left-0 right-0 max-h-64 overflow-y-auto z-40 border-b ${
            isDarkMode
              ? 'border-gray-700 bg-gray-800 shadow-lg'
              : 'border-gray-200 bg-white shadow-lg'
          }`}
          role="listbox"
        >
          {/* New Conversation Button */}
          <button
            onClick={onCreateNew}
            className={`w-full px-4 py-3 text-left border-b font-medium ${
              isDarkMode
                ? 'border-gray-700 bg-gray-700 hover:bg-gray-600 text-white'
                : 'border-gray-200 bg-gray-50 hover:bg-gray-100 text-gray-900'
            } transition-colors`}
            role="option"
          >
            + New Conversation
          </button>

          {/* Conversations List */}
          {recentConversations.length === 0 ? (
            <div
              className={`px-4 py-6 text-center text-sm ${
                isDarkMode ? 'text-gray-400' : 'text-gray-600'
              }`}
            >
              No conversations yet. Create one to get started!
            </div>
          ) : (
            recentConversations.map((conv) => (
              <div key={conv.id} className={`border-b ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
                <button
                  onClick={() => onSelectConversation(conv.id.toString())}
                  className={`w-full px-4 py-3 text-left flex items-center justify-between transition-colors ${
                    activeConversationId === conv.id
                      ? isDarkMode
                        ? 'bg-gray-700 text-blue-400'
                        : 'bg-blue-100 text-blue-900'
                      : isDarkMode
                        ? 'text-gray-300 hover:bg-gray-700'
                        : 'text-gray-900 hover:bg-gray-50'
                  }`}
                  role="option"
                  aria-selected={activeConversationId === conv.id}
                >
                  <div className="flex-1 min-w-0">
                    <p className="truncate text-sm font-medium">
                      {conv.title || 'Untitled Conversation'}
                    </p>
                    {conv.message_count > 0 && (
                      <p className={`text-xs truncate ${
                        isDarkMode ? 'text-gray-500' : 'text-gray-600'
                      }`}>
                        {conv.message_count} messages
                      </p>
                    )}
                  </div>
                </button>

                {/* Delete button */}
                <div
                  className={`px-4 py-2 border-t ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}
                >
                  {deleteConfirmId === conv.id ? (
                    <div className="flex gap-2 text-sm">
                      <button
                        onClick={() => handleDelete(conv.id.toString())}
                        className="flex-1 px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                      >
                        Confirm
                      </button>
                      <button
                        onClick={() => setDeleteConfirmId(null)}
                        className={`flex-1 px-2 py-1 rounded ${
                          isDarkMode
                            ? 'bg-gray-700 text-white hover:bg-gray-600'
                            : 'bg-gray-300 text-gray-900 hover:bg-gray-400'
                        }`}
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setDeleteConfirmId(conv.id.toString())}
                      className={`w-full px-2 py-1 text-sm rounded transition-colors ${
                        isDarkMode
                          ? 'text-red-400 hover:bg-gray-700'
                          : 'text-red-600 hover:bg-gray-100'
                      }`}
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
