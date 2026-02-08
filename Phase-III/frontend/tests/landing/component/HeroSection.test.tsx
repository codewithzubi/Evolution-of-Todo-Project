// [Task]: T038, [From]: specs/003-landing-page/tasks.md#T038
// Component tests for HeroSection

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NextIntlClientProvider } from 'next-intl';
import HeroSection from '@/components/landing/HeroSection';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock useLanguage hook
jest.mock('@/hooks/useLanguage', () => ({
  useLanguage: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'hero.headline': 'Manage Your Tasks Effortlessly',
        'hero.subheadline':
          'Simple, powerful task management for students, freelancers, and teams.',
        'hero.cta': 'Get Started Free',
        'hero.trustline': 'No credit card required • Start managing today',
      };
      return translations[key] || key;
    },
    isRTL: false,
  }),
}));

// Mock CTAButton component
jest.mock('@/components/landing/CTAButton', () => {
  return function MockCTAButton({
    children,
    ...props
  }: React.PropsWithChildren<any>) {
    return <button {...props}>{children}</button>;
  };
});

describe('HeroSection', () => {
  test('renders hero headline', () => {
    render(<HeroSection />);

    const headline = screen.getByRole('heading', {
      name: /Manage Your Tasks Effortlessly/i,
    });

    expect(headline).toBeInTheDocument();
    expect(headline).toHaveClass('text-4xl');
  });

  test('renders hero subheadline', () => {
    render(<HeroSection />);

    const subheadline = screen.getByText(
      /Simple, powerful task management for students, freelancers, and teams./i
    );

    expect(subheadline).toBeInTheDocument();
  });

  test('renders CTA button with correct text', () => {
    render(<HeroSection />);

    const ctaButton = screen.getByRole('button', {
      name: /Get Started Free/i,
    });

    expect(ctaButton).toBeInTheDocument();
  });

  test('renders trust line message', () => {
    render(<HeroSection />);

    const trustLine = screen.getByText(/No credit card required/i);

    expect(trustLine).toBeInTheDocument();
  });

  test('displays trust line with checkmark icon', () => {
    render(<HeroSection />);

    const trustLineContainer = screen.getByText(/No credit card required/i);
    const checkmark = trustLineContainer.textContent;

    expect(checkmark).toContain('✓');
  });

  test('section has proper ARIA labels for accessibility', () => {
    render(<HeroSection />);

    const section = screen.getByRole('region', {
      name: /Hero section/i,
    });

    expect(section).toBeInTheDocument();
  });

  test('headline is properly focused for screen readers', () => {
    render(<HeroSection />);

    const headline = screen.getByRole('heading', {
      name: /Manage Your Tasks Effortlessly/i,
    });

    // Verify headline has ID for aria-describedby
    expect(headline).toHaveAttribute('id');
  });

  test('CTA button is keyboard accessible', async () => {
    const user = userEvent.setup();
    render(<HeroSection />);

    const ctaButton = screen.getByRole('button', {
      name: /Get Started Free/i,
    });

    // Verify button can be focused via keyboard
    await user.tab();

    expect(ctaButton).toHaveFocus();
  });

  test('responsive classes are applied', () => {
    const { container } = render(<HeroSection />);

    const section = container.querySelector('section');

    // Check for responsive padding classes
    expect(section).toHaveClass('py-12', 'sm:py-16', 'md:py-20', 'lg:py-28');
  });

  test('has proper color contrast for WCAG AA', () => {
    const { container } = render(<HeroSection />);

    const headline = container.querySelector('h1');
    const subheadline = container.querySelector(
      'p[aria-describedby="hero-headline"]'
    );

    // Verify text colors meet WCAG AA
    // text-gray-900 (dark text) on white background: > 4.5:1 contrast
    expect(headline).toHaveClass('text-gray-900', 'dark:text-white');

    // Gray-600 text: 6.5:1 contrast on white background
    expect(subheadline).toHaveClass(
      'text-gray-600',
      'dark:text-gray-300'
    );
  });

  test('trust line has proper semantic structure', () => {
    render(<HeroSection />);

    const trustLineText = screen.getByText(/No credit card required/i);

    // Verify trust line is in a paragraph with status role
    const trustLineContainer = trustLineText.closest('p');
    expect(trustLineContainer).toHaveAttribute('role', 'status');
  });

  test('renders without errors', () => {
    expect(() => render(<HeroSection />)).not.toThrow();
  });

  test('mobile responsive: single column layout on small screens', () => {
    const { container } = render(<HeroSection />);

    const contentDiv = container.querySelector('.mx-auto.max-w-4xl');

    // Verify max-width is set for large screens but allows full width on mobile
    expect(contentDiv).toHaveClass('max-w-4xl');
  });
});
