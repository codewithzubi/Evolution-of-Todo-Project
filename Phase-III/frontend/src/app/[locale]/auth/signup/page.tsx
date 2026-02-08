// [Task]: T036, T037, [From]: specs/002-task-ui-frontend/spec.md#US1
// Signup page with email, password, and confirm password validation

'use client';

import { FormEvent, useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Input } from '@/components/common/Input';
import { Button } from '@/components/common/Button';
import { AuthLayout } from '@/components/layout/AuthLayout';
import { validateSignupForm } from '@/utils/validation';
import type { ValidationError } from '@/utils/validation';

/**
 * SignupPage Component
 * Handles new user registration with email, password, and validation
 * [Task]: T036, T037, [From]: specs/002-task-ui-frontend/spec.md#US1
 */
export default function SignupPage() {
  const router = useRouter();
  const pathname = usePathname();
  const { signup, isLoading, error, isAuthenticated, clearError } = useAuth();

  // Extract locale from pathname (format: /[locale]/auth/signup)
  const locale = pathname.split('/')[1] || 'en';

  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [validationErrors, setValidationErrors] = useState<
    Record<string, string>
  >({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Password strength indicator
  const [passwordStrength, setPasswordStrength] = useState<
    'weak' | 'fair' | 'strong'
  >('weak');

  // Redirect to tasks if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push(`/${locale}/tasks`);
    }
  }, [isAuthenticated, router, locale]);

  /**
   * Calculate password strength
   * [Task]: T037, [From]: specs/002-task-ui-frontend/spec.md#US1
   */
  const calculatePasswordStrength = (pwd: string): 'weak' | 'fair' | 'strong' => {
    if (pwd.length < 8) return 'weak';
    if (pwd.length < 12) return 'fair';

    // Check for variety of character types
    const hasUpperCase = /[A-Z]/.test(pwd);
    const hasLowerCase = /[a-z]/.test(pwd);
    const hasNumbers = /\d/.test(pwd);
    const hasSpecialChars = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pwd);

    const varietyCount = [hasUpperCase, hasLowerCase, hasNumbers, hasSpecialChars].filter(
      (v) => v
    ).length;

    return varietyCount >= 3 ? 'strong' : 'fair';
  };

  // Update password strength when password changes
  useEffect(() => {
    if (password) {
      setPasswordStrength(calculatePasswordStrength(password));
    }
  }, [password]);

  /**
   * Validate form data
   * [Task]: T037, [From]: specs/002-task-ui-frontend/spec.md#US1
   */
  const validateForm = (): boolean => {
    const errors = validateSignupForm(email, password, confirmPassword);
    const errorMap: Record<string, string> = {};

    errors.forEach((error: ValidationError) => {
      errorMap[error.field] = error.message;
    });

    setValidationErrors(errorMap);
    return errors.length === 0;
  };

  /**
   * Handle form submission
   * [Task]: T036, [From]: specs/002-task-ui-frontend/spec.md#US1
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
      await signup(email, password);
      // useAuth hook handles redirect to /${locale}/tasks
    } catch (err) {
      // Check if error is about user already existing
      if (
        error &&
        (error.includes('already exists') || error.includes('USER_EXISTS'))
      ) {
        setValidationErrors({
          email: 'An account with this email already exists',
        });
      }
      console.error('Signup failed:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Check if form is valid for submission
   */
  const isFormValid =
    email.trim().length > 0 &&
    password.length >= 8 &&
    confirmPassword === password &&
    !validationErrors.email &&
    !validationErrors.password &&
    !validationErrors.confirmPassword;

  /**
   * Get password strength color
   */
  const getStrengthColor = (strength: 'weak' | 'fair' | 'strong') => {
    switch (strength) {
      case 'weak':
        return 'bg-red-500';
      case 'fair':
        return 'bg-yellow-500';
      case 'strong':
        return 'bg-green-500';
    }
  };

  /**
   * Get password strength text
   */
  const getStrengthText = (strength: 'weak' | 'fair' | 'strong') => {
    switch (strength) {
      case 'weak':
        return 'Weak';
      case 'fair':
        return 'Fair';
      case 'strong':
        return 'Strong';
    }
  };

  return (
    <AuthLayout title="Create Account" subtitle="Join us to start managing your tasks">
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
        <div>
          <Input
            id="password"
            label="Password"
            type="password"
            placeholder="At least 8 characters"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
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
            autoComplete="new-password"
            required
          />

          {/* Password Strength Indicator */}
          {password && (
            <div className="mt-2 space-y-2">
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${getStrengthColor(passwordStrength)} transition-all duration-300`}
                    style={{
                      width:
                        passwordStrength === 'weak'
                          ? '33%'
                          : passwordStrength === 'fair'
                            ? '66%'
                            : '100%',
                    }}
                  />
                </div>
                <span className="text-xs font-medium text-gray-600">
                  {getStrengthText(passwordStrength)}
                </span>
              </div>
              <p className="text-xs text-gray-500">
                Mix uppercase, numbers, and special characters for a stronger password
              </p>
            </div>
          )}
        </div>

        {/* Confirm Password Field */}
        <Input
          id="confirmPassword"
          label="Confirm Password"
          type="password"
          placeholder="Confirm your password"
          value={confirmPassword}
          onChange={(e) => {
            setConfirmPassword(e.target.value);
            if (validationErrors.confirmPassword) {
              setValidationErrors((prev) => {
                const next = { ...prev };
                delete next.confirmPassword;
                return next;
              });
            }
          }}
          error={validationErrors.confirmPassword}
          disabled={isSubmitting || isLoading}
          autoComplete="new-password"
          required
        />

        {/* Submit Button */}
        <Button
          type="submit"
          disabled={!isFormValid || isSubmitting || isLoading}
          isLoading={isSubmitting || isLoading}
          className="w-full mt-6"
        >
          {isSubmitting || isLoading ? 'Creating Account...' : 'Create Account'}
        </Button>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">
              Already have an account?
            </span>
          </div>
        </div>

        {/* Login Link */}
        <Link
          href={`/${locale}/auth/login`}
          className="block w-full text-center px-4 py-3 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors duration-200 font-medium"
        >
          Log In
        </Link>
      </form>

      {/* Terms */}
      <div className="mt-6 pt-6 border-t border-gray-200 text-center text-xs text-gray-600">
        <p>
          By signing up, you agree to our{' '}
          <a href="#" className="text-blue-600 hover:underline">
            Terms of Service
          </a>{' '}
          and{' '}
          <a href="#" className="text-blue-600 hover:underline">
            Privacy Policy
          </a>
        </p>
      </div>
    </AuthLayout>
  );
}
