// [Task]: T023, [From]: specs/002-task-ui-frontend/spec.md#FR-011
// Header component with navigation and user menu

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/common/Button';

/**
 * Header component displaying user information and navigation
 *
 * @example
 * <Header />
 */
export function Header() {
  const router = useRouter();
  const { user, logout, isAuthenticated } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    setMobileMenuOpen(false);
    router.push('/login');
  };

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <header className="bg-blue-600 text-white sticky top-0 z-40 shadow-md">
      <div className="max-w-6xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo / Brand */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-400 rounded-lg flex items-center justify-center font-bold">
              T
            </div>
            <h1 className="text-xl font-bold hidden sm:block">Tasks</h1>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <Link
              href="/tasks"
              className="hover:text-blue-100 transition-colors duration-200"
            >
              Tasks
            </Link>

            <div className="flex items-center gap-4 pl-6 border-l border-blue-400">
              <div className="flex flex-col items-end">
                <span className="text-sm font-medium">{user.email}</span>
                {user.name && (
                  <span className="text-xs text-blue-100">{user.name}</span>
                )}
              </div>
              <Button
                variant="secondary"
                onClick={handleLogout}
                className="!px-3 !py-1.5 text-sm"
              >
                Logout
              </Button>
            </div>
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden flex flex-col gap-1 hover:opacity-80 transition-opacity"
            aria-label="Toggle menu"
          >
            <span className="w-6 h-0.5 bg-white block" />
            <span className="w-6 h-0.5 bg-white block" />
            <span className="w-6 h-0.5 bg-white block" />
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="md:hidden mt-4 pt-4 border-t border-blue-400 space-y-3">
            <Link
              href="/tasks"
              className="block hover:text-blue-100 transition-colors duration-200 py-2"
              onClick={() => setMobileMenuOpen(false)}
            >
              Tasks
            </Link>

            <div className="py-3 border-t border-blue-400">
              <div className="mb-3">
                <span className="text-sm font-medium block">{user.email}</span>
                {user.name && (
                  <span className="text-xs text-blue-100">{user.name}</span>
                )}
              </div>
              <Button
                variant="secondary"
                onClick={handleLogout}
                className="w-full text-sm"
              >
                Logout
              </Button>
            </div>
          </nav>
        )}
      </div>
    </header>
  );
}
