// [Task]: T014, [From]: specs/003-landing-page/tasks.md#T014
// Footer component with links, copyright, and social

'use client';

import React from 'react';
import Link from 'next/link';
import { useLanguage } from '@/hooks/useLanguage';
import clsx from 'clsx';

const Footer: React.FC = () => {
  const { t, isRTL, locale } = useLanguage();

  return (
    <footer
      className={clsx(
        'bg-gray-900 text-white',
        isRTL && 'direction-rtl'
      )}
    >
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-400 to-blue-600" />
              <span className="text-lg font-bold">{t('footer.appName')}</span>
            </div>
            <p className="text-sm text-gray-400">
              Simple task management for everyone.
            </p>
          </div>

          {/* Product */}
          <div className="space-y-4">
            <h3 className="font-semibold">Product</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>
                <Link href={`/${locale}/auth/signup`} className="hover:text-white transition-colors">
                  {t('footer.links.signUp')}
                </Link>
              </li>
              <li>
                <Link href={`/${locale}/auth/login`} className="hover:text-white transition-colors">
                  {t('footer.links.logIn')}
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div className="space-y-4">
            <h3 className="font-semibold">Legal</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>
                <a href="/privacy" className="hover:text-white transition-colors">
                  {t('footer.links.privacyPolicy')}
                </a>
              </li>
              <li>
                <a href="/terms" className="hover:text-white transition-colors">
                  {t('footer.links.termsOfService')}
                </a>
              </li>
            </ul>
          </div>

          {/* Social */}
          <div className="space-y-4">
            <h3 className="font-semibold">Social</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition-colors"
                >
                  {t('footer.links.github')}
                </a>
              </li>
              <li>
                <a
                  href="mailto:contact@example.com"
                  className="hover:text-white transition-colors"
                >
                  {t('footer.links.contact')}
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-8 border-t border-gray-800 pt-8 text-center text-sm text-gray-400">
          {t('footer.copyright')}
        </div>
      </div>
    </footer>
  );
};

export default Footer;
