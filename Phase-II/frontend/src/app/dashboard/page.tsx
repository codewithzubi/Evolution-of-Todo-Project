'use client';

import { useState, useEffect } from 'react';
import { taskApi } from '../../lib/api';
import { Task } from '../../types/task';
import Link from 'next/link';

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const tasksData = await taskApi.getTasks();
      setTasks(tasksData);
      setError(null);
    } catch (err) {
      setError('Failed to load tasks. Please try again.');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTask = async (id: string) => {
    try {
      await taskApi.deleteTask(id);
      setTasks(tasks.filter(task => task.id !== id));
    } catch (err) {
      setError('Failed to delete task. Please try again.');
      console.error('Error deleting task:', err);
    }
  };

  const handleUpdateTask = async (task: Task) => {
    try {
      const updatedTask = await taskApi.updateTask(task.id, {
        title: task.title,
        description: task.description,
        status: task.status
      });

      setTasks(tasks.map(t => t.id === task.id ? updatedTask : t));
    } catch (err) {
      setError('Failed to update task. Please try again.');
      console.error('Error updating task:', err);
    }
  };

  const handleStatusToggle = async (task: Task) => {
    try {
      const updatedStatus = task.status === 'pending' ? 'completed' : 'pending';
      const updatedTask = await taskApi.updateTaskStatus(task.id, updatedStatus);

      setTasks(tasks.map(t => t.id === task.id ? updatedTask : t));
    } catch (err) {
      setError('Failed to update task status. Please try again.');
      console.error('Error updating task status:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-4 sm:p-8">
      {/* Decorative background elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/3 right-1/4 w-72 h-72 bg-pink-500/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/3 right-1/3 w-56 h-56 bg-blue-500/10 rounded-full blur-3xl"></div>
      </div>

      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="mb-10">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">Task Dashboard</h1>
              <p className="text-purple-200">Manage your tasks with style</p>
            </div>
            <Link
              href="/"
              className="glass-button px-4 py-2 rounded-xl text-white font-medium hover:backdrop-blur-2xl hover:scale-105 transition-all"
            >
              Home
            </Link>
          </div>
        </header>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-white mb-2">Total Tasks</h3>
            <p className="text-3xl font-bold text-purple-300">{tasks.length}</p>
          </div>
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-white mb-2">Completed</h3>
            <p className="text-3xl font-bold text-green-300">
              {tasks.filter(t => t.status === 'completed').length}
            </p>
          </div>
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-white mb-2">Pending</h3>
            <p className="text-3xl font-bold text-yellow-300">
              {tasks.filter(t => t.status === 'pending').length}
            </p>
          </div>
        </div>

        {/* Main Content */}
        <div className="glass-card p-6 sm:p-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-white">Your Tasks</h2>
            <button
              onClick={() => {
                // In a real app, this would open an add task modal
                alert('Add task functionality would open here');
              }}
              className="glass-button px-6 py-2 rounded-xl text-white font-medium hover:backdrop-blur-2xl hover:scale-105 transition-all duration-300"
            >
              + Add Task
            </button>
          </div>

          {error && (
            <div className="mb-6 p-3 bg-red-500/20 backdrop-blur-sm rounded-lg text-red-200">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-400"></div>
            </div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-12">
              <h3 className="text-xl font-medium text-white mb-2">No tasks yet</h3>
              <p className="text-purple-200 mb-6">Add your first task to get started</p>
              <button
                onClick={() => {
                  // In a real app, this would open an add task modal
                  alert('Add task functionality would open here');
                }}
                className="glass-button px-6 py-3 rounded-xl text-white font-medium hover:backdrop-blur-2xl hover:scale-105 transition-all"
              >
                Create Your First Task
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-purple-500/30">
                <thead>
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-purple-300 uppercase tracking-wider">ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-purple-300 uppercase tracking-wider">Title</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-purple-300 uppercase tracking-wider">Description</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-purple-300 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-purple-300 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-purple-500/20">
                  {tasks.map((task) => (
                    <tr key={task.id} className="hover:bg-white/5 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-purple-200">{task.id.substring(0, 8)}...</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">{task.title}</td>
                      <td className="px-6 py-4 text-sm text-purple-200 max-w-xs truncate">{task.description || 'No description'}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => handleStatusToggle(task)}
                          className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            task.status === 'completed'
                              ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                              : 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30'
                          }`}
                        >
                          {task.status === 'completed' ? 'Completed' : 'Pending'}
                        </button>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => handleDeleteTask(task.id)}
                          className="text-red-400 hover:text-red-300 mr-4 transition-colors"
                        >
                          Delete
                        </button>
                        <button
                          onClick={() => handleUpdateTask(task)}
                          className="text-blue-400 hover:text-blue-300 transition-colors"
                        >
                          Edit
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <style jsx global>{`
        .glass-card {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 16px;
          box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
        }

        .glass-button {
          background: rgba(255, 255, 255, 0.15);
          backdrop-filter: blur(10px);
          -webkit-backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 8px;
          transition: all 0.3s ease;
        }

        .glass-button:hover {
          background: rgba(255, 255, 255, 0.25);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          transform: scale(1.02);
        }
      `}</style>
    </div>
  );
}