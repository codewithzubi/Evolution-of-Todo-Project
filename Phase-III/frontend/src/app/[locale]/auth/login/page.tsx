// [Task]: T034, T035, [From]: specs/002-task-ui-frontend/spec.md#US1
// Login page with email/password form and validation

'use client';

import { FormEvent, useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Input } from '@/components/common/Input';
import { Button } from '@/components/common/Button';
import { AuthLayout } from '@/components/layout/AuthLayout';
import { validateLoginForm } from '@/utils/validation';
import type { ValidationError } from '@/utils/validation';

/**
 * LoginPage Component
 * Handles user login with email and password validation
 * [Task]: T034, T035, [From]: specs/002-task-ui-frontend/spec.md#US1
 */
export default function LoginPage() {
  const router = useRouter();
  const pathname = usePathname();
  const { login, isLoading, error, isAuthenticated, clearError } = useAuth();

  // Extract locale from pathname (format: /[locale]/auth/login)
  const locale = pathname.split('/')[1] || 'en';

  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [validationErrors, setValidationErrors] = useState<
    Record<string, string>
  >({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Redirect to tasks if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push(`/${locale}/tasks`);
    }
  }, [isAuthenticated, router, locale]);

  /**
   * Validate form data
   * [Task]: T035, [From]: specs/002-task-ui-frontend/spec.md#US1
   */
  const validateForm = (): boolean => {
    const errors = validateLoginForm(email, password);
    const errorMap: Record<string, string> = {};

    errors.forEach((error: ValidationError) => {
      errorMap[error.field] = error.message;
    });

    setValidationErrors(errorMap);
    return errors.length === 0;
  };

  /**
   * Handle form submission
   * [Task]: T034, [From]: specs/002-task-ui-frontend/spec.md#US1
   */
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    clearError();
    setValidationErrors({});

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      await login(email, password);
      // useAuth hook handles redirect to /${locale}/tasks
    } catch (err) {
      // Error is handled by useAuth context
      console.error('Login failed:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Check if form is valid for submission
   */
  const isFormValid = email.trim().length > 0 && password.length > 0;

  return (
    <AuthLayout title="Log In" subtitle="Sign in to your account">
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Error Alert */}
        {error && (
          <div
            className="bg-red-50 border border-red-200 rounded-md p-4 text-red-800 text-sm"
            role="alert"
          >
            {error}
          </div>
        )}

        {/* Email Field */}
        <Input
          id="email"
          label="Email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            // Clear error when user starts typing
            if (validationErrors.email) {
              setValidationErrors((prev) => {
                const next = { ...prev };
                delete next.email;
                return next;
              });
            }
          }}
          error={validationErrors.email}
          disabled={isSubmitting || isLoading}
          autoComplete="email"
          required
        />

        {/* Password Field */}
        <Input
          id="password"
          label="Password"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            // Clear error when user starts typing
            if (validationErrors.password) {
              setValidationErrors((prev) => {
                const next = { ...prev };
                delete next.password;
                return next;
              });
            }
          }}
          error={validationErrors.password}
          disabled={isSubmitting || isLoading}
          autoComplete="current-password"
          required
        />

        {/* Submit Button */}
        <Button
          type="submit"
          disabled={!isFormValid || isSubmitting || isLoading}
          isLoading={isSubmitting || isLoading}
          className="w-full mt-6"
        >
          {isSubmitting || isLoading ? 'Logging in...' : 'Log In'}
        </Button>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">
              Don't have an account?
            </span>
          </div>
        </div>

        {/* Sign Up Link */}
        <Link
          href={`/${locale}/auth/signup`}
          className="block w-full text-center px-4 py-3 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors duration-200 font-medium"
        >
          Create Account
        </Link>
      </form>

      {/* Additional Help */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <div className="text-center text-xs text-gray-600 space-y-2">
          <p>Demo credentials:</p>
          <p className="font-mono text-gray-500">demo@example.com / password123</p>
        </div>
      </div>
    </AuthLayout>
  );
}
