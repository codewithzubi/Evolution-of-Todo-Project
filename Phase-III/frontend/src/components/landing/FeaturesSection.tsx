// [Task]: T027, [From]: specs/003-landing-page/spec.md#FR-005
// Features section displaying 5-6 core features

'use client';

import React from 'react';
import { useLanguage } from '@/hooks/useLanguage';
import SectionHeading from './SectionHeading';
import Card from './Card';
import CTAButton from './CTAButton';
import clsx from 'clsx';

const FeaturesSection: React.FC = () => {
  const { t, isRTL, locale } = useLanguage();
  const features = t.raw('features.items') as Array<{
    title: string;
    description: string;
  }>;

  const featureIcons = [
    '⚡', // Quick task creation
    '📅', // Smart due dates
    '📊', // Priority levels
    '🏷️', // Tags & filtering
    '🌍', // Multilingual
    '🤖', // AI-ready
  ];

  return (
    <section
      className={clsx(
        'py-12 sm:py-16 md:py-20 lg:py-28',
        'px-4 sm:px-6 lg:px-8',
        isRTL && 'direction-rtl'
      )}
      aria-label="Features section - Core capabilities of Evolution of Todo"
      role="region"
    >
      <div className="mx-auto max-w-6xl space-y-12 md:space-y-16">
        <SectionHeading
          title={t('features.title')}
          description={t('features.description')}
        />

        {/* Features Grid - Responsive: 1 col mobile, 2 tablet, 3 desktop */}
        <div
          className="grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-2 lg:grid-cols-3"
          role="list"
          aria-label="Feature list with descriptions"
        >
          {features && features.map((feature, index) => (
            <div key={index} role="listitem">
              <Card
                className="hover:shadow-lg transition-shadow flex flex-col min-h-[280px]"
              >
              <div className="space-y-4 flex-1">
                {/* Feature Icon - Emoji with no semantic meaning */}
                <div
                  className="text-4xl sm:text-5xl"
                  aria-hidden="true"
                  role="img"
                >
                  {featureIcons[index] || '✨'}
                </div>
                {/* Feature Content */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white leading-tight">
                    {feature.title}
                  </h3>
                  <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </div>

              {/* Secondary CTA Button on each feature card */}
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <CTAButton
                  size="sm"
                  variant="outline"
                  href={`/${locale}/auth/signup`}
                  fullWidth
                  aria-label={`Learn more about ${feature.title}`}
                >
                  Learn More
                </CTAButton>
              </div>
              </Card>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
