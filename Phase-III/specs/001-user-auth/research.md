# Research: User Authentication System

**Feature**: 001-user-auth
**Date**: 2026-02-09
**Purpose**: Document architectural decisions, technology choices, and implementation patterns for authentication system

## Overview

This document captures research findings and architectural decisions for implementing a secure, multi-user authentication system using Better Auth 1.4.18, FastAPI 0.128.5, and JWT tokens.

## Key Architectural Decisions

### 1. Authentication Library: Better Auth 1.4.18

**Decision**: Use Better Auth for frontend authentication management

**Rationale**:
- Constitution requirement (locked tech stack)
- Built-in JWT token management
- Seamless Next.js App Router integration
- Supports multiple auth providers (email/password + OAuth)
- TypeScript-first with excellent type safety
- Handles token refresh automatically

**Alternatives Considered**:
- NextAuth.js: More mature but not specified in constitution
- Custom JWT implementation: More control but higher complexity and security risk
- Auth0/Clerk: Third-party services add external dependencies

**Implementation Pattern**:
```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  database: {
    provider: "postgresql",
    url: process.env.DATABASE_URL
  },
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET
    }
  }
})
```

**References**:
- Better Auth Docs: https://better-auth.com/docs
- Next.js App Router Integration: https://better-auth.com/docs/integrations/nextjs

---

### 2. JWT Token Management Strategy

**Decision**: Use stateless JWT tokens with client-side secure storage (Better Auth managed) and 7-day expiration

**Rationale**:
- Stateless architecture eliminates need for session storage or httpOnly cookies
- Better Auth handles secure token storage automatically (encrypted localStorage)
- 7-day expiration balances security and user convenience
- Scalable: no server-side session state
- Simple: backend only verifies JWT signature and extracts user_id

**Alternatives Considered**:
- httpOnly cookies: Requires session management, violates stateless requirement (rejected)
- Plain localStorage: Vulnerable to XSS, Better Auth encrypts tokens (mitigated)
- sessionStorage: Lost on tab close, poor UX (rejected)
- Short-lived tokens (1 hour): Requires frequent re-authentication (rejected for hackathon UX)

**Token Structure**:
```json
{
  "user_id": "uuid-string",
  "email": "user@example.com",
  "iat": 1707552000,
  "exp": 1708156800
}
```

**Security Considerations**:
- Token signing algorithm: HS256 (HMAC with SHA-256)
- Secret key: BETTER_AUTH_SECRET (shared between frontend and backend)
- Token validation on every backend request
- Better Auth encrypts tokens in localStorage
- Blacklist not needed (7-day expiration + logout clears client storage)

**References**:
- OWASP JWT Security: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- httpOnly Cookie Best Practices: https://owasp.org/www-community/HttpOnly

---

### 3. Password Hashing: bcrypt with 12 rounds

**Decision**: Use passlib with bcrypt algorithm, 12 cost factor

**Rationale**:
- bcrypt is industry standard for password hashing
- Adaptive algorithm (cost factor increases with hardware improvements)
- 12 rounds provides strong security without excessive latency (~250ms)
- passlib provides clean Python API with automatic salt generation

**Alternatives Considered**:
- Argon2: More modern but not in constitution dependencies (rejected)
- PBKDF2: Weaker against GPU attacks (rejected)
- scrypt: Good but bcrypt more widely adopted (rejected)

**Implementation Pattern**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Performance Impact**:
- Hashing: ~250ms per password (acceptable for registration/login)
- Verification: ~250ms per attempt (acceptable for login)
- No impact on authenticated requests (JWT validation is fast)

**References**:
- passlib Documentation: https://passlib.readthedocs.io/
- bcrypt Cost Factor Analysis: https://security.stackexchange.com/questions/17207/recommended-of-rounds-for-bcrypt

---

### 4. Rate Limiting: Token Bucket Algorithm

**Decision**: Implement rate limiting with 5 attempts per 15 minutes per IP

**Rationale**:
- Prevents brute force attacks on login endpoint
- Token bucket algorithm allows burst traffic while limiting sustained abuse
- IP-based tracking (simple, effective for hackathon scale)
- 5 attempts allows legitimate typos while blocking automated attacks

**Alternatives Considered**:
- Account lockout: Enables denial-of-service attacks (rejected)
- CAPTCHA: Poor UX, not in scope (rejected)
- No rate limiting: Security vulnerability (rejected)

**Implementation Pattern**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/15minutes")
async def login(credentials: LoginRequest):
    # Login logic
    pass
