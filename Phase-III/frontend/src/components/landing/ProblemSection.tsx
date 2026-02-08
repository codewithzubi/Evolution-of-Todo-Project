// [Task]: T025, [From]: specs/003-landing-page/spec.md#FR-003
// Problem section listing pain points users face

'use client';

import React from 'react';
import { useLanguage } from '@/hooks/useLanguage';
import SectionHeading from './SectionHeading';
import Card from './Card';
import clsx from 'clsx';

const ProblemSection: React.FC = () => {
  const { t, isRTL } = useLanguage();
  const problems = t.raw('problem.items') as Array<{
    title: string;
    description: string;
  }>;

  return (
    <section
      className={clsx(
        'py-12 sm:py-16 md:py-20 lg:py-28',
        'px-4 sm:px-6 lg:px-8',
        isRTL && 'direction-rtl'
      )}
      aria-label="Problems section - Common task management challenges"
      role="region"
    >
      <div className="mx-auto max-w-6xl space-y-12 md:space-y-16">
        <SectionHeading
          title={t('problem.title')}
          description={t('problem.description')}
        />

        {/* Problem Items Grid - Responsive: 1 col mobile, 2 tablet, 4 desktop */}
        <div
          className="grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-2 lg:grid-cols-4"
          role="list"
          aria-label="List of task management problems"
        >
          {problems && problems.map((problem, index) => (
            <div key={index} role="listitem">
              <Card
                className={clsx(
                  'hover:shadow-lg transition-shadow',
                  'min-h-[200px] flex flex-col'
                )}
              >
              <div className="space-y-3 flex-1">
                {/* Icon with contrast: red-600 on white = 5.1:1 (exceeds WCAG AA) */}
                <div
                  className="flex h-12 w-12 items-center justify-center rounded-lg bg-red-100 dark:bg-red-900"
                  aria-hidden="true"
                >
                  <span className="text-xl font-bold text-red-600 dark:text-red-300">
                    ✕
                  </span>
                </div>
                {/* Problem Title - Semantic heading */}
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {problem.title}
                </h3>
                {/* Problem Description with semantic text color */}
                <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                  {problem.description}
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

export default ProblemSection;
