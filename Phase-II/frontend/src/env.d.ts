// [Task]: T-007, [From]: specs/002-task-ui-frontend/spec.md#Environment
// Environment variable type definitions

namespace NodeJS {
  interface ProcessEnv {
    NEXT_PUBLIC_API_BASE_URL: string;
    NEXT_PUBLIC_JWT_SECRET: string;
    NEXT_PUBLIC_ENABLE_DEBUG_MODE?: string;
  }
}
