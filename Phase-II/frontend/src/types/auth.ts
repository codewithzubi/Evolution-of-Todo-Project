// [Task]: T-010, [From]: specs/002-task-ui-frontend/spec.md#Key-Entities
// Authentication-related TypeScript type definitions

export interface User {
  id: string;
  email: string;
  name?: string;
  createdAt: string;
}

export interface AuthResponse {
  data: {
    user: User;
    token: string;
  };
  error: null;
}

export interface AuthError {
  data: null;
  error: {
    code: string;
    message: string;
  };
}

export interface SignupRequest {
  email: string;
  password: string;
  name?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

export interface JWTPayload {
  userId?: string;
  user_id?: string;
  email: string;
  iat: number;
  exp: number;
}
