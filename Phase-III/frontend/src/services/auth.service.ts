// [Task]: T032, [From]: specs/002-task-ui-frontend/spec.md#US1
// Authentication Service - Handles signup, login, logout operations

import { apiClient } from '@/services/api';
import type { User, SignupRequest, LoginRequest } from '@/types/auth';
import { ApiError } from '@/types/api';

/**
 * Authentication Service
 * Handles all authentication-related API calls and token management
 * [Task]: T032, [From]: specs/002-task-ui-frontend/spec.md#US1
 */
export class AuthService {
  /**
   * Sign up a new user with email and password
   * [Task]: T032, [From]: specs/002-task-ui-frontend/spec.md#US1
   *
   * @param email - User's email address
   * @param password - User's password (must be at least 8 characters)
   * @param name - Optional user name
   * @returns Promise resolving to user object and JWT token
   * @throws ApiError if signup fails (user exists, invalid input, server error)
   *
   * @example
   * const { user, token } = await authService.signup('user@example.com', 'password123', 'John Doe');
   */
  async signup(
    email: string,
    password: string,
    name?: string
  ): Promise<{ user: User; token: string }> {
    try {
      const payload: SignupRequest = {
        email,
        password,
        ...(name && { name }),
      };

      // Call backend signup endpoint
      const response = await apiClient.post<{
        data: { user: User; token: string };
        error: null;
      }>('/api/auth/signup', payload);

      return response.data;
    } catch (error) {
      // Re-throw API errors with user-friendly messages
      if (error instanceof ApiError) {
        if (error.code === 'VALIDATION_ERROR' && error.status === 400) {
          throw new ApiError(
            'Invalid email or password format',
            error.code,
            error.status,
            error.details
          );
        }
        if (error.status === 409) {
          throw new ApiError(
            'An account with this email already exists',
            'USER_EXISTS',
            409,
            error.details
          );
        }
      }
      throw error;
    }
  }

  /**
   * Log in user with email and password
   * [Task]: T032, [From]: specs/002-task-ui-frontend/spec.md#US1
   *
   * @param email - User's email address
   * @param password - User's password
   * @returns Promise resolving to user object and JWT token
   * @throws ApiError if login fails (invalid credentials, user not found, server error)
   *
   * @example
   * const { user, token } = await authService.login('user@example.com', 'password123');
   */
  async login(email: string, password: string): Promise<{ user: User; token: string }> {
    try {
      const payload: LoginRequest = {
        email,
        password,
      };

      // Call backend login endpoint
      const response = await apiClient.post<{
        data: { user: User; token: string };
        error: null;
      }>('/api/auth/login', payload);

      return response.data;
    } catch (error) {
      // Re-throw API errors with user-friendly messages
      if (error instanceof ApiError) {
        if (error.status === 401) {
          throw new ApiError(
            'Invalid email or password. Please try again.',
            'INVALID_CREDENTIALS',
            401,
            error.details
          );
        }
        if (error.status === 404) {
          throw new ApiError(
            'No account found with this email',
            'USER_NOT_FOUND',
            404,
            error.details
          );
        }
      }
      throw error;
    }
  }

  /**
   * Log out user - clears token from client (server session termination is backend's responsibility)
   * [Task]: T032, [From]: specs/002-task-ui-frontend/spec.md#US1
   *
   * @returns Promise that resolves when logout is complete
   *
   * @example
   * await authService.logout();
   */
  async logout(): Promise<void> {
    try {
      // Call backend logout endpoint to invalidate session
      await apiClient.post<{ data: null; error: null }>('/api/auth/logout');
    } catch (error) {
      // Log error but don't throw - logout should clear client state even if server call fails
      console.warn('Logout API call failed:', error);
    }
  }

  /**
   * Verify if a token is still valid by attempting to use it
   * [Task]: T032, [From]: specs/002-task-ui-frontend/spec.md#US1
   *
   * @param token - JWT token to verify
   * @returns Promise resolving to User if token is valid, null if invalid
   *
   * @example
   * const user = await authService.verifyToken(token);
   */
  async verifyToken(token: string): Promise<User | null> {
    try {
      // Send token in Authorization header to verify endpoint
      const response = await apiClient.get<{
        data: { user: User };
        error: null;
      }>('/api/auth/verify', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      return response.data.user;
    } catch (error) {
      // Token is invalid or expired
      console.warn('Token verification failed:', error);
      return null;
    }
  }
}

// Export singleton instance
export const authService = new AuthService();
