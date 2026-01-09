import React, { useState } from 'react';
import { Task } from '../../types/task';
import { taskApi } from '../../lib/api';

interface TaskActionsProps {
  task: Task;
  onTaskUpdate: (task: Task) => void;
  onTaskDelete: (id: string) => void;
}

const TaskActions: React.FC<TaskActionsProps> = ({ task, onTaskUpdate, onTaskDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpdate = async () => {
    setLoading(true);
    setError(null);

    try {
      const updatedTask = await taskApi.updateTask(task.id, {
        title,
        description,
      });

      onTaskUpdate(updatedTask);
      setIsEditing(false);
    } catch (err) {
      setError('Failed to update task. Please try again.');
      console.error('Error updating task:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await taskApi.deleteTask(task.id);
      onTaskDelete(task.id);
    } catch (err) {
      setError('Failed to delete task. Please try again.');
      console.error('Error deleting task:', err);
    }
  };

  if (isEditing) {
    return (
      <div className="glass-card p-4">
        {error && (
          <div className="mb-3 p-2 bg-red-500/20 backdrop-blur-sm rounded text-red-200 text-sm">
            {error}
          </div>
        )}
        <div className="mb-3">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full glass-input text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-400 mb-2"
            placeholder="Task title"
          />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full glass-input text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-400 min-h-[80px]"
            placeholder="Task description"
          />
        </div>
        <div className="flex justify-end space-x-2">
          <button
            onClick={() => setIsEditing(false)}
            disabled={loading}
            className="px-3 py-1 rounded-lg text-purple-200 hover:text-white transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleUpdate}
            disabled={loading || !title.trim()}
            className={`px-4 py-1 rounded-lg font-medium text-white transition-all ${
              loading || !title.trim()
                ? 'bg-purple-700 cursor-not-allowed opacity-70'
                : 'glass-button hover:backdrop-blur-2xl'
            }`}
          >
            {loading ? 'Updating...' : 'Save'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex space-x-3">
      <button
        onClick={() => setIsEditing(true)}
        className="text-blue-400 hover:text-blue-300 transition-colors text-sm"
      >
        Edit
      </button>
      <button
        onClick={handleDelete}
        className="text-red-400 hover:text-red-300 transition-colors text-sm"
      >
        Delete
      </button>
    </div>
  );
};

export default TaskActions;