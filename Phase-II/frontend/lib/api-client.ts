/**
 * API client for making authenticated requests to FastAPI backend.
 *
 * This client automatically includes JWT tokens in the Authorization header
 * for all requests to protected endpoints.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

/**
 * Get the current JWT token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === "undefined") {
    return null
  }

  try {
    return localStorage.getItem("auth_token")
  } catch (error) {
    console.error("Failed to get auth token:", error)
    return null
  }
}

/**
 * Make an authenticated API request to the FastAPI backend
 *
 * @param endpoint - API endpoint path (e.g., "/api/auth/register")
 * @param options - Fetch options (method, body, headers, etc.)
 * @returns Response from the API
 */
export async function apiClient<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`

  // Debug: Log the full URL being fetched
  console.log("Fetching:", url)

  // Get JWT token for authenticated requests
  const token = getAuthToken()

  // Prepare headers
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  }

  // Add Authorization header if token exists
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  // Make the request
  const response = await fetch(url, {
    ...options,
    headers,
  })

  // Handle non-OK responses
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      detail: response.statusText,
    }))

    throw new Error(errorData.detail || `API request failed: ${response.status}`)
  }

  // Parse and return JSON response
  return response.json()
}

/**
 * Convenience methods for common HTTP verbs
 */
export const api = {
  /**
   * GET request
   */
  get: <T = any>(endpoint: string, options?: RequestInit) =>
    apiClient<T>(endpoint, { ...options, method: "GET" }),

  /**
   * POST request
   */
  post: <T = any>(endpoint: string, data?: any, options?: RequestInit) =>
    apiClient<T>(endpoint, {
      ...options,
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    }),

  /**
   * PUT request
   */
  put: <T = any>(endpoint: string, data?: any, options?: RequestInit) =>
    apiClient<T>(endpoint, {
      ...options,
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    }),

  /**
   * PATCH request
   */
  patch: <T = any>(endpoint: string, data?: any, options?: RequestInit) =>
    apiClient<T>(endpoint, {
      ...options,
      method: "PATCH",
      body: data ? JSON.stringify(data) : undefined,
    }),

  /**
   * DELETE request
   */
  delete: <T = any>(endpoint: string, options?: RequestInit) =>
    apiClient<T>(endpoint, { ...options, method: "DELETE" }),
}

/**
 * Type definitions for API responses
 */
export interface UserResponse {
  id: string
  email: string
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: UserResponse
}

export interface ErrorResponse {
  detail: string
}
