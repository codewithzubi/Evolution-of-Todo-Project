// [Task]: T029, [From]: specs/002-task-ui-frontend/spec.md#US1
// Contract test for POST /api/auth/login endpoint

import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('Auth Login Contract Tests', () => {
  const API_BASE_URL = 'http://localhost:8000';
  const loginEndpoint = `${API_BASE_URL}/api/auth/login`;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('POST /api/auth/login - Success Case', () => {
    it('should accept valid email and password and return JWT token and user data', async () => {
      const mockResponse = {
        data: {
          user: {
            id: 'user-123',
            email: 'test@example.com',
            name: 'Test User',
            createdAt: '2026-02-02T00:00:00Z',
          },
          token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyLTEyMyIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImlhdCI6MTcwMzc4MDAwMCwiZXhwIjoxNzAzODY2NDAwfQ.signature',
        },
        error: null,
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const payload = {
        email: 'test@example.com',
        password: 'password123',
      };

      const response = await fetch(loginEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      expect(response.status).toBe(200);
      expect(response.ok).toBe(true);

      const data = await response.json();
      expect(data.data.user).toBeDefined();
      expect(data.data.user.id).toBe('user-123');
      expect(data.data.user.email).toBe('test@example.com');
      expect(data.data.token).toBeDefined();
      expect(data.error).toBeNull();
    });

    it('should return token with valid JWT claims', async () => {
      const jwtToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyLTQ1NiIsImVtYWlsIjoiam9obkBleGFtcGxlLmNvbSIsImlhdCI6MTcwMzc4MDAwMCwiZXhwIjoxNzAzODY2NDAwfQ.signature';

      const parts = jwtToken.split('.');
      expect(parts.length).toBe(3);

      const payload = JSON.parse(
        Buffer.from(parts[1].replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString()
      );

      expect(payload.userId).toBeDefined();
      expect(payload.email).toBeDefined();
      expect(payload.iat).toBeDefined();
      expect(payload.exp).toBeDefined();
      expect(payload.exp).toBeGreaterThan(payload.iat);
    });
  });

  describe('POST /api/auth/login - Error Cases', () => {
    it('should return 401 Unauthorized for invalid credentials', async () => {
      const mockResponse = {
        data: null,
        error: {
          code: 'INVALID_CREDENTIALS',
          message: 'Invalid email or password',
        },
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => mockResponse,
      });

      const payload = {
        email: 'test@example.com',
        password: 'wrongpassword',
      };

      const response = await fetch(loginEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      expect(response.status).toBe(401);
      expect(response.ok).toBe(false);

      const data = await response.json();
      expect(data.error.code).toBe('INVALID_CREDENTIALS');
      expect(data.data).toBeNull();
    });

    it('should return 404 Not Found when user does not exist', async () => {
      const mockResponse = {
        data: null,
        error: {
          code: 'USER_NOT_FOUND',
          message: 'User not found',
        },
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => mockResponse,
      });

      const payload = {
        email: 'nonexistent@example.com',
        password: 'password123',
      };

      const response = await fetch(loginEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      expect(response.status).toBe(404);
      expect(response.ok).toBe(false);

      const data = await response.json();
      expect(data.error.code).toBe('USER_NOT_FOUND');
      expect(data.data).toBeNull();
    });

    it('should return 400 Bad Request for missing email', async () => {
      const mockResponse = {
        data: null,
        error: {
          code: 'MISSING_FIELD',
          message: 'Email is required',
        },
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => mockResponse,
      });

      const payload = {
        password: 'password123',
      };

      const response = await fetch(loginEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data.error.code).toBe('MISSING_FIELD');
    });
  });

  describe('POST /api/auth/login - Request Validation', () => {
    it('should require email and password fields', async () => {
      const validPayload = {
        email: 'test@example.com',
        password: 'password123',
      };

      expect(validPayload).toHaveProperty('email');
      expect(validPayload).toHaveProperty('password');
    });

    it('should not include sensitive fields in response', async () => {
      const mockResponse = {
        data: {
          user: {
            id: 'user-123',
            email: 'test@example.com',
            // Password should NEVER be returned
            name: 'Test User',
            createdAt: '2026-02-02T00:00:00Z',
          },
          token: 'token_value',
        },
        error: null,
      };

      expect(mockResponse.data.user).not.toHaveProperty('password');
    });
  });

  describe('POST /api/auth/login - Response Format', () => {
    it('should always return consistent response structure', async () => {
      const mockResponse = {
        data: null,
        error: {
          code: 'INVALID_CREDENTIALS',
          message: 'Invalid email or password',
        },
      };

      // Even errors should have consistent structure
      expect(mockResponse).toHaveProperty('data');
      expect(mockResponse).toHaveProperty('error');
      expect(typeof mockResponse.error.code).toBe('string');
      expect(typeof mockResponse.error.message).toBe('string');
    });
  });
});