```

**Edge Cases**:
- Shared IP (corporate NAT): May affect legitimate users, acceptable for hackathon
- VPN/proxy: Rate limit still applies per IP
- Distributed attacks: Out of scope for Phase II

**References**:
- slowapi (FastAPI rate limiting): https://github.com/laurentS/slowapi
- Token Bucket Algorithm: https://en.wikipedia.org/wiki/Token_bucket

---

### 5. Session Management: Stateless JWT with Client-Side Storage

**Decision**: Stateless JWT tokens (no server-side session storage, no sessions table)

**Rationale**:
- Scalability: No session database required
- Simplicity: Reduces infrastructure complexity
- Performance: No database lookup on every request
- Constitution alignment: Matches stateless JWT-based architecture
- Better Auth handles client-side storage securely

**Alternatives Considered**:
- Server-side sessions (Redis): Adds infrastructure complexity (rejected)
- Database sessions table: Adds latency to every request, violates stateless requirement (rejected)
- Hybrid (JWT + session table): Over-engineered for hackathon (rejected)

**Logout Strategy**:
- Clear JWT token from client-side storage on logout
- No token blacklist (7-day expiration is acceptable risk)
- User cannot revoke tokens from other devices (acceptable for Phase II)

**Session Persistence**:
- Token persists in client storage across browser restarts (7-day expiration)
- User remains logged in until explicit logout or token expiry
- No "remember me" checkbox (always remember for 7 days)

**References**:
- Stateless JWT Best Practices: https://jwt.io/introduction
- Session Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html

---

### 6. Google OAuth Integration: Better Auth Social Provider

**Decision**: Use Better Auth's built-in Google OAuth provider

**Rationale**:
- Better Auth handles OAuth flow automatically
- Reduces custom code and security risks
- Seamless integration with email/password auth
- Automatic account linking by email

**OAuth Flow**:
1. User clicks "Sign in with Google"
2. Better Auth redirects to Google OAuth consent screen
3. User authorizes application
4. Google redirects back with authorization code
5. Better Auth exchanges code for tokens
6. Better Auth creates/retrieves user account
7. Better Auth issues JWT token
8. User redirected to dashboard

**Account Linking Strategy**:
- If email exists (email/password account): Link to existing account
- If email new: Create new account with OAuth provider
- User can use both email/password and Google OAuth interchangeably

**Security Considerations**:
- OAuth state parameter prevents CSRF
- PKCE (Proof Key for Code Exchange) for additional security
- Google Client ID/Secret stored in environment variables
- Redirect URI whitelist configured in Google Console

**References**:
- Better Auth Social Providers: https://better-auth.com/docs/social-providers
- Google OAuth 2.0: https://developers.google.com/identity/protocols/oauth2

---

### 7. CORS Configuration: Frontend Origin Only

**Decision**: Restrict CORS to frontend origin (http://localhost:3000 in dev, production domain in prod)

**Rationale**:
- Prevents unauthorized domains from calling backend API
- Constitution requirement for security
- Simple configuration with FastAPI CORSMiddleware

**Implementation Pattern**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,  # Required for Authorization headers
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Development vs Production**:
- Development: http://localhost:3000
- Production: https://yourdomain.com (from environment variable)

**References**:
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/
- CORS Best Practices: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

---

### 8. Database Schema: Minimal User Table

**Decision**: Single `users` table with id, email, hashed_password, created_at

**Rationale**:
- Simplicity: No sessions table needed (stateless JWT)
- Better Auth manages its own tables if needed (we only need users for backend verification)
- SQLModel provides type-safe ORM with Pydantic validation
- UUID for id enables distributed systems

**Schema Design**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Indexes**:
- Primary key: `id` (UUID)
- Unique index: `email` (fast lookup, prevent duplicates)

**Migration Strategy**:
- Alembic for database migrations
- Initial migration creates users table
- No sessions table (stateless architecture)

**References**:
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- Alembic Tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html

---

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Frontend Auth | Better Auth | 1.4.18 | Authentication management |
| Backend Framework | FastAPI | 0.128.5 | API endpoints |
| ORM | SQLModel | 0.0.32 | Database models |
| Database | PostgreSQL | Latest (Neon) | User data storage |
| Password Hashing | passlib + bcrypt | Latest | Secure password storage |
| JWT Library | python-jose | Latest | Token generation/validation |
| Rate Limiting | slowapi | Latest | Brute force prevention |
| Testing (Backend) | pytest | Latest | Unit/integration tests |
| Testing (Frontend) | Vitest + Playwright | Latest | Unit/E2E tests |

## Security Checklist

- ✅ Passwords hashed with bcrypt (12 rounds)
- ✅ JWT tokens stored securely by Better Auth (encrypted localStorage)
- ✅ JWT signature verification using BETTER_AUTH_SECRET on every backend request
- ✅ CORS restricted to frontend origin
- ✅ Rate limiting on auth endpoints (5/15min)
- ✅ SQL injection prevention (SQLModel parameterized queries)
- ✅ Secrets in environment variables (never hardcoded)
- ✅ HTTPS in production
- ✅ Token expiration (7 days)
- ✅ Email validation (format checking)
- ✅ User isolation (all queries filtered by user_id from JWT)

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Registration | <60s | End-to-end user flow |
| Login | <30s | End-to-end user flow |
| Token validation | <50ms | Backend middleware |
| Password hashing | ~250ms | Acceptable for auth operations |
| Concurrent users | 100 | Load testing target |

## Open Questions

None - all technical decisions resolved based on constitution requirements and industry best practices.

## Next Steps

1. Create data-model.md (User entity schema)
2. Generate API contracts (OpenAPI spec for auth endpoints)
3. Create quickstart.md (local development setup)
4. Update agent context with authentication patterns
5. Generate tasks.md with /sp.tasks command
