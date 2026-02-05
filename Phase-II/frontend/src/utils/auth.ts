// [Task]: T013, [From]: specs/002-task-ui-frontend/spec.md#FR-003
// JWT Token Persistence Utilities - Secure token management and validation

import type { JWTPayload } from '@/types/auth';

const JWT_TOKEN_KEY = 'evolution_todo_jwt_token';

/**
 * Saves JWT token to localStorage
 * [Task]: T013, [From]: specs/002-task-ui-frontend/spec.md#FR-003
 *
 * @param token - JWT token string to persist
 * @throws Error if window is undefined (SSR context)
 */
export function saveToken(token: string): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    localStorage.setItem(JWT_TOKEN_KEY, token);
  } catch (error) {
    // Handle localStorage quota exceeded or other storage errors
    console.error('Failed to save JWT token to localStorage:', error);
  }
}

/**
 * Retrieves JWT token from localStorage
 * [Task]: T013, [From]: specs/002-task-ui-frontend/spec.md#FR-003
 *
 * @returns JWT token string or null if not found/invalid
 */
export function getToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const token = localStorage.getItem(JWT_TOKEN_KEY);
    return token;
  } catch (error) {
    console.error('Failed to retrieve JWT token from localStorage:', error);
    return null;
  }
}

/**
 * Removes JWT token from localStorage (used on logout)
 * [Task]: T013, [From]: specs/002-task-ui-frontend/spec.md#FR-011
 */
export function removeToken(): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    localStorage.removeItem(JWT_TOKEN_KEY);
  } catch (error) {
    console.error('Failed to remove JWT token from localStorage:', error);
  }
}

/**
 * Decodes JWT token without verification (for client-side expiration check)
 * WARNING: This decodes the token but does NOT verify the signature.
 * Server must always validate token signature and claims.
 * [Task]: T013, [From]: specs/002-task-ui-frontend/spec.md#FR-003
 *
 * @param token - JWT token string
 * @returns Decoded JWT payload or null if invalid
 */
export function decodeToken(token: string): JWTPayload | null {
  try {
    // JWT format: header.payload.signature
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    // Decode the payload (second part)
    const payload = parts[1];

    // Browser-compatible base64 decoding
    const base64url = payload;
    const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');

    // Add padding if needed
    const padding = '='.repeat((4 - (base64.length % 4)) % 4);
    const base64Padded = base64 + padding;

    // Decode using atob (browser API)
    const decodedStr = atob(base64Padded);

    // Convert to JSON
    const decodedPayload = JSON.parse(decodedStr);

    console.log('Decoded token:', decodedPayload);
    return decodedPayload as JWTPayload;
  } catch (error) {
    console.error('Failed to decode JWT token:', error);
    return null;
  }
}

/**
 * Checks if JWT token is expired
 * [Task]: T013, [From]: specs/002-task-ui-frontend/spec.md#FR-003
 *
 * @param token - JWT token string
 * @returns true if token is expired, false if valid or cannot be decoded
 */
export function isTokenExpired(token: string): boolean {
  const payload = decodeToken(token);

  if (!payload || !payload.exp) {
    // If we can't decode or no exp claim, consider it expired for safety
    return true;
  }

  // exp is in seconds since epoch, Date.now() is in milliseconds
  const expirationTime = payload.exp * 1000;
  const currentTime = Date.now();

  // Token is expired if current time >= expiration time
  return currentTime >= expirationTime;
}

/**
 * Validates token presence and expiration
 * [Task]: T013, [From]: specs/002-task-ui-frontend/spec.md#FR-003
 *
 * @returns true if valid token exists and is not expired
 */
export function isTokenValid(): boolean {
  const token = getToken();

  if (!token) {
    return false;
  }

  return !isTokenExpired(token);
}
