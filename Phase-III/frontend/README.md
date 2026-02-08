# Evolution of Todo - Frontend

A modern task management frontend built with Next.js 16+, React 19, TypeScript, and Tailwind CSS.

## Project Structure

```
frontend/
├── src/
│   ├── app/                  # Next.js App Router pages and layouts
│   ├── components/           # Reusable React components
│   ├── services/             # API client services
│   ├── hooks/                # Custom React hooks
│   ├── types/                # TypeScript type definitions
│   ├── utils/                # Utility functions
│   ├── middleware.ts         # Next.js middleware
│   ├── env.d.ts              # Environment variable types
│   └── globals.css           # Global Tailwind styles
├── tests/                    # Test files
├── public/                   # Static assets
├── package.json
├── tsconfig.json             # TypeScript configuration (strict mode)
├── tailwind.config.ts        # Tailwind CSS configuration
├── vitest.config.ts          # Vitest configuration
├── .eslintrc.json            # ESLint configuration
├── prettier.config.json      # Prettier configuration
└── .env.local                # Local environment variables
```

## Prerequisites

- Node.js 20+ (or via nvm)
- pnpm 8+ (or npm/yarn)

## Setup

### 1. Install Dependencies

```bash
cd frontend
pnpm install
```

### 2. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env.local

# Edit .env.local with your values
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
# NEXT_PUBLIC_JWT_SECRET=your_secret_key
```

## Development

### Start Development Server

```bash
pnpm dev
```

Visit `http://localhost:3000` in your browser.

### Code Quality

```bash
# Run ESLint (zero tolerance for violations)
pnpm lint

# Type checking
pnpm type-check

# Format code with Prettier
pnpm format
```

## Testing

```bash
# Run all tests
pnpm test

# Run tests with UI
pnpm test:ui

# Generate coverage report
pnpm test:coverage
```

## Building

### Production Build

```bash
pnpm build

# Start production server
pnpm start
```

## Features

### Phase 1: Authentication (P1)
- User signup and login with email/password
- JWT token management
- Protected routes and redirect logic
- Session persistence

### Phase 2: Task Management (P1)
- Task list with pagination (10 items per page)
- Create, read, update, delete tasks
- Mark tasks as complete/incomplete
- Task filtering and sorting

### Design
- Responsive design (mobile 375px, tablet 768px, desktop 1024px+)
- Tailwind CSS styling with custom theme
- Accessible components (ARIA labels, semantic HTML)
- Dark mode support (ready for Phase 2+)

## Architecture

### Component Hierarchy
```
RootLayout
├── AuthPages (login, signup)
├── TaskPages (list, detail)
└── Common Components (Button, Input, Card, etc.)
```

### State Management
- **Authentication**: React Context API
- **Task Data**: TanStack Query (React Query)
- **Form State**: React Hook Form

### API Integration
- Base API client with JWT token injection
- Automatic error handling and retries
- User data isolation via backend authentication

## Type Safety

This project uses **strict TypeScript mode** with:
- `strict: true` in tsconfig.json
- No `any` types allowed
- ESLint type checking enabled
- All API responses typed

## Performance

- Server components by default (Next.js 16+)
- Lazy loading for page components
- Image optimization with Next.js Image component
- CSS-in-JS via Tailwind (zero runtime overhead)

## Security

- JWT tokens stored in localStorage (production: upgrade to httpOnly cookies)
- Bearer token in Authorization header for all API requests
- Protected routes with middleware
- CSRF protection via HTTP-only cookies (ready for production)
- XSS prevention via React's built-in escaping

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Deployment

### Vercel (Recommended)

```bash
pnpm build
# Push to GitHub, connect to Vercel
```

### Alternative Platforms
- Railway
- Render
- Netlify

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_JWT_SECRET` | JWT secret key | `dev_secret_key` |
| `NEXT_PUBLIC_ENABLE_DEBUG_MODE` | Enable debug logging | `false` |

## Learning Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [TypeScript](https://www.typescriptlang.org)
- [Vitest](https://vitest.dev)

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes with proper TypeScript types
3. Run tests: `pnpm test`
4. Run linter: `pnpm lint`
5. Commit: `git commit -m "feat: your feature"`
6. Push: `git push origin feature/your-feature`

## License

MIT
