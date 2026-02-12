"use client"

/**
 * Login form component for user authentication.
 *
 * Features:
 * - Email and password input with validation
 * - Form validation using react-hook-form
 * - Error display for login failures
 * - Integration with useAuth hook for login mutation
 */

import { useState } from "react"
import { useForm } from "react-hook-form"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface LoginFormData {
  email: string
  password: string
}

interface LoginFormProps {
  onSubmit: (data: LoginFormData) => Promise<void>
  isLoading?: boolean
  error?: string | null
}

export function LoginForm({ onSubmit, isLoading = false, error = null }: LoginFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>()

  const [localError, setLocalError] = useState<string | null>(null)

  const handleFormSubmit = async (data: LoginFormData) => {
    try {
      setLocalError(null)
      await onSubmit(data)
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : "Login failed")
    }
  }

  const displayError = error || localError

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Welcome back</CardTitle>
        <CardDescription>
          Enter your email and password to access your account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={handleSubmit(handleFormSubmit)}
          className="space-y-4"
          aria-label="Login form"
        >
          {/* Email field */}
          <div className="space-y-2">
            <Label htmlFor="login-email">
              Email <span className="text-red-500" aria-label="required">*</span>
            </Label>
            <Input
              id="login-email"
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
              aria-describedby={errors.email ? "login-email-error" : undefined}
              aria-required="true"
            />
            {errors.email && (
              <p id="login-email-error" className="text-sm text-red-500" role="alert">
                {errors.email.message}
              </p>
            )}
          </div>

          {/* Password field */}
          <div className="space-y-2">
            <Label htmlFor="login-password">
              Password <span className="text-red-500" aria-label="required">*</span>
            </Label>
            <Input
              id="login-password"
              type="password"
              placeholder="Enter your password"
              autoComplete="current-password"
              {...register("password", {
                required: "Password is required",
              })}
              disabled={isLoading}
              aria-invalid={errors.password ? "true" : "false"}
              aria-describedby={errors.password ? "login-password-error" : undefined}
              aria-required="true"
            />
            {errors.password && (
              <p id="login-password-error" className="text-sm text-red-500" role="alert">
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
            {isLoading ? "Logging in..." : "Log in"}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
