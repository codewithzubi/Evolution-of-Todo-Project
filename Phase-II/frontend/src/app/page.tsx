'use client';

import { useState, useEffect } from 'react';
import { isAuthenticated } from '../lib/auth';
import Link from 'next/link';

export default function Home() {
  const [isAuthenticatedState, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated
    setIsAuthenticated(isAuthenticated());
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-400"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-4">
      <div className="max-w-4xl mx-auto">
        <header className="py-8 text-center">
          <h1 className="text-4xl font-bold text-white mb-2">Phase II Todo App</h1>
          <p className="text-purple-200">Glassmorphic Full-Stack Web Application</p>
        </header>

        <main className="glass-card p-8 rounded-2xl">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Welcome to the Todo App</h2>
            <p className="text-purple-200 mb-6">
              {isAuthenticatedState
                ? 'You are logged in! Start managing your tasks.'
                : 'Please log in or register to access your tasks.'}
            </p>

            {!isAuthenticatedState ? (
              <div className="space-y-4">
                <Link
                  href="/auth/login"
                  className="inline-block glass-button px-6 py-3 rounded-xl font-medium text-white hover:backdrop-blur-2xl hover:scale-105 transition-all"
                >
                  Login
                </Link>
                <Link
                  href="/auth/register"
                  className="inline-block glass-button px-6 py-3 rounded-xl font-medium text-white hover:backdrop-blur-2xl hover:scale-105 transition-all ml-4"
                >
                  Register
                </Link>
              </div>
            ) : (
              <Link
                href="/dashboard"
                className="inline-block glass-button px-6 py-3 rounded-xl font-medium text-white hover:backdrop-blur-2xl hover:scale-105 transition-all"
              >
                Go to Dashboard
              </Link>
            )}
          </div>
        </main>

        <footer className="py-8 text-center text-purple-300 text-sm">
          <p>Phase II Full-Stack Web Todo App with Glassmorphism Design</p>
        </footer>
      </div>

      <style jsx global>{`
        .glass-card {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 16px;
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