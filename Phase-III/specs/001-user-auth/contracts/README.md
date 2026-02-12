# API Contracts: Authentication

**Feature**: 001-user-auth
**Date**: 2026-02-09

## Overview

This directory contains API contract specifications for the authentication system. All endpoints follow RESTful conventions and return JSON responses.

## Files

- **auth.openapi.yaml**: OpenAPI 3.1 specification for authentication endpoints

## Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user account | No |
| POST | `/api/auth/login` | Login with email/password | No |
| POST | `/api/auth/logout` | Logout current user | Yes |
| GET | `/api/auth/me` | Get current user info | Yes |
| POST | `/api/auth/refresh` | Refresh JWT token | Yes |

## Authentication

All authenticated endpoints require a JWT token stored in an httpOnly cookie named `token`.

**Cookie Attributes**:
- HttpOnly: true (prevents XSS)
- Secure: true (HTTPS only in production)
- SameSite: Lax (prevents CSRF)
- Max-Age: 604800 (7 days)

## Request/Response Examples

### Register User

**Request**:
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** (201 Created):
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-02-09T12:00:00Z"
  },
  "message": "Registration successful"
}
```

### Login

**Request**:
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** (200 OK):
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-02-09T12:00:00Z"
  },
  "message": "Login successful"
}
```

**Headers**:
```
Set-Cookie: token=eyJhbGc...; HttpOnly; Secure; SameSite=Lax; Max-Age=604800
```

### Get Current User

**Request**:
```bash
GET /api/auth/me
Cookie: token=eyJhbGc...
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-02-09T12:00:00Z"
}
```

### Logout

**Request**:
```bash
POST /api/auth/logout
Cookie: token=eyJhbGc...
```

**Response** (200 OK):
```json
{
  "message": "Logout successful"
}
```

**Headers**:
```
Set-Cookie: token=; HttpOnly; Secure; SameSite=Lax; Max-Age=0
```

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "Error type or title",
  "details": "Detailed error message"
}
```

### Common Error Codes

| Status | Error | Description |
|--------|-------|-------------|
| 400 | Invalid email format | Email validation failed |
| 400 | Password too short | Password < 8 characters |
| 401 | Invalid email or password | Login credentials incorrect |
| 401 | Not authenticated | JWT token missing or invalid |
| 409 | Email already registered | Duplicate email on registration |
| 429 | Too many requests | Rate limit exceeded (5/15min) |

## Rate Limiting

Authentication endpoints are rate-limited to prevent brute force attacks:

- **Limit**: 5 requests per 15 minutes per IP address
- **Applies to**: `/api/auth/register`, `/api/auth/login`
- **Response**: 429 Too Many Requests

## Validation Rules

### Email
- Format: Valid email address (RFC 5322)
- Max length: 255 characters
- Case-insensitive (normalized to lowercase)

### Password
- Min length: 8 characters
- Max length: 255 characters (before hashing)
- No complexity requirements

## Security Considerations

- Passwords are hashed with bcrypt (12 rounds) before storage
- JWT tokens are signed with HS256 algorithm
- Tokens expire after 7 days
- httpOnly cookies prevent XSS attacks
- SameSite=Lax prevents CSRF attacks
- Rate limiting prevents brute force attacks
- Error messages don't reveal whether email exists

## Testing

### Import into API Client

**Postman**:
1. Import → Link → Paste OpenAPI spec URL
2. Or: Import → File → Select `auth.openapi.yaml`

**Insomnia**:
1. Create → Import From → File
2. Select `auth.openapi.yaml`

**Swagger UI**:
- Available at http://localhost:8000/docs when backend is running

### cURL Examples

See `quickstart.md` for complete cURL examples.

## Implementation Status

- ✅ OpenAPI specification complete
- ⏭️ Backend implementation (next phase)
- ⏭️ Frontend integration (next phase)
- ⏭️ E2E tests (next phase)

## References

- OpenAPI Specification: https://spec.openapis.org/oas/v3.1.0
- FastAPI OpenAPI: https://fastapi.tiangolo.com/tutorial/metadata/
- JWT Best Practices: https://jwt.io/introduction
