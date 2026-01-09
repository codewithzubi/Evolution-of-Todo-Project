import React, { useEffect } from 'react';

interface GlassToastProps {
  message: string;
  type?: 'success' | 'error' | 'info' | 'warning';
  visible: boolean;
  onClose: () => void;
  duration?: number;
}

const GlassToast: React.FC<GlassToastProps> = ({
  message,
  type = 'info',
  visible,
  onClose,
  duration = 3000,
}) => {
  useEffect(() => {
    if (visible) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [visible, duration, onClose]);

  if (!visible) return null;

  const getTypeStyles = () => {
    switch (type) {
      case 'success':
        return 'bg-green-500/20 border border-green-500/30 text-green-200';
      case 'error':
        return 'bg-red-500/20 border border-red-500/30 text-red-200';
      case 'warning':
        return 'bg-yellow-500/20 border border-yellow-500/30 text-yellow-200';
      case 'info':
      default:
        return 'bg-blue-500/20 border border-blue-500/30 text-blue-200';
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50">
      <div className={`glass-card p-4 rounded-xl backdrop-blur-xl border ${getTypeStyles()} shadow-2xl min-w-[300px]`}>
        <div className="flex items-start">
          <div className="flex-1">
            <p className="text-sm font-medium">{message}</p>
          </div>
          <button
            onClick={onClose}
            className="text-white/70 hover:text-white ml-2 transition-colors"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
};

export default GlassToast;