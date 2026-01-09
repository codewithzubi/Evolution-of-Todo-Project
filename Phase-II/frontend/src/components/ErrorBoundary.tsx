'use client';

import React, { Component, ReactNode } from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-4">
          <div className="glass-card p-8 max-w-md w-full text-center">
            <div className="text-center mb-6">
              <div className="mx-auto w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Something went wrong</h2>
              <p className="text-purple-200">
                An unexpected error has occurred. Please try again.
              </p>
            </div>

            <div className="text-left bg-red-500/10 p-4 rounded-lg mb-6">
              <p className="text-red-200 text-sm font-mono break-words">
                {this.state.error?.message || 'Unknown error occurred'}
              </p>
            </div>

            <button
              onClick={() => window.location.reload()}
              className="glass-button px-6 py-3 rounded-xl font-medium text-white hover:backdrop-blur-2xl hover:scale-105 transition-all"
            >
              Refresh Page
            </button>
          </div>
        </div>
      );

      return FallbackComponent;
    }

    return this.props.children;
  }
}

export default ErrorBoundary;