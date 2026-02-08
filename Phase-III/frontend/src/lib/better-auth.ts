// [Task]: T033, [From]: specs/002-task-ui-frontend/spec.md#US1
// Better Auth configuration and client setup

import { betterAuth } from 'better-auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/**
 * Better Auth Client Configuration
 * [Task]: T033, [From]: specs/002-task-ui-frontend/spec.md#US1
 *
 * Configures Better Auth for:
 * - Email/password authentication
 * - JWT token management
 * - Token refresh and expiration handling
 * - Integration with backend API
 */
export const auth = betterAuth({
  baseURL: API_BASE_URL,
  basePath: '/api/auth',
  secret: process.env.BETTER_AUTH_SECRET || 'dev-secret-key',
  database: {
    type: 'custom',
    // Custom database connector would go here for production
    // For now, relies on backend handling
  },
  plugins: [],
  trustedOrigins: [
    process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  ],
});

/**
 * Better Auth API Client
 * Wrapper around Better Auth for easier use in components and services
 */
export const betterAuthClientInstance = {
  /**
   * Sign up user with email and password
   *
   * @param email - User's email
   * @param password - User's password (min 8 chars)
   * @param name - Optional user name
   * @returns JWT token and user data
   */
  async signup(email: string, password: string, name?: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          ...(name && { name }),
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || 'Signup failed');
      }

      return await response.json();
    } catch (error) {
      throw error;
    }
  },

  /**
   * Sign in user with email and password
   *
   * @param email - User's email
   * @param password - User's password
   * @returns JWT token and user data
   */
  async signin(email: string, password: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || 'Login failed');
      }

      return await response.json();
    } catch (error) {
      throw error;
    }
  },

  /**
   * Sign out user and clear session
   */
  async signout() {
    try {
      const token = typeof window !== 'undefined'
        ? localStorage.getItem('evolution_todo_jwt_token')
        : null;

      if (token) {
        await fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        });
      }

      // Clear local storage regardless of API response
      if (typeof window !== 'undefined') {
        localStorage.removeItem('evolution_todo_jwt_token');
      }
    } catch (error) {
      // Even if logout API fails, clear local storage
      if (typeof window !== 'undefined') {
        localStorage.removeItem('evolution_todo_jwt_token');
      }
      console.warn('Logout failed:', error);
    }
  },

  /**
   * Refresh authentication token
   * Attempts to get a new token from the backend
   */
  async refreshToken() {
    try {
      const token = typeof window !== 'undefined'
        ? localStorage.getItem('evolution_todo_jwt_token')
        : null;

      if (!token) {
        throw new Error('No token found');
      }

      const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      if (data.data?.token) {
        if (typeof window !== 'undefined') {
          localStorage.setItem('evolution_todo_jwt_token', data.data.token);
        }
        return data.data;
      }

      throw new Error('No token in refresh response');
    } catch (error) {
      // Refresh failed - logout user
      if (typeof window !== 'undefined') {
        localStorage.removeItem('evolution_todo_jwt_token');
        window.dispatchEvent(new Event('auth:unauthorized'));
      }
      throw error;
    }
  },
};

export const betterAuthClient = betterAuthClientInstance;
