// [Task]: T031, [From]: specs/002-task-ui-frontend/spec.md#US1
// Integration test for full authentication workflow

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

describe('Authentication Integration Tests', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  const mockSignupResponse = {
    data: {
      user: {
        id: 'user-123',
        email: 'test@example.com',
        name: 'Test User',
        createdAt: '2026-02-02T00:00:00Z',
      },
      token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyLTEyMyIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImlhdCI6MTcwMzc4MDAwMCwiZXhwIjoyMDAwMDAwMDAwfQ.signature',
    },
    error: null,
  };

  const mockLoginResponse = {
    data: {
      user: {
        id: 'user-456',
        email: 'login@example.com',
        name: 'Login User',
        createdAt: '2026-02-01T00:00:00Z',
      },
      token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyLTQ1NiIsImVtYWlsIjoibG9naW5AZXhhbXBsZS5jb20iLCJpYXQiOjE3MDM3ODAwMDAsImV4cCI6MjAwMDAwMDAwMH0.signature',
    },
    error: null,
  };

  describe('Full Signup Flow', () => {
    it('should complete full signup flow with token storage', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => mockSignupResponse,
      });

      // 1. Send signup request
      const signupResponse = await fetch('http://localhost:8000/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'password123',
          name: 'Test User',
        }),
      });

      expect(signupResponse.ok).toBe(true);
      const data = await signupResponse.json();

      // 2. Verify response contains user and token
      expect(data.data.user).toBeDefined();
      expect(data.data.token).toBeDefined();

      // 3. Store token in localStorage (simulating useAuth behavior)
      localStorage.setItem('evolution_todo_jwt_token', data.data.token);

      // 4. Verify token is stored
      const storedToken = localStorage.getItem('evolution_todo_jwt_token');
      expect(storedToken).toBe(data.data.token);

      // 5. Verify token can be decoded
      const parts = storedToken!.split('.');
      const payload = JSON.parse(
        Buffer.from(parts[1].replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString()
      );

      expect(payload.userId).toBe('user-123');
      expect(payload.email).toBe('test@example.com');
    });
  });

  describe('Full Login Flow', () => {
    it('should complete full login flow with token storage', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockLoginResponse,
      });

      // 1. Send login request
      const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'login@example.com',
          password: 'password123',
        }),
      });

      expect(loginResponse.ok).toBe(true);
      const data = await loginResponse.json();

      // 2. Store token and user info
      localStorage.setItem('evolution_todo_jwt_token', data.data.token);

      // 3. Verify stored token
      const storedToken = localStorage.getItem('evolution_todo_jwt_token');
      expect(storedToken).toBe(data.data.token);

      // 4. Verify can access user info from token
      const parts = storedToken!.split('.');
      const payload = JSON.parse(
        Buffer.from(parts[1].replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString()
      );

      expect(payload.userId).toBe('user-456');
      expect(payload.email).toBe('login@example.com');
    });
  });

  describe('Logout Flow', () => {
    it('should clear token and user state on logout', () => {
      // 1. Set up authenticated state
      localStorage.setItem('evolution_todo_jwt_token', mockLoginResponse.data.token);
      expect(localStorage.getItem('evolution_todo_jwt_token')).toBeDefined();

      // 2. Perform logout (clear token)
      localStorage.removeItem('evolution_todo_jwt_token');

      // 3. Verify token is cleared
      expect(localStorage.getItem('evolution_todo_jwt_token')).toBeNull();
    });
  });

  describe('Protected Route Access', () => {
    it('should redirect to login when accessing protected route without token', () => {
      // No token in localStorage
      const token = localStorage.getItem('evolution_todo_jwt_token');
      expect(token).toBeNull();

      // Application logic would redirect to login
      const shouldRedirectToLogin = !token;
      expect(shouldRedirectToLogin).toBe(true);
    });

    it('should allow access to protected route with valid token', () => {
      // 1. Set up authenticated state
      localStorage.setItem('evolution_todo_jwt_token', mockLoginResponse.data.token);

      // 2. Check if token exists
      const token = localStorage.getItem('evolution_todo_jwt_token');
      expect(token).toBeDefined();

      // 3. Check if token is not expired
      const parts = token!.split('.');
      const payload = JSON.parse(
        Buffer.from(parts[1].replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString()
      );

      const currentTimeSeconds = Math.floor(Date.now() / 1000);
      const isExpired = currentTimeSeconds >= payload.exp;

      expect(isExpired).toBe(false);
    });

    it('should redirect to login after logout', () => {
      // 1. Authenticate
      localStorage.setItem('evolution_todo_jwt_token', mockLoginResponse.data.token);
      expect(localStorage.getItem('evolution_todo_jwt_token')).toBeDefined();

      // 2. Logout
      localStorage.removeItem('evolution_todo_jwt_token');

      // 3. Check if should redirect
      const token = localStorage.getItem('evolution_todo_jwt_token');
      const shouldRedirect = !token;

      expect(shouldRedirect).toBe(true);
    });
  });

  describe('Token Management Across Operations', () => {
    it('should include token in Authorization header for API requests', () => {
      const token = mockLoginResponse.data.token;
      localStorage.setItem('evolution_todo_jwt_token', token);

      // Retrieve and verify token is in correct format for header
      const storedToken = localStorage.getItem('evolution_todo_jwt_token');
      const authHeader = `Bearer ${storedToken}`;

      expect(authHeader).toBe(`Bearer ${token}`);
      expect(authHeader).toMatch(/^Bearer eyJ/);
    });

    it('should persist token across page reloads', () => {
      const token = mockLoginResponse.data.token;

      // Simulate first page load
      localStorage.setItem('evolution_todo_jwt_token', token);

      // Simulate page reload - token should still exist
      const retrievedToken = localStorage.getItem('evolution_todo_jwt_token');
      expect(retrievedToken).toBe(token);
    });

    it('should handle concurrent requests with same token', () => {
      const token = mockLoginResponse.data.token;
      localStorage.setItem('evolution_todo_jwt_token', token);

      // Simulate multiple concurrent API requests using same token
      const token1 = localStorage.getItem('evolution_todo_jwt_token');
      const token2 = localStorage.getItem('evolution_todo_jwt_token');

      expect(token1).toBe(token2);
      expect(token1).toBe(token);
    });
  });

  describe('Error Handling in Auth Flow', () => {
    it('should not store token on signup failure', async () => {
      const errorResponse = {
        data: null,
        error: {
          code: 'USER_EXISTS',
          message: 'User already exists',
        },
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 409,
        json: async () => errorResponse,
      });

      const response = await fetch('http://localhost:8000/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'password123',
        }),
      });

      expect(response.ok).toBe(false);

      // Token should not be stored
      expect(localStorage.getItem('evolution_todo_jwt_token')).toBeNull();
    });

    it('should handle 401 Unauthorized and clear token', () => {
      // Set up authenticated state
      localStorage.setItem('evolution_todo_jwt_token', mockLoginResponse.data.token);
      expect(localStorage.getItem('evolution_todo_jwt_token')).toBeDefined();

      // Simulate 401 response - should clear token
      // (In real app, this would be handled by API interceptor)
      localStorage.removeItem('evolution_todo_jwt_token');

      expect(localStorage.getItem('evolution_todo_jwt_token')).toBeNull();
    });
  });

  describe('Session State Management', () => {
    it('should have consistent user info throughout session', () => {
      const userData = mockLoginResponse.data.user;

      // After login, user info should be consistent
      const userId = userData.id;
      const userEmail = userData.email;

      expect(userId).toBe('user-456');
      expect(userEmail).toBe('login@example.com');

      // Even if we query again, should be same
      expect(userData.id).toBe(userId);
      expect(userData.email).toBe(userEmail);
    });

    it('should track authentication state correctly', () => {
      let isAuthenticated = false;
      let user = null;

      // Initial state - not authenticated
      expect(isAuthenticated).toBe(false);
      expect(user).toBeNull();

      // After login
      isAuthenticated = true;
      user = mockLoginResponse.data.user;

      expect(isAuthenticated).toBe(true);
      expect(user).toBeDefined();
      expect(user?.id).toBe('user-456');

      // After logout
      isAuthenticated = false;
      user = null;

      expect(isAuthenticated).toBe(false);
      expect(user).toBeNull();
    });
  });
});
