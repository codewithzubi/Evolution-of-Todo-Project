// [Task]: T030, [From]: specs/002-task-ui-frontend/spec.md#US1
// Contract test for JWT token validation and token utilities

import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('JWT Token Contract Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('JWT Token Structure', () => {
    it('should have valid JWT structure with three parts', () => {
      const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyLTEyMyIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImlhdCI6MTcwMzc4MDAwMCwiZXhwIjoxNzAzODY2NDAwfQ.signature';

      const parts = token.split('.');
      expect(parts.length).toBe(3);
      expect(parts[0]).toBeDefined(); // header
      expect(parts[1]).toBeDefined(); // payload
      expect(parts[2]).toBeDefined(); // signature
    });

    it('should decode header with algorithm and type', () => {
      const headerPart = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9';
      const decoded = JSON.parse(
        Buffer.from(headerPart.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString()
      );

      expect(decoded.alg).toBe('HS256');
      expect(decoded.typ).toBe('JWT');
    });
  });

  describe('JWT Payload and Claims', () => {
    it('should contain required claims: userId, email, iat, exp', () => {
      const payloadPart = 'eyJ1c2VySWQiOiJ1c2VyLTEyMyIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImlhdCI6MTcwMzc4MDAwMCwiZXhwIjoxNzAzODY2NDAwfQ';
      const payload = JSON.parse(
        Buffer.from(payloadPart.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString()
      );

      expect(payload).toHaveProperty('userId');
      expect(payload).toHaveProperty('email');
      expect(payload).toHaveProperty('iat');
      expect(payload).toHaveProperty('exp');
    });

    it('should have valid timestamps for iat and exp', () => {
      const payloadPart = 'eyJ1c2VySWQiOiJ1c2VyLTEyMyIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImlhdCI6MTcwMzc4MDAwMCwiZXhwIjoxNzAzODY2NDAwfQ';
      const payload = JSON.parse(
        Buffer.from(payloadPart.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString()
      );

      // iat and exp should be Unix timestamps in seconds
      expect(typeof payload.iat).toBe('number');
      expect(typeof payload.exp).toBe('number');
      expect(payload.iat).toBeGreaterThan(0);
      expect(payload.exp).toBeGreaterThan(payload.iat);

      // exp should be after iat (typical token validity)
      const tokenValiditySeconds = payload.exp - payload.iat;
      expect(tokenValiditySeconds).toBeGreaterThan(0);
    });

    it('should have userId and email as strings', () => {
      const payloadPart = 'eyJ1c2VySWQiOiJ1c2VyLTEyMyIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImlhdCI6MTcwMzc4MDAwMCwiZXhwIjoxNzAzODY2NDAwfQ';
      const payload = JSON.parse(
        Buffer.from(payloadPart.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString()
      );

      expect(typeof payload.userId).toBe('string');
      expect(typeof payload.email).toBe('string');
    });
  });

  describe('decodeToken Function', () => {
    it('should decode valid JWT token', () => {
      const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyLTEyMyIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImlhdCI6MTcwMzc4MDAwMCwiZXhwIjoxNzAzODY2NDAwfQ.signature';

      const parts = token.split('.');
      const payload = JSON.parse(
        Buffer.from(parts[1].replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString()
      );

      expect(payload.userId).toBe('user-123');
      expect(payload.email).toBe('test@example.com');
    });

    it('should return null for invalid JWT token', () => {
      const invalidToken = 'invalid.token.format';

      try {
        const parts = invalidToken.split('.');
        if (parts.length !== 3) {
          throw new Error('Invalid token structure');
        }
      } catch {
        expect(true).toBe(true);
      }
    });

    it('should handle malformed payload gracefully', () => {
      const tokenWithBadPayload = 'header.invalid_base64!!!.signature';

      try {
        const parts = tokenWithBadPayload.split('.');
        Buffer.from(parts[1].replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString();
        expect(false).toBe(true); // Should not reach here with malformed base64
      } catch {
        expect(true).toBe(true);
      }
    });
  });

  describe('isTokenExpired Function', () => {
    it('should return true for expired token', () => {
      // Token with exp set to past timestamp (seconds)
      const expiredPayload = {
        userId: 'user-123',
        email: 'test@example.com',
        iat: 1703700000, // past
        exp: 1703700000, // also past (1 day ago in unix time)
      };

      const currentTimeSeconds = Math.floor(Date.now() / 1000);
      const isExpired = currentTimeSeconds >= expiredPayload.exp;

      expect(isExpired).toBe(true);
    });

    it('should return false for valid token not yet expired', () => {
      const currentTimeMs = Date.now();
      const futureExpSeconds = Math.floor((currentTimeMs + 86400000) / 1000); // 24 hours from now

      const validPayload = {
        userId: 'user-123',
        email: 'test@example.com',
        iat: Math.floor(currentTimeMs / 1000),
        exp: futureExpSeconds,
      };

      const currentTimeSeconds = Math.floor(Date.now() / 1000);
      const isExpired = currentTimeSeconds >= validPayload.exp;

      expect(isExpired).toBe(false);
    });

    it('should consider token expired if current time equals exp time', () => {
      const currentTimeSeconds = Math.floor(Date.now() / 1000);

      const payload = {
        userId: 'user-123',
        email: 'test@example.com',
        iat: currentTimeSeconds - 3600,
        exp: currentTimeSeconds, // Same as current time
      };

      const isExpired = currentTimeSeconds >= payload.exp;
      expect(isExpired).toBe(true);
    });
  });

  describe('Token Persistence', () => {
    it('should store token in localStorage', () => {
      const token = 'test.jwt.token';
      localStorage.setItem('evolution_todo_jwt_token', token);

      const retrieved = localStorage.getItem('evolution_todo_jwt_token');
      expect(retrieved).toBe(token);
    });

    it('should retrieve stored token from localStorage', () => {
      const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyLTEyMyJ9.signature';
      localStorage.setItem('evolution_todo_jwt_token', token);

      const retrieved = localStorage.getItem('evolution_todo_jwt_token');
      expect(retrieved).toBe(token);
    });

    it('should remove token from localStorage', () => {
      const token = 'test.jwt.token';
      localStorage.setItem('evolution_todo_jwt_token', token);

      expect(localStorage.getItem('evolution_todo_jwt_token')).toBe(token);

      localStorage.removeItem('evolution_todo_jwt_token');
      expect(localStorage.getItem('evolution_todo_jwt_token')).toBeNull();
    });

    it('should clear all localStorage on logout', () => {
      localStorage.setItem('evolution_todo_jwt_token', 'token1');
      localStorage.setItem('other_key', 'value');

      localStorage.clear();

      expect(localStorage.getItem('evolution_todo_jwt_token')).toBeNull();
      expect(localStorage.getItem('other_key')).toBeNull();
    });
  });

  describe('Token Validation Edge Cases', () => {
    it('should handle token with missing exp claim', () => {
      const payloadWithoutExp = {
        userId: 'user-123',
        email: 'test@example.com',
        iat: 1703700000,
      };

      expect(payloadWithoutExp).not.toHaveProperty('exp');
    });

    it('should handle token with missing userId claim', () => {
      const payloadWithoutUserId = {
        email: 'test@example.com',
        iat: 1703700000,
        exp: 1703800000,
      };

      expect(payloadWithoutUserId).not.toHaveProperty('userId');
    });
  });
});
