// [Task]: T047, [From]: specs/002-task-ui-frontend/spec.md#US2
// TanStack Query configuration and setup with React Query

import { QueryClient } from '@tanstack/react-query';

/**
 * Create and configure QueryClient instance
 * [Task]: T047, [From]: specs/002-task-ui-frontend/spec.md#US2
 *
 * Configuration:
 * - staleTime: 1 minute (data becomes stale after 1 minute of not being used)
 * - gcTime: 5 minutes (garbage collection time, previously known as cacheTime)
 * - retry: 3 retries on failed requests
 * - retryDelay: exponential backoff starting at 1000ms
 */
export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60, // 1 minute
        gcTime: 1000 * 60 * 5, // 5 minutes
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      },
      mutations: {
        retry: 1,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      },
    },
  });
}

/**
 * Singleton instance of QueryClient
 * [Task]: T047, [From]: specs/002-task-ui-frontend/spec.md#US2
 */
export const queryClient = createQueryClient();

export type { QueryClient };
