"use client"

/**
 * Protected route layout wrapper.
 *
 * Features:
 * - Check authentication status using useUser hook
 * - Redirect to login if unauthenticated
 * - Show loading state while checking authentication
 * - Wrap all protected pages (dashboard, etc.)
 */

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useUser } from "@/hooks/use-user"

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { user, isLoading, isAuthenticated } = useUser()

  useEffect(() => {
    // If not loading and not authenticated, redirect to login
    if (!isLoading && !isAuthenticated) {
      router.push("/login")
    }
  }, [isLoading, isAuthenticated, router])

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-white border-r-transparent"></div>
          <p className="mt-4 text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  // If not authenticated, show nothing (redirect is in progress)
  if (!isAuthenticated) {
    return null
  }

  // Render protected content
  return <>{children}</>
}
