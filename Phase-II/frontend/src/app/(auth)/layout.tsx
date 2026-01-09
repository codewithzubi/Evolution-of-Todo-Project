import React from 'react';
import './globals.css';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-4">
      <div className="relative w-full max-w-md">
        {/* Background glass effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-xl rounded-2xl shadow-2xl transform rotate-1"></div>
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 backdrop-blur-xl rounded-2xl shadow-2xl transform -rotate-1"></div>

        {/* Main glass card */}
        <div className="relative glass-card p-8 z-10">
          {children}
        </div>

        {/* Decorative elements */}
        <div className="absolute -top-4 -left-4 w-24 h-24 bg-purple-500/10 rounded-full blur-xl"></div>
        <div className="absolute -bottom-4 -right-4 w-32 h-32 bg-pink-500/10 rounded-full blur-xl"></div>
      </div>
    </div>
  );
}