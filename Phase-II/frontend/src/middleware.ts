import { NextRequest, NextResponse } from 'next/server';

// Protect dashboard and other authenticated routes
export function middleware(request: NextRequest) {
  // Define protected routes
  const protectedPaths = ['/dashboard', '/tasks', '/profile'];
  const isProtectedPath = protectedPaths.some(path =>
    request.nextUrl.pathname.startsWith(path)
  );

  // Get the auth token from cookies (or wherever you store it)
  const token = request.cookies.get('better-auth-session-token')?.value ||
                request.headers.get('authorization')?.replace('Bearer ', '');

  // If trying to access a protected route without a token
  if (isProtectedPath && !token) {
    // Redirect to login page
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // If trying to access auth pages but already logged in
  const authPaths = ['/login', '/register'];
  const isAuthPath = authPaths.some(path =>
    request.nextUrl.pathname.startsWith(path)
  );

  if (isAuthPath && token) {
    // Redirect to dashboard if already logged in
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Continue with the request
  return NextResponse.next();
}

// Specify which paths the middleware should run on
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};