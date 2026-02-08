---
name: "backend-api"
description: "Generate backend APIs with routes, request/response handling, database connections, and middleware. Use when the user asks to build APIs, create endpoints, or handle server-side logic."
version: "1.0.0"
---

# Backend API Skill

## When to Use This Skill

- When the user asks to "create an API" or "build backend routes"
- When the user mentions endpoints, REST APIs, GraphQL, or server logic
- When the user needs database integration, authentication, or middleware
- When the user wants to handle HTTP requests/responses
- When the user mentions Express, FastAPI, Node.js, or backend frameworks

## Procedure

1. **Understand requirements**: Clarify framework choice, database type, and authentication needs
2. **Design API structure**: Define routes, HTTP methods, and response formats
3. **Set up database connection**: Configure connection pooling and error handling
4. **Implement routes**: Create endpoints with proper validation and error handling
5. **Add middleware**: Include authentication, logging, CORS, and rate limiting as needed
6. **Test considerations**: Mention how to test endpoints and common edge cases

## Output Format

**Tech Stack**: Framework, database, and key libraries  
**Database Schema**: Tables/collections with fields and relationships  
**API Routes**: Method, path, description, and auth requirements  
**Code Structure**: Organized by feature/resource with clear separation  
**Environment Variables**: Required configuration (with examples, no real values)

## Quality Criteria

- **RESTful design**: Use proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
- **Error handling**: Return consistent error responses with appropriate status codes
- **Validation**: Validate input data before processing
- **Security**: Sanitize inputs, use parameterized queries, implement rate limiting
- **Database efficiency**: Use connection pooling, indexes, and avoid N+1 queries
- **Code organization**: Group by resource/feature, not by technical layer
- **Documentation**: Include clear comments for complex logic

## Best Practices

### Do's
✅ Use environment variables for sensitive configuration  
✅ Implement proper error handling and logging  
✅ Validate and sanitize all user inputs  
✅ Use parameterized queries to prevent SQL injection  
✅ Return consistent JSON response structures  
✅ Include appropriate HTTP status codes  
✅ Set up CORS properly for cross-origin requests  
✅ Use middleware for cross-cutting concerns (auth, logging)  

### Don'ts
❌ Don't commit API keys or database credentials  
❌ Don't return raw error messages to clients  
❌ Don't skip input validation  
❌ Don't use string concatenation for SQL queries  
❌ Don't expose internal implementation details in responses  
❌ Don't forget to close database connections  
❌ Don't ignore rate limiting for public APIs  

## Common Patterns

### REST API Response Structure
```json
{
  "success": true,
  "data": { /* payload */ },
  "message": "Operation successful",
  "timestamp": "2026-01-18T10:30:00Z"
}
```

### Error Response Structure
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": ["Email is required", "Password must be 8+ characters"]
  },
  "timestamp": "2026-01-18T10:30:00Z"
}
```

### HTTP Status Codes
- **200 OK**: Successful GET, PUT, PATCH
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid input
- **401 Unauthorized**: Missing/invalid authentication
- **403 Forbidden**: Valid auth but insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Resource conflict (duplicate)
- **422 Unprocessable Entity**: Validation failed
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

## Example

**Input**: "Create a REST API for a task management system with user authentication"

**Output**:

### Tech Stack
- **Framework**: Express.js (Node.js)
- **Database**: PostgreSQL with Prisma ORM
- **Authentication**: JWT tokens
- **Key Libraries**: bcrypt, express-validator, helmet, cors

### Database Schema
```sql
Users
- id (UUID, primary key)
- email (string, unique)
- password_hash (string)
- name (string)
- created_at (timestamp)

Tasks
- id (UUID, primary key)
- user_id (UUID, foreign key → Users)
- title (string)
- description (text)
- status (enum: pending, in_progress, completed)
- priority (enum: low, medium, high)
- due_date (date, nullable)
- created_at (timestamp)
- updated_at (timestamp)
```

### API Routes

**Authentication**
- `POST /api/auth/register` - Create new user account
- `POST /api/auth/login` - Authenticate and get JWT token
- `POST /api/auth/logout` - Invalidate token (if using refresh tokens)

**Tasks** (all require authentication)
- `GET /api/tasks` - List all tasks for authenticated user
  - Query params: status, priority, sort, limit, offset
- `GET /api/tasks/:id` - Get single task details
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/:id` - Update entire task
- `PATCH /api/tasks/:id` - Partial update (e.g., mark as completed)
- `DELETE /api/tasks/:id` - Delete task

### Code Structure
```
src/
├── config/
│   ├── database.js       # DB connection setup
│   └── env.js            # Environment variables
├── middleware/
│   ├── auth.js           # JWT verification
│   ├── errorHandler.js   # Global error handler
│   └── validators.js     # Input validation
├── routes/
│   ├── auth.routes.js    # Authentication endpoints
│   └── tasks.routes.js   # Task management endpoints
├── controllers/
│   ├── auth.controller.js
│   └── tasks.controller.js
├── models/
│   └── index.js          # Prisma client
├── utils/
│   ├── jwt.js            # Token generation/validation
│   └── password.js       # Hashing utilities
└── app.js                # Express app setup
```

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/taskdb

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRES_IN=7d

# Server
PORT=3000
NODE_ENV=development

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Key Implementation Notes

**Authentication Middleware**:
```javascript
// Verify JWT token on protected routes
const authMiddleware = async (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token provided' });
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.userId = decoded.userId;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};
```

**Input Validation Example**:
```javascript
// Use express-validator for task creation
const validateTask = [
  body('title').trim().notEmpty().withMessage('Title is required'),
  body('status').isIn(['pending', 'in_progress', 'completed']),
  body('priority').isIn(['low', 'medium', 'high']),
  body('due_date').optional().isISO8601()
];
```

**Database Query with Pagination**:
```javascript
// Get tasks with filtering and pagination
const tasks = await prisma.task.findMany({
  where: {
    user_id: req.userId,
    status: req.query.status, // optional filter
  },
  orderBy: { created_at: 'desc' },
  skip: parseInt(req.query.offset) || 0,
  take: parseInt(req.query.limit) || 20,
});
```

### Testing Considerations
- Test authentication (valid/invalid/expired tokens)
- Test validation (missing fields, invalid formats)
- Test authorization (users can't access others' tasks)
- Test pagination and filtering
- Test error cases (database errors, duplicate entries)

## Framework-Specific Variations

### Node.js/Express
- Use `express-validator` for input validation
- Implement async error handling with try-catch or express-async-errors
- Use `helmet` for security headers
- Consider `morgan` for request logging

### Python/FastAPI
- Use Pydantic models for automatic validation
- Leverage dependency injection for database sessions
- Use async endpoints with `async def` when possible
- Implement custom exception handlers

### Go/Gin or Fiber
- Use struct tags for JSON binding and validation
- Implement middleware chains for auth and logging
- Use goroutines carefully with database connections
- Consider using `sqlx` or `GORM` for database operations

### Ruby/Rails or Sinatra
- Use strong parameters for input filtering
- Implement ActiveRecord validations
- Use `rack-cors` for CORS handling
- Consider `jwt` gem for authentication

## Security Checklist

- [ ] Password hashing with bcrypt/argon2
- [ ] JWT secrets stored in environment variables
- [ ] Input validation on all endpoints
- [ ] Parameterized database queries
- [ ] CORS configured properly
- [ ] Rate limiting implemented
- [ ] Helmet or security headers set
- [ ] HTTPS enforced in production
- [ ] SQL injection prevention
- [ ] XSS protection

## Performance Optimization

- Use connection pooling for database
- Implement caching (Redis) for frequently accessed data
- Add database indexes on commonly queried fields
- Use pagination for large datasets
- Consider implementing background jobs for heavy tasks
- Monitor and optimize slow queries
- Use compression middleware (gzip)

---

**Notes**: Always adapt the tech stack and patterns to the user's specific requirements. When in doubt, ask clarifying questions about framework preference, database choice, and authentication needs.