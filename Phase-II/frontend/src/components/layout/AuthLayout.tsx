// [Task]: T039, [From]: specs/002-task-ui-frontend/spec.md#US1
// Authentication layout wrapper for login and signup pages

'use client';

import { ReactNode } from 'react';

export interface AuthLayoutProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
}

/**
 * AuthLayout Component
 * Wrapper for authentication pages (login, signup) with branding, centered form, and responsive design
 * [Task]: T039, [From]: specs/002-task-ui-frontend/spec.md#US1
 *
 * @param children - Form content to display
 * @param title - Optional page title
 * @param subtitle - Optional page subtitle
 *
 * @example
 * <AuthLayout title="Create Account">
 *   <SignupForm />
 * </AuthLayout>
 */
export function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Branding Section */}
        <div className="text-center mb-8">
          {/* Logo */}
          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-2xl font-bold text-white">T</span>
            </div>
          </div>

          {/* App Title */}
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Evolution Todo</h1>
          <p className="text-gray-600 text-sm">Manage your tasks with ease</p>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-lg shadow-lg p-6 md:p-8 space-y-6">
          {/* Page Title */}
          {title && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
              {subtitle && (
                <p className="text-gray-600 text-sm mt-2">{subtitle}</p>
              )}
            </div>
          )}

          {/* Form Content */}
          {children}
        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-gray-600 text-xs">
            Secure authentication with JWT tokens
          </p>
        </div>
      </div>
    </div>
  );
}
