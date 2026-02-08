// [Task]: T026, [From]: specs/003-landing-page/spec.md#FR-004
// Solution section explaining how app solves problems

'use client';

import React from 'react';
import { useLanguage } from '@/hooks/useLanguage';
import SectionHeading from './SectionHeading';
import Card from './Card';
import clsx from 'clsx';

const SolutionSection: React.FC = () => {
  const { t, isRTL } = useLanguage();
  const highlights = t.raw('solution.highlights') as Array<{
    title: string;
    description: string;
  }>;

  return (
    <section
      className={clsx(
        'py-12 sm:py-16 md:py-20 lg:py-28',
        'px-4 sm:px-6 lg:px-8',
        'bg-blue-50 dark:bg-gray-800',
        isRTL && 'direction-rtl'
      )}
      aria-label="Solution section - How Evolution of Todo solves task management"
      role="region"
    >
      <div className="mx-auto max-w-6xl space-y-12 md:space-y-16">
        <SectionHeading
          title={t('solution.title')}
          description={t('solution.description')}
        />

        {/* Solution Highlights - Responsive: 1 col mobile, 3 desktop */}
        <div
          className="grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-3"
          role="list"
          aria-label="Key solution features"
        >
          {highlights && highlights.map((highlight, index) => (
            <div key={index} role="listitem">
              <Card
                className={clsx(
                  'bg-white dark:bg-gray-900 hover:shadow-lg transition-shadow',
                  'min-h-[200px] flex flex-col'
                )}
              >
              <div className="space-y-3 flex-1">
                {/* Success icon with contrast: green-600 on white = 4.5:1 (meets WCAG AA) */}
                <div
                  className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100 dark:bg-green-900"
                  aria-hidden="true"
                >
                  <span className="text-xl font-bold text-green-600 dark:text-green-300">
                    ✓
                  </span>
                </div>
                {/* Highlight Title */}
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {highlight.title}
                </h3>
                {/* Highlight Description */}
                <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                  {highlight.description}
                </p>
              </div>
              </Card>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default SolutionSection;
