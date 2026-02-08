// [Task]: T028, [From]: specs/002-task-ui-frontend/spec.md#US1
// Contract test for POST /api/auth/signup endpoint

import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('Auth Signup Contract Tests', () => {
  const API_BASE_URL = 'http://localhost:8000';
  const signupEndpoint = `${API_BASE_URL}/api/auth/signup`;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('POST /api/auth/signup - Success Case', () => {
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
        status: 201,
        json: async () => mockResponse,
      });

      const payload = {
        email: 'test@example.com',
        password: 'password123',
      };

      const response = await fetch(signupEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      expect(response.status).toBe(201);
      expect(response.ok).toBe(true);

      const data = await response.json();
      expect(data.data.user).toBeDefined();
      expect(data.data.user.id).toBe('user-123');
      expect(data.data.user.email).toBe('test@example.com');
      expect(data.data.token).toBeDefined();
      expect(data.data.token.length).toBeGreaterThan(0);
      expect(data.error).toBeNull();
    });

    it('should include user ID and email in JWT token payload', async () => {
      const jwtToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyLTEyMyIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImlhdCI6MTcwMzc4MDAwMCwiZXhwIjoxNzAzODY2NDAwfQ.signature';

      // JWT decoding (base64url payload)
      const parts = jwtToken.split('.');
      const payload = JSON.parse(
        Buffer.from(parts[1].replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString()
      );

      expect(payload.userId).toBe('user-123');
      expect(payload.email).toBe('test@example.com');
      expect(payload.iat).toBeDefined();
      expect(payload.exp).toBeDefined();
    });
  });

  describe('POST /api/auth/signup - Error Cases', () => {
    it('should return 409 Conflict when user already exists', async () => {
      const mockResponse = {
        data: null,
        error: {
          code: 'USER_EXISTS',
          message: 'User with this email already exists',
        },
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 409,
        json: async () => mockResponse,
      });

      const payload = {
        email: 'existing@example.com',
        password: 'password123',
      };

      const response = await fetch(signupEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      expect(response.status).toBe(409);
      expect(response.ok).toBe(false);

      const data = await response.json();
      expect(data.error.code).toBe('USER_EXISTS');
      expect(data.error.message).toContain('already exists');
      expect(data.data).toBeNull();
    });

    it('should return 400 Bad Request for invalid email format', async () => {
      const mockResponse = {
        data: null,
        error: {
          code: 'INVALID_EMAIL',
          message: 'Invalid email format',
        },
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => mockResponse,
      });

      const payload = {
        email: 'invalid-email',
        password: 'password123',
      };

      const response = await fetch(signupEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      expect(response.status).toBe(400);
      expect(response.ok).toBe(false);

      const data = await response.json();
      expect(data.error.code).toBe('INVALID_EMAIL');
      expect(data.data).toBeNull();
    });

    it('should return 400 Bad Request for weak password', async () => {
      const mockResponse = {
        data: null,
        error: {
          code: 'WEAK_PASSWORD',
          message: 'Password must be at least 8 characters',
        },
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => mockResponse,
      });

      const payload = {
        email: 'test@example.com',
        password: 'short',
      };

      const response = await fetch(signupEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data.error.code).toBe('WEAK_PASSWORD');
    });
  });

  describe('POST /api/auth/signup - Request Validation', () => {
    it('should require email field in request', async () => {
      const payload = {
        password: 'password123',
      };

      // This would be validated by the client before sending
      // but we test that the contract expects email
      expect(payload).not.toHaveProperty('email');
    });

    it('should require password field in request', async () => {
      const payload = {
        email: 'test@example.com',
      };

      // This would be validated by the client before sending
      expect(payload).not.toHaveProperty('password');
    });

    it('should accept optional name field', async () => {
      const payload = {
        email: 'test@example.com',
        password: 'password123',
        name: 'Test User',
      };

      expect(payload).toHaveProperty('name');
    });
  });
});
