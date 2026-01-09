import React from 'react';
import { Task } from '../../types/task';
import { taskApi } from '../../lib/api';
import TaskActions from './TaskActions';

interface GlassTableProps {
  tasks: Task[];
  onDeleteTask: (id: string) => void;
  onUpdateTask: (task: Task) => void;
}

const GlassTable: React.FC<GlassTableProps> = ({ tasks, onDeleteTask, onUpdateTask }) => {
  const handleStatusToggle = async (task: Task) => {
    try {
      // Optimistic update: immediately update UI
      const updatedStatus = task.status === 'pending' ? 'completed' : 'pending';
      const optimisticTask = {
        ...task,
        status: updatedStatus
      };

      // Update the UI optimistically
      onUpdateTask(optimisticTask);

      // Then update the server
      await taskApi.updateTaskStatus(task.id, updatedStatus);
    } catch (error) {
      console.error('Error updating task status:', error);
      // If the API call fails, revert the optimistic update
      // In a real app, you'd want to show an error message to the user
    }
  };

  return (
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
                <TaskActions
                  task={task}
                  onTaskUpdate={onUpdateTask}
                  onTaskDelete={onDeleteTask}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default GlassTable;