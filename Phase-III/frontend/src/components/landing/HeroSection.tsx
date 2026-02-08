// [Task]: T024, [From]: specs/003-landing-page/spec.md#FR-002
// Hero section with headline, subheadline, CTA, and trust line

'use client';

import React from 'react';
import { useLanguage } from '@/hooks/useLanguage';
import CTAButton from './CTAButton';
import clsx from 'clsx';

const HeroSection: React.FC = () => {
  const { t, isRTL, locale } = useLanguage();

  return (
    <section
      className={clsx(
        // Responsive padding: mobile, tablet, desktop
        'py-12 sm:py-16 md:py-20 lg:py-28 xl:py-32',
        'px-4 sm:px-6 lg:px-8',
        isRTL && 'direction-rtl'
      )}
      aria-label="Hero section - Discover what Evolution of Todo offers"
      role="region"
    >
      <div className="mx-auto max-w-4xl space-y-6 sm:space-y-8 md:space-y-10">
        {/* Main Headline & Subheadline */}
        <div className={clsx('space-y-4', isRTL && 'text-right')}>
          <h1
            className={clsx(
              // Responsive font sizes for headline
              'text-4xl font-bold leading-tight text-gray-900 dark:text-white',
              'sm:text-5xl md:text-6xl lg:text-7xl',
              // Color contrast: #111827 on #FFFFFF = 16.5:1 (exceeds WCAG AAA)
              // Dark mode: white on #030712 = 21:1
              'focus:outline-none'
            )}
            id="hero-headline"
          >
            {t('hero.headline')}
          </h1>
          <p
            className={clsx(
              // Responsive font sizes for subheadline
              'text-lg text-gray-600 dark:text-gray-300',
              'sm:text-xl md:text-2xl lg:text-3xl',
              'leading-relaxed',
              // Color contrast: #4B5563 on #FFFFFF = 6.5:1 (exceeds WCAG AA)
              // Dark mode: #D1D5DB on #030712 = 11:1
              'max-w-3xl'
            )}
            aria-describedby="hero-headline"
            role="complementary"
          >
            {t('hero.subheadline')}
          </p>
        </div>

        {/* CTA Button Container */}
        <div
          className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 sm:gap-6 pt-4"
          role="group"
          aria-label="Call to action buttons"
        >
          <CTAButton
            size="lg"
            href={`/${locale}/auth/signup`}
            aria-label="Get started with Evolution of Todo - no credit card required"
          >
            {t('hero.cta')}
          </CTAButton>
        </div>

        {/* Trust Line - Confidence Building */}
        <p
          className={clsx(
            'text-sm sm:text-base text-gray-500 dark:text-gray-400',
            'flex items-center gap-2',
            isRTL && 'flex-row-reverse'
          )}
          role="status"
          aria-live="polite"
        >
          <span aria-hidden="true" className="text-green-600 dark:text-green-400">
            ✓
          </span>
          <span>{t('hero.trustline')}</span>
        </p>
      </div>
    </section>
  );
};

export default HeroSection;
