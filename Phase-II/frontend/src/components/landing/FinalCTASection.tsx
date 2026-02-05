// [Task]: T040, [From]: specs/003-landing-page/spec.md#FR-010
// Final CTA section with motivational message and "Start Managing Tasks Now" CTA

'use client';

import React from 'react';
import { useLanguage } from '@/hooks/useLanguage';
import CTAButton from './CTAButton';
import clsx from 'clsx';

const FinalCTASection: React.FC = () => {
  const { t, isRTL, locale } = useLanguage();

  return (
    <section
      className={clsx(
        'py-16 sm:py-20 md:py-28 bg-gradient-to-r from-blue-600 to-blue-800 text-white',
        isRTL && 'direction-rtl'
      )}
      aria-label="Final call to action section"
    >
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div className="space-y-8 text-center">
          {/* Motivational Headline */}
          <div className="space-y-4">
            <h2 className="text-4xl font-bold leading-tight sm:text-5xl">
              {t('finalCta.headline')}
            </h2>
            <p className="text-lg text-blue-100 sm:text-xl">
              {t('finalCta.description')}
            </p>
          </div>

          {/* Primary CTA Button */}
          <div className="flex justify-center">
            <CTAButton
              size="lg"
              variant="primary"
              href={`/${locale}/auth/signup`}
              className="bg-white text-blue-600 hover:bg-gray-100"
            >
              {t('finalCta.cta')}
            </CTAButton>
          </div>

          {/* Trust Line */}
          <p className="text-sm text-blue-100">
            ✓ {t('finalCta.trustline')}
          </p>
        </div>
      </div>
    </section>
  );
};

export default FinalCTASection;
