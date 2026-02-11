"use client"

/**
 * Dashboard page - protected route for authenticated users.
 *
 * This is a placeholder for User Story 1 testing.
 * Full dashboard implementation will come in later user stories.
 */

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem("auth_token")
    const userData = localStorage.getItem("user")

    if (!token || !userData) {
      // Redirect to login if not authenticated
      router.push("/login")
      return
    }

    setUser(JSON.parse(userData))
  }, [router])

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-2">Welcome!</h2>
          <p className="text-gray-400 mb-4">
            You are successfully logged in as: <span className="text-white">{user.email}</span>
          </p>
          <p className="text-sm text-gray-500">
            User ID: {user.id}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Account created: {new Date(user.created_at).toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  )
}
