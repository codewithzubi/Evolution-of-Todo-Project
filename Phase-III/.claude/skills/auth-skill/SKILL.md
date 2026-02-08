---
name: "auth-skill"
description: "Implement secure authentication flows including signup, sign-in, password hashing, JWT tokens, and Better Auth integration. Use when the user needs to add authentication, secure endpoints, or handle user sessions."
version: "1.0.0"
---

# Auth Skill

## When to Use This Skill

- When the user asks to "add authentication" or "implement login"
- When the user mentions signup, sign-in, JWT, or session management
- When the user needs to integrate Better Auth or any auth provider
- When the user asks about password security or hashing
- When the user needs to protect routes or API endpoints
- When the user mentions "secure my app" or authentication bugs

## Procedure

1. **Understand the requirements**: Clarify auth method (email/password, OAuth, magic links), existing stack, and security needs
2. **Choose auth strategy**: Better Auth for modern apps, or manual JWT implementation for custom needs
3. **Implement secure storage**: Password hashing (bcrypt/argon2), token storage (httpOnly cookies preferred)
4. **Set up authentication flow**: Signup → email verification → login → session/token management
5. **Protect resources**: Add middleware for route protection and role-based access
6. **Handle edge cases**: Token refresh, logout, password reset, expired sessions

## Output Format

**Authentication Strategy**: Brief explanation of chosen approach (Better Auth vs custom JWT)  
**Security Measures**: List of implemented security features (hashing algorithm, token storage, CSRF protection)  
**Code Structure**: Organized by concern (auth routes, middleware, utilities, config)  
**Integration Points**: Where auth connects to the rest of the app (protected routes, user context, API calls)  
**Testing Notes**: Key scenarios to test (invalid credentials, expired tokens, role permissions)

## Quality Criteria

- **Never store plain passwords**: Always use bcrypt (10+ rounds) or argon2
- **Secure token storage**: httpOnly cookies for web, secure storage for mobile (never localStorage for sensitive tokens)
- **Proper validation**: Validate all inputs, sanitize emails, enforce password requirements
- **Clear error messages**: Informative but don't leak security info ("Invalid credentials" not "Password incorrect")
- **Rate limiting**: Prevent brute force attacks on auth endpoints
- **HTTPS only**: Secure flag on cookies, warn if not using HTTPS in production
- **Token expiration**: Access tokens (15-30 min), refresh tokens (7-30 days)
- **CORS configuration**: Strict origin allowlisting for auth endpoints

## Implementation Patterns

### Better Auth Integration (Recommended)
```typescript
// auth.ts - Better Auth configuration
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  database: prisma, // or drizzle
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24 // update every 24 hours
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET
    }
  }
})
```

### JWT Manual Implementation
```typescript
// utils/jwt.ts
import bcrypt from 'bcrypt'
import jwt from 'jsonwebtoken'

export async function hashPassword(password: string) {
  return bcrypt.hash(password, 12) // 12 rounds minimum
}

export async function verifyPassword(password: string, hash: string) {
  return bcrypt.compare(password, hash)
}

export function generateTokens(userId: string) {
  const accessToken = jwt.sign(
    { userId, type: 'access' },
    process.env.JWT_SECRET!,
    { expiresIn: '15m' }
  )
  
  const refreshToken = jwt.sign(
    { userId, type: 'refresh' },
    process.env.JWT_REFRESH_SECRET!,
    { expiresIn: '7d' }
  )
  
  return { accessToken, refreshToken }
}
```

### Protected Route Middleware
```typescript
// middleware/auth.ts
export async function requireAuth(req, res, next) {
  try {
    const token = req.cookies.accessToken // httpOnly cookie
    
    if (!token) {
      return res.status(401).json({ error: 'Authentication required' })
    }
    
    const payload = jwt.verify(token, process.env.JWT_SECRET!)
    req.user = await db.user.findUnique({ where: { id: payload.userId } })
    
    next()
  } catch (error) {
    return res.status(401).json({ error: 'Invalid or expired token' })
  }
}
```

## Common Pitfalls to Avoid

- ❌ Storing tokens in localStorage (XSS vulnerable)
- ❌ Using weak password hashing (MD5, SHA1, or bcrypt < 10 rounds)
- ❌ Not implementing rate limiting on auth endpoints
- ❌ Revealing whether email exists during login ("User not found" vs "Invalid credentials")
- ❌ Not validating email format and password strength
- ❌ Forgetting to handle token refresh logic
- ❌ Not clearing tokens/sessions on logout
- ❌ Missing CORS configuration for auth endpoints

## Example

**Input**: "I need to add authentication to my Next.js app with email/password and Google login"

**Output**:

**Authentication Strategy**: Better Auth with email/password + Google OAuth, session-based with httpOnly cookies

**Security Measures**:
- Password hashing: bcrypt with 12 rounds
- Token storage: httpOnly, secure, sameSite=strict cookies
- Email verification required before first login
- Rate limiting: 5 attempts per 15 minutes per IP
- CSRF protection enabled

**Code Structure**:
```
/lib/auth.ts           # Better Auth configuration
/app/api/auth/[...all] # Better Auth API routes
/middleware.ts         # Route protection middleware
/lib/auth-client.ts    # Client-side auth utilities
```

**Integration Points**:
- Protected routes use middleware.ts matcher config
- User session available via `useSession()` hook
- API routes check auth via `auth.api.getSession()`
- Profile data fetched after successful authentication

**Testing Notes**:
- Test invalid credentials return generic error
- Verify email verification flow works
- Check token refresh before expiration
- Confirm protected routes redirect correctly
- Test Google OAuth callback handling
- Verify logout clears all session data

**Next Steps**:
1. Install Better Auth: `npm install better-auth`
2. Set up database schema with Better Auth models
3. Configure environment variables (secrets, callback URLs)
4. Implement auth routes and middleware
5. Add client-side session management
6. Test all flows in development before deploying

## Security Checklist

Before deploying authentication:
- [ ] All passwords hashed with bcrypt (12+ rounds) or argon2
- [ ] Tokens stored in httpOnly cookies (or secure mobile storage)
- [ ] Email validation on signup
- [ ] Password strength requirements enforced
- [ ] Rate limiting on login/signup endpoints
- [ ] HTTPS enforced in production (secure cookie flag)
- [ ] CORS properly configured
- [ ] Token expiration times set appropriately
- [ ] Logout clears all session data
- [ ] Error messages don't leak security info
- [ ] Email verification flow working
- [ ] Password reset flow secure (time-limited tokens)
- [ ] SQL injection prevention (use ORMs/prepared statements)
- [ ] XSS prevention (sanitize inputs, CSP headers)

## Resources

- Better Auth Documentation: https://better-auth.com
- OWASP Authentication Cheat Sheet
- JWT Best Practices: https://jwt.io/introduction
- Password Hashing Guidelines: bcrypt 12+ rounds, argon2id preferred