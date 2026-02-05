// [Task]: T-008, [From]: specs/002-task-ui-frontend/spec.md#Requirements
// Root layout component with metadata and providers

import type { Metadata, Viewport } from 'next';
import '@/globals.css';
import { Providers } from '@/providers/Providers';

export const metadata: Metadata = {
  title: 'Evolution of Todo - Task Management',
  description: 'A modern task management application built with Next.js',
  keywords: ['tasks', 'todo', 'productivity', 'management'],
  authors: [{ name: 'Evolution of Todo Team' }],
  robots: 'index, follow',
  openGraph: {
    title: 'Evolution of Todo - Task Management',
    description: 'A modern task management application',
    type: 'website',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
};

interface RootLayoutProps {
  children: React.ReactNode;
}

/**
 * Root Layout Component
 * Provides document structure, metadata, and global providers
 * [Task]: T-008, [From]: specs/002-task-ui-frontend/spec.md#FR-019
 */
export default function RootLayout({ children }: RootLayoutProps): React.ReactNode {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <meta name="theme-color" content="#0ea5e9" />
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
        <base href="/" />
      </head>
      <body>
        {/* Wrap with Providers for auth and React Query */}
        <Providers>
          {/* Main content */}
          <main className="min-h-screen bg-white">{children}</main>

          {/* Toast container for notifications */}
          <div id="toast-container" className="fixed bottom-4 right-4 z-50 space-y-2" />
        </Providers>
      </body>
    </html>
  );
}
