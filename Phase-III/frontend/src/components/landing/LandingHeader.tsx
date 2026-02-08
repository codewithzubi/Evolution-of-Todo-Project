// [Task]: T012, [From]: specs/003-landing-page/tasks.md#T012
// Landing page header component with logo, navigation, and language selector

'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useLanguage } from '@/hooks/useLanguage';
import LanguageSelector from './LanguageSelector';
import Button from './Button';

const LandingHeader: React.FC = () => {
  const { t, locale } = useLanguage();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-white shadow-sm dark:bg-gray-900">
      <nav className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-600 to-blue-800" />
            <span className="text-xl font-bold text-gray-900 dark:text-white">
              Evolution of Todo
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden items-center space-x-4 md:flex">
            <LanguageSelector />
            <Link href={`/${locale}/auth/login`}>
              <Button variant="outline" size="sm">
                {t('header.logIn')}
              </Button>
            </Link>
            <Link href={`/${locale}/auth/signup`}>
              <Button variant="primary" size="sm">
                {t('header.signUp')}
              </Button>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex items-center space-x-2 md:hidden">
            <LanguageSelector />
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="inline-flex items-center justify-center rounded-md p-2 text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
              aria-expanded="false"
            >
              <span className="sr-only">Open main menu</span>
              {mobileMenuOpen ? (
                <svg
                  className="h-6 w-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              ) : (
                <svg
                  className="h-6 w-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="mt-4 space-y-2 md:hidden">
            <Link href={`/${locale}/auth/login`} className="block">
              <Button variant="outline" size="md" fullWidth>
                {t('header.logIn')}
              </Button>
            </Link>
            <Link href={`/${locale}/auth/signup`} className="block">
              <Button variant="primary" size="md" fullWidth>
                {t('header.signUp')}
              </Button>
            </Link>
          </div>
        )}
      </nav>
    </header>
  );
};

export default LandingHeader;
