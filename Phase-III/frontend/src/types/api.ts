// [Task]: T-010, [From]: specs/002-task-ui-frontend/spec.md#API-Integration-Contracts
// Generic API-related TypeScript type definitions

export interface ApiResponse<T> {
  data: T;
  error: null;
}

export interface ApiErrorResponse<E = unknown> {
  data: null;
  error: {
    code: string;
    message: string;
    details?: E;
  };
}

export type ApiResult<T, E = unknown> = ApiResponse<T> | ApiErrorResponse<E>;

export interface HttpRequestConfig {
  headers?: Record<string, string>;
  params?: Record<string, unknown>;
  data?: unknown;
  timeout?: number;
  withAuth?: boolean;
}

export interface HttpResponse<T> {
  status: number;
  statusText: string;
  headers: Record<string, string>;
  data: T;
}

export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export class ApiError extends Error {
  code: string;
  status: number;
  details?: unknown;

  constructor(message: string, code: string, status: number, details?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

export enum ApiErrorCode {
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT = 'TIMEOUT',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
}
