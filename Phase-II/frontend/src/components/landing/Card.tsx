// [Task]: T017, [From]: specs/003-landing-page/tasks.md#T017
// Reusable Card component wrapper for consistent card styling

import React from 'react';
import { CardProps } from '@/types/landing';
import clsx from 'clsx';

const Card: React.FC<CardProps> = ({ children, className, onClick }) => {
  return (
    <div
      onClick={onClick}
      className={clsx(
        'rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition-all dark:border-gray-700 dark:bg-gray-800',
        onClick && 'cursor-pointer hover:shadow-md hover:border-gray-300',
        className
      )}
    >
      {children}
    </div>
  );
};

export default Card;
