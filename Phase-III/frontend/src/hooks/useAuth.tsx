// [Task]: T014, [From]: specs/002-task-ui-frontend/spec.md#US1
// Authentication Context and hook for managing user authentication state

'use client';

import { createContext, useContext, useCallback, useEffect, useState, ReactNode, FC } from 'react';
import type { AuthContextValue, User, SignupRequest, LoginRequest } from '@/types/auth';
import { saveToken, getToken, removeToken, isTokenExpired, decodeToken } from '@/utils/auth';
import { apiClient } from '@/services/api';

/**
 * Authentication Context
 * [Task]: T014, [From]: specs/002-task-ui-frontend/spec.md#US1
 */
const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * AuthProvider component - wraps application to provide auth context
 * [Task]: T014, [From]: specs/002-task-ui-frontend/spec.md#US1
 *
 * @param children - React component children
 *
 * @example
 * <AuthProvider>
 *   <App />
 * </AuthProvider>
 */
export const AuthProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load token from localStorage on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedToken = getToken();

        if (storedToken && !isTokenExpired(storedToken)) {
          // Decode token to get user info
          const decoded = decodeToken(storedToken);
          // Backend sends user_id (snake_case) not userId
          if (decoded && (decoded.user_id || decoded.userId)) {
            setToken(storedToken);
            setUser({
              id: (decoded.user_id || decoded.userId) as string,
              email: decoded.email,
              name: undefined,
              createdAt: new Date().toISOString(), // Set to current time; actual value comes from backend
            });
          } else {
            // Invalid token structure, remove it
            removeToken();
          }
        } else if (storedToken) {
          // Token is expired, remove it
          removeToken();
          setToken(null);
        }
      } catch (err) {
        console.error('Failed to initialize authentication:', err);
        removeToken();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Listen for unauthorized events (401 responses from API)
  useEffect(() => {
    const handleUnauthorized = () => {
      setUser(null);
      setToken(null);
      removeToken();
      setError('Your session has expired. Please log in again.');
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
  }, []);

  /**
   * Sign up new user
   * [Task]: T014, [From]: specs/002-task-ui-frontend/spec.md#US1
   */
  const signup = useCallback(async (email: string, password: string, name?: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const payload: SignupRequest = {
        email,
        password,
        ...(name && { name }),
      };

      // Call signup endpoint
      const response = await apiClient.post<{
        data: { user: User; token: string };
      }>('/api/auth/signup', payload);

      const { user: newUser, token: newToken } = response.data;

      // Save token and update state
      saveToken(newToken);
      setToken(newToken);
      setUser(newUser);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to sign up. Please try again.';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Log in existing user
   * [Task]: T014, [From]: specs/002-task-ui-frontend/spec.md#US1
   */
  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const payload: LoginRequest = {
        email,
        password,
      };

      // Call login endpoint
      const response = await apiClient.post<{
        data: { user: User; token: string };
      }>('/api/auth/login', payload);

      const { user: loggedInUser, token: newToken } = response.data;

      // Save token and update state
      saveToken(newToken);
      setToken(newToken);
      setUser(loggedInUser);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to log in. Please try again.';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Log out user
   * [Task]: T014, [From]: specs/002-task-ui-frontend/spec.md#US1
   */
  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    removeToken();
    setError(null);
  }, []);

  /**
   * Clear error message
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value: AuthContextValue = {
    user,
    isLoading,
    error,
    login,
    signup,
    logout,
    clearError,
    isAuthenticated: !!user && !!token,
  };

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
};

/**
 * Hook to access authentication context
 * [Task]: T014, [From]: specs/002-task-ui-frontend/spec.md#US1
 *
 * @returns Authentication context value
 * @throws Error if used outside AuthProvider
 *
 * @example
 * const { user, login, logout } = useAuth();
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}
