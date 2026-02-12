"use client"

/**
 * Login/Signup page with tab toggle.
 *
 * Features:
 * - Tab toggle between login and signup forms
 * - Integration with useAuth hook
 * - Redirect to dashboard on successful authentication
 * - Redirect logged-in users to dashboard (T029)
 * - Session expiry message display (T034)
 * - Error handling and display
 */

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { SignupForm } from "@/components/auth/signup-form"
import { LoginForm } from "@/components/auth/login-form"
import { useAuth } from "@/hooks/use-auth"
import { toast } from "sonner"

export default function LoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [activeTab, setActiveTab] = useState<"login" | "signup">("login")
  const [sessionExpiredMessage, setSessionExpiredMessage] = useState<string | null>(null)
  const { register, isRegistering, registerError, login, isLoggingIn, loginError } = useAuth()

  // T034: Check for session expiry message
  useEffect(() => {
    const sessionExpired = searchParams.get("session_expired")
    if (sessionExpired === "true") {
      setSessionExpiredMessage("Your session has expired. Please log in again.")
      // Clear the query parameter after showing the message
      const timer = setTimeout(() => {
        setSessionExpiredMessage(null)
      }, 5000) // Hide message after 5 seconds
      return () => clearTimeout(timer)
    }
  }, [searchParams])

  // T029: Redirect logged-in users to dashboard
  useEffect(() => {
    const token = localStorage.getItem("auth_token")
    if (token) {
      router.push("/dashboard")
    }
  }, [router])

  const handleSignup = async (data: { email: string; password: string }) => {
    try {
      await register(data)
      toast.success("Account created successfully!")
      // On success, redirect to dashboard
      router.push("/dashboard")
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Registration failed")
      console.error("Signup failed:", error)
    }
  }

  const handleLogin = async (data: { email: string; password: string }) => {
    try {
      await login(data)
      toast.success("Logged in successfully!")
      // On success, redirect to dashboard
      router.push("/dashboard")
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Login failed")
      console.error("Login failed:", error)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-4">
      <div className="w-full max-w-md">
        {/* Session expired message (T034) */}
        {sessionExpiredMessage && (
          <div
            className="mb-4 p-4 text-sm text-yellow-500 bg-yellow-50 dark:bg-yellow-900/10 rounded-md border border-yellow-200 dark:border-yellow-800"
            role="alert"
          >
            {sessionExpiredMessage}
          </div>
        )}

        {/* Tab toggle */}
        <div className="flex mb-6 bg-gray-800 rounded-lg p-1">
          <button
            onClick={() => setActiveTab("login")}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === "login"
                ? "bg-white text-gray-900"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setActiveTab("signup")}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === "signup"
                ? "bg-white text-gray-900"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            Sign Up
          </button>
        </div>

        {/* Forms */}
        {activeTab === "login" && (
          <LoginForm
            onSubmit={handleLogin}
            isLoading={isLoggingIn}
            error={loginError}
          />
        )}

        {activeTab === "signup" && (
          <SignupForm
            onSubmit={handleSignup}
            isLoading={isRegistering}
            error={registerError}
          />
        )}
      </div>
    </div>
  )
}
