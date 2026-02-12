"use client"

/**
 * Signup form component for user registration.
 *
 * Features:
 * - Email and password input with validation
 * - Form validation using react-hook-form
 * - Error display for registration failures
 * - Integration with useAuth hook for registration mutation
 */

import { useState } from "react"
import { useForm } from "react-hook-form"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface SignupFormData {
  email: string
  password: string
}

interface SignupFormProps {
  onSubmit: (data: SignupFormData) => Promise<void>
  isLoading?: boolean
  error?: string | null
}

export function SignupForm({ onSubmit, isLoading = false, error = null }: SignupFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupFormData>()

  const [localError, setLocalError] = useState<string | null>(null)

  const handleFormSubmit = async (data: SignupFormData) => {
    try {
      setLocalError(null)
      await onSubmit(data)
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : "Registration failed")
    }
  }

  const displayError = error || localError

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Create an account</CardTitle>
        <CardDescription>
          Enter your email and password to create your account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={handleSubmit(handleFormSubmit)}
          className="space-y-4"
          aria-label="Sign up form"
        >
          {/* Email field */}
          <div className="space-y-2">
            <Label htmlFor="email">
              Email <span className="text-red-500" aria-label="required">*</span>
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="user@example.com"
              autoComplete="email"
              {...register("email", {
                required: "Email is required",
                pattern: {
                  value: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
                  message: "Please enter a valid email address",
                },
              })}
              disabled={isLoading}
              aria-invalid={errors.email ? "true" : "false"}
              aria-describedby={errors.email ? "email-error" : undefined}
              aria-required="true"
            />
            {errors.email && (
              <p id="email-error" className="text-sm text-red-500" role="alert">
                {errors.email.message}
              </p>
            )}
          </div>

          {/* Password field */}
          <div className="space-y-2">
            <Label htmlFor="password">
              Password <span className="text-red-500" aria-label="required">*</span>
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="Minimum 8 characters"
              autoComplete="new-password"
              {...register("password", {
                required: "Password is required",
                minLength: {
                  value: 8,
                  message: "Password must be at least 8 characters",
                },
              })}
              disabled={isLoading}
              aria-invalid={errors.password ? "true" : "false"}
              aria-describedby={errors.password ? "password-error password-hint" : "password-hint"}
              aria-required="true"
            />
            <p id="password-hint" className="text-xs text-gray-400">
              Must be at least 8 characters long
            </p>
            {errors.password && (
              <p id="password-error" className="text-sm text-red-500" role="alert">
                {errors.password.message}
              </p>
            )}
          </div>

          {/* Error message */}
          {displayError && (
            <div
              className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/10 rounded-md"
              role="alert"
              aria-live="polite"
            >
              {displayError}
            </div>
          )}

          {/* Submit button */}
          <Button
            type="submit"
            className="w-full"
            disabled={isLoading}
            aria-busy={isLoading}
          >
            {isLoading ? "Creating account..." : "Sign up"}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
