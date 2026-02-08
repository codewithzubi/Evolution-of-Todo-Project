// [Task]: T-004, [From]: specs/002-task-ui-frontend/spec.md#FR-003
// Base API client with JWT token handling and authentication

import { ApiError, ApiErrorCode, type ApiResult } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const JWT_TOKEN_KEY = 'evolution_todo_jwt_token';

/**
 * API Client Service
 * Handles all HTTP requests with automatic JWT token injection,
 * error handling, response parsing, and token refresh logic.
 * [Task]: T038, [From]: specs/002-task-ui-frontend/spec.md#US1
 */
class ApiClient {
  private baseUrl: string;
  private isRefreshing = false;
  private refreshQueue: Array<() => void> = [];

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Get JWT token from localStorage
   */
  private getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(JWT_TOKEN_KEY);
  }

  /**
   * Set JWT token in localStorage
   */
  setToken(token: string): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(JWT_TOKEN_KEY, token);
  }

  /**
   * Clear JWT token from localStorage
   */
  clearToken(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(JWT_TOKEN_KEY);
  }

  /**
   * Build authorization header with JWT token
   */
  private getAuthHeaders(): Record<string, string> {
    const token = this.getToken();
    if (!token) return {};
    return {
      Authorization: `Bearer ${token}`,
    };
  }

  /**
   * Refresh the JWT token
   * [Task]: T038, [From]: specs/002-task-ui-frontend/spec.md#US1
   */
  private async refreshToken(): Promise<boolean> {
    try {
      const token = this.getToken();
      if (!token) {
        return false;
      }

      const response = await fetch(`${this.baseUrl}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        return false;
      }

      const data = await response.json();
      if (data.data?.token) {
        this.setToken(data.data.token);
        return true;
      }

      return false;
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  }

  /**
   * Queue request while token is being refreshed
   * [Task]: T038, [From]: specs/002-task-ui-frontend/spec.md#US1
   */
  private queueRequest(callback: () => void): void {
    this.refreshQueue.push(callback);
  }

  /**
   * Process queued requests after token refresh
   * [Task]: T038, [From]: specs/002-task-ui-frontend/spec.md#US1
   */
  private processQueue(): void {
    this.refreshQueue.forEach((callback) => callback());
    this.refreshQueue = [];
  }

  /**
   * Make HTTP request with automatic JWT injection
   * [Task]: T-004, [From]: specs/002-task-ui-frontend/spec.md#FR-003
   */
  async request<T>(
    endpoint: string,
    options: RequestInit & { params?: Record<string, unknown> } = {}
  ): Promise<T> {
    const { params, ...fetchOptions } = options;

    // Build URL with query parameters
    const url = new URL(`${this.baseUrl}${endpoint}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    // Merge headers
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...this.getAuthHeaders(),
      ...(fetchOptions.headers as Record<string, string>),
    };

    try {
      let response = await fetch(url.toString(), {
        ...fetchOptions,
        headers,
      });

      // Handle 401 Unauthorized - attempt token refresh
      // [Task]: T038, [From]: specs/002-task-ui-frontend/spec.md#US1
      if (response.status === 401) {
        // Avoid multiple simultaneous refresh attempts
        if (!this.isRefreshing) {
          this.isRefreshing = true;

          // Try to refresh token
          const refreshed = await this.refreshToken();
          this.isRefreshing = false;

          if (refreshed) {
            // Token refreshed successfully, retry original request
            const newHeaders: Record<string, string> = {
              'Content-Type': 'application/json',
              ...this.getAuthHeaders(),
              ...(fetchOptions.headers as Record<string, string>),
            };

            response = await fetch(url.toString(), {
              ...fetchOptions,
              headers: newHeaders,
            });

            // Process any queued requests
            this.processQueue();
          } else {
            // Refresh failed - clear token and trigger logout
            this.clearToken();
            if (typeof window !== 'undefined') {
              window.dispatchEvent(new Event('auth:unauthorized'));
            }
            throw new ApiError(
              'Unauthorized. Please log in again.',
              ApiErrorCode.UNAUTHORIZED,
              401
            );
          }
        } else {
          // Token is already being refreshed, queue this request
          return new Promise((resolve, reject) => {
            this.queueRequest(async () => {
              try {
                const retryResponse = await fetch(url.toString(), {
                  ...fetchOptions,
                  headers,
                });
                if (!retryResponse.ok) {
                  const errorData = await retryResponse.json();
                  reject(
                    new ApiError(
                      errorData.error?.message || `HTTP ${retryResponse.status}`,
                      ApiErrorCode.UNAUTHORIZED,
                      retryResponse.status
                    )
                  );
                } else {
                  resolve(retryResponse.json());
                }
              } catch (err) {
                reject(err);
              }
            });
          });
        }
      }

      // Handle other HTTP errors
      if (!response.ok) {
        let errorData: { error?: { message?: string; code?: string } } = {};
        try {
          errorData = await response.json();
        } catch {
          // If response body is not JSON, use default error message
        }

        const errorMessage =
          errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`;
        const errorCode = errorData.error?.code || ApiErrorCode.SERVER_ERROR;

        throw new ApiError(errorMessage, errorCode, response.status, errorData);
      }

      // Handle 204 No Content - no response body to parse
      if (response.status === 204) {
        return undefined as T;
      }

      // Parse response as JSON
      const data = await response.json();
      return data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }

      if (error instanceof TypeError) {
        throw new ApiError(
          'Network error. Please check your connection.',
          ApiErrorCode.NETWORK_ERROR,
          0
        );
      }

      throw new ApiError(
        'An unknown error occurred',
        ApiErrorCode.UNKNOWN_ERROR,
        0,
        error instanceof Error ? error.message : String(error)
      );
    }
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string, options?: RequestInit & { params?: Record<string, unknown> }): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  /**
   * PUT request
   */
  async put<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  /**
   * PATCH request
   */
  async patch<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

export type { ApiResult };
export { ApiError, ApiErrorCode };
