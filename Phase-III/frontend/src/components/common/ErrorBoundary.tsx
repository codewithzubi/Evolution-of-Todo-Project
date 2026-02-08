// [Task]: T021, [From]: specs/002-task-ui-frontend/spec.md#FR-013
// Error boundary component for catching render errors

'use client';

import React, { ReactNode, ReactElement } from 'react';
import { Button } from './Button';

export interface ErrorBoundaryProps {
  /**
   * Children to render
   */
  children: ReactNode;

  /**
   * Optional fallback UI to display on error
   */
  fallback?: (error: Error, reset: () => void) => ReactElement;

  /**
   * Callback when error is caught
   */
  onError?: (error: Error, info: React.ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Error boundary component that catches rendering errors in child components
 *
 * @example
 * <ErrorBoundary>
 *   <MyComponent />
 * </ErrorBoundary>
 */
export class ErrorBoundary extends React.Component<ErrorBoundaryProps, State> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by boundary:', error, errorInfo);
    }
    this.props.onError?.(error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.handleReset);
      }

      return (
        <div className="p-4 md:p-6 bg-red-50 border border-red-200 rounded-lg">
          <div className="max-w-md">
            <h2 className="text-lg font-semibold text-red-900 mb-2">Something went wrong</h2>
            <p className="text-sm text-red-800 mb-4">
              {this.state.error.message || 'An unexpected error occurred'}
            </p>
            <Button
              variant="danger"
              onClick={this.handleReset}
              className="w-full md:w-auto"
            >
              Try again
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
