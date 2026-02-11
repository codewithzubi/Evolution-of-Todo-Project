"use client"

/**
 * Authentication hook using TanStack Query.
 *
 * Provides:
 * - Registration mutation
 * - Login mutation (User Story 2)
 * - Logout mutation (User Story 4)
 * - Loading states and error handling
 */

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { api, TokenResponse } from "@/lib/api-client"

interface RegisterData {
  email: string
  password: string
}

interface LoginData {
  email: string
  password: string
}

/**
 * Hook for authentication operations.
 */
export function useAuth() {
  const queryClient = useQueryClient()

  // Registration mutation
  const registerMutation = useMutation({
    mutationFn: async (data: RegisterData): Promise<TokenResponse> => {
      return api.post<TokenResponse>("/api/auth/register", data)
    },
    onSuccess: (data) => {
      // Clear any cached data from previous user before storing new user data
      queryClient.clear()

      // Store token in localStorage (Better Auth will handle this in production)
      if (typeof window !== "undefined") {
        localStorage.setItem("auth_token", data.access_token)
        localStorage.setItem("user", JSON.stringify(data.user))
      }
    },
  })

  // Login mutation (User Story 2 - placeholder)
  const loginMutation = useMutation({
    mutationFn: async (data: LoginData): Promise<TokenResponse> => {
      return api.post<TokenResponse>("/api/auth/login", data)
    },
    onSuccess: (data) => {
      // Clear any cached data from previous user before storing new user data
      queryClient.clear()

      // Store token in localStorage
      if (typeof window !== "undefined") {
        localStorage.setItem("auth_token", data.access_token)
        localStorage.setItem("user", JSON.stringify(data.user))
      }
    },
  })

  // Logout mutation (User Story 4 - placeholder)
  const logoutMutation = useMutation({
    mutationFn: async (): Promise<void> => {
      await api.post("/api/auth/logout")
    },
    onSuccess: () => {
      // Clear token from localStorage
      if (typeof window !== "undefined") {
        localStorage.removeItem("auth_token")
        localStorage.removeItem("user")
      }

      // Clear TanStack Query cache to prevent previous user's data from appearing
      queryClient.clear()
    },
  })

  return {
    // Registration
    register: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,
    registerError: registerMutation.error?.message || null,

    // Login
    login: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error?.message || null,

    // Logout
    logout: logoutMutation.mutateAsync,
    isLoggingOut: logoutMutation.isPending,
    logoutError: logoutMutation.error?.message || null,
  }
}
