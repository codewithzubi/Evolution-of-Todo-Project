// [Task]: T016, [From]: specs/003-landing-page/tasks.md#T016
// Reusable SectionHeading component for consistent section titles and descriptions

import React from 'react';
import { SectionHeadingProps } from '@/types/landing';
import clsx from 'clsx';

const SectionHeading: React.FC<SectionHeadingProps> = ({
  title,
  description,
  size = 'md',
  centered = true,
  className,
}) => {
  const sizeStyles = {
    sm: {
      title: 'text-2xl md:text-3xl',
      description: 'text-base md:text-lg',
    },
    md: {
      title: 'text-3xl md:text-4xl',
      description: 'text-lg md:text-xl',
    },
    lg: {
      title: 'text-4xl md:text-5xl',
      description: 'text-xl md:text-2xl',
    },
  };

  return (
    <div
      className={clsx(
        'space-y-3 md:space-y-4',
        centered && 'text-center',
        className
      )}
    >
      <h2
        className={clsx(
          'font-bold text-gray-900 dark:text-white',
          sizeStyles[size].title
        )}
      >
        {title}
      </h2>
      {description && (
        <p
          className={clsx(
            'text-gray-600 dark:text-gray-400',
            sizeStyles[size].description
          )}
        >
          {description}
        </p>
      )}
    </div>
  );
};

export default SectionHeading;
