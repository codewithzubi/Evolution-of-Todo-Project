// [Task]: T018, [From]: specs/003-landing-page/tasks.md#T018
// CTA Button component with link to signup endpoint

'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { CTAButtonProps } from '@/types/landing';
import { useCTATracking } from '@/hooks/useCTATracking';
import Button from './Button';
import clsx from 'clsx';

const CTAButton: React.FC<CTAButtonProps> = ({
  href = '/auth/signup',
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  disabled = false,
  className,
}) => {
  const router = useRouter();
  const { trackCTAClick } = useCTATracking();

  const handleClick = () => {
    // Track CTA click with variant type (map outline to secondary)
    const trackingType = variant === 'outline' ? 'secondary' : variant;
    trackCTAClick(
      String(children) || 'CTA Button',
      trackingType as 'primary' | 'secondary' | 'final'
    );

    if (onClick) {
      onClick();
    } else if (href) {
      router.push(href);
    }
  };

  return (
    <Button
      type="button"
      variant={variant}
      size={size}
      fullWidth={fullWidth}
      disabled={disabled}
      onClick={handleClick}
      className={clsx(
        // Ensure CTA buttons are prominent
        variant === 'primary' && 'min-h-[48px]',
        className
      )}
    >
      {children}
    </Button>
  );
};

export default CTAButton;
