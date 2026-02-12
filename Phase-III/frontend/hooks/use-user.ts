"use client"

/**
 * User hook using TanStack Query for fetching and caching current user data.
 *
 * Features:
 * - Fetch current user from localStorage (Better Auth integration)
 * - Cache user data with TanStack Query
 * - Auto-refetch on window focus
 * - Handle authentication state
 * - Session expiry detection
 */

import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

interface User {
  id: string
  email: string
  created_at: string
}

/**
 * Hook for fetching and managing current user data.
 */
export function useUser() {
  const router = useRouter()

  const {
    data: user,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["user"],
    queryFn: async (): Promise<User | null> => {
      // Check if we're in the browser
      if (typeof window === "undefined") {
        return null
      }

      // Get token from localStorage
      const token = localStorage.getItem("auth_token")
      if (!token) {
        return null
      }

      // Get user data from localStorage
      const userStr = localStorage.getItem("user")
      if (!userStr) {
        return null
      }

      try {
        const userData = JSON.parse(userStr)
        return userData as User
      } catch (error) {
        console.error("Failed to parse user data:", error)
        return null
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: true,
    retry: false,
  })

  // Handle session expiry
  useEffect(() => {
    if (error) {
      // Clear auth data and redirect to login
      if (typeof window !== "undefined") {
        localStorage.removeItem("auth_token")
        localStorage.removeItem("user")
      }
      router.push("/login?session_expired=true")
    }
  }, [error, router])

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    error,
    refetch,
  }
}
