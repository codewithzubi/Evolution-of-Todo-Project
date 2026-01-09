import React, { useState } from 'react';
import { Task } from '../../types/task';

interface AddTaskModalProps {
  onClose: () => void;
  onAddTask: (task: Task) => void;
}

const AddTaskModal: React.FC<AddTaskModalProps> = ({ onClose, onAddTask }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // In a real implementation, we would call our API to create the task
      // For now, we'll create a mock task
      const newTask: Task = {
        id: Math.random().toString(36).substring(7),
        title,
        description,
        status: 'pending',
        user_id: 'current-user-id', // This would come from auth context
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 500));

      onAddTask(newTask);
    } catch (err) {
      setError('Failed to add task. Please try again.');
      console.error('Error adding task:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="glass-modal w-full max-w-md">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-white">Add New Task</h2>
            <button
              onClick={onClose}
              className="text-purple-300 hover:text-white transition-colors"
              disabled={loading}
            >
              ✕
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-500/20 backdrop-blur-sm rounded-lg text-red-200">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="title" className="block text-sm font-medium text-purple-200 mb-1">
                Title *
              </label>
              <input
                id="title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full glass-input text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-400"
                placeholder="Enter task title"
                required
                disabled={loading}
              />
            </div>

            <div className="mb-6">
              <label htmlFor="description" className="block text-sm font-medium text-purple-200 mb-1">
                Description
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full glass-input text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-400 min-h-[100px]"
                placeholder="Enter task description (optional)"
                disabled={loading}
              />
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={onClose}
                disabled={loading}
                className="px-4 py-2 rounded-lg text-purple-200 hover:text-white transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || !title.trim()}
                className={`px-6 py-2 rounded-xl font-medium text-white transition-all ${
                  loading || !title.trim()
                    ? 'bg-purple-700 cursor-not-allowed opacity-70'
                    : 'glass-button hover:backdrop-blur-2xl hover:scale-105'
                }`}
              >
                {loading ? (
                  <span className="flex items-center">
                    <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                    Adding...
                  </span>
                ) : (
                  'Add Task'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AddTaskModal;