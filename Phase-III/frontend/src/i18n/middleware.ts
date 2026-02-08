// [Task]: T003, [From]: specs/003-landing-page/tasks.md#T003
// i18n middleware for URL-based language routing with next-intl

import { NextRequest, NextResponse } from 'next/server';
import { SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE } from './config';

// Custom middleware that handles locale routing without requiring config file
export default function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // List of supported locales
  const locales = Object.values(SUPPORTED_LANGUAGES);

  // Check if pathname starts with a supported locale
  const localePattern = new RegExp(`^/(${locales.join('|')})(/|$)`);

  if (localePattern.test(pathname)) {
    // Path already has locale prefix, let it through
    return NextResponse.next();
  }

  // If no locale prefix and not a static file or API, redirect to default locale
  if (!pathname.startsWith('/api') && !pathname.startsWith('/_next') && !pathname.match(/\.\w+$/)) {
    const locale = DEFAULT_LANGUAGE;
    const newPathname = `/${locale}${pathname === '/' ? '' : pathname}`;
    return NextResponse.redirect(new URL(newPathname, request.url));
  }

  return NextResponse.next();
}

// Configuration for Next.js middleware routing
export const config = {
  matcher: [
    // Match all routes except: api, _next/static, _next/image, favicon.ico, and files with extensions
    '/((?!api|_next/static|_next/image|favicon\\.ico).*)',
  ],
};
