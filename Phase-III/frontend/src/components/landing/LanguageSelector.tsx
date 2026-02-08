// [Task]: T013, [From]: specs/003-landing-page/tasks.md#T013
// Language selector component for en/ur/ur-roman toggle

'use client';

import React, { useState } from 'react';
import { useLanguage } from '@/hooks/useLanguage';
import { useRouter, usePathname } from 'next/navigation';
import { LANGUAGES } from '@/i18n/config';
import clsx from 'clsx';

const LanguageSelector: React.FC = () => {
  const { locale } = useLanguage();
  const router = useRouter();
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);

  const handleLanguageChange = (newLocale: string) => {
    // Remove current locale prefix from path
    const pathnameWithoutLocale = pathname.replace(`/${locale}`, '');
    // Construct new path with new locale
    const newPathname = `/${newLocale}${pathnameWithoutLocale}`;

    router.push(newPathname);
    setIsOpen(false);

    // Save preference to localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('preferred-language', newLocale);
    }
  };

  const currentLanguage = LANGUAGES.find((l) => l.code === locale);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
      >
        <svg
          className="h-4 w-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
          />
        </svg>
        <span className="hidden sm:inline">{currentLanguage?.nativeName}</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-40 rounded-lg border border-gray-300 bg-white shadow-lg dark:border-gray-600 dark:bg-gray-800">
          {LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              onClick={() => handleLanguageChange(lang.code)}
              className={clsx(
                'block w-full px-4 py-2 text-left text-sm font-medium transition-colors',
                locale === lang.code
                  ? 'bg-blue-50 text-blue-600 dark:bg-blue-900 dark:text-blue-200'
                  : 'text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
              )}
            >
              {lang.name}
              <span className="ml-2 text-xs opacity-75">({lang.nativeName})</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default LanguageSelector;
