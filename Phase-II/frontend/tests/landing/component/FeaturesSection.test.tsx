// [Task]: T039, [From]: specs/003-landing-page/tasks.md#T039
// Component tests for FeaturesSection

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FeaturesSection from '@/components/landing/FeaturesSection';

// Mock useLanguage hook
jest.mock('@/hooks/useLanguage', () => ({
  useLanguage: () => ({
    t: (key: string) => {
      const translations: Record<string, string | any> = {
        'features.title': 'Powerful Features Built for You',
        'features.description': 'Everything you need to stay organized.',
        'features.items': [
          {
            title: 'Quick Task Creation',
            description: 'Add tasks with due dates and priorities.',
          },
          {
            title: 'Smart Due Dates',
            description: 'Never miss a deadline.',
          },
          {
            title: 'Priority Levels',
            description: 'Focus on what matters most.',
          },
          {
            title: 'Tags & Filtering',
            description: 'Organize with custom tags.',
          },
          {
            title: 'Multilingual Support',
            description: 'Use in your preferred language.',
          },
          {
            title: 'AI-Ready Architecture',
            description: 'Built for the future.',
          },
        ],
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
    'aria-label': ariaLabel,
    ...props
  }: React.PropsWithChildren<any>) {
    return (
      <button aria-label={ariaLabel} {...props}>
        {children}
      </button>
    );
  };
});

// Mock SectionHeading component
jest.mock('@/components/landing/SectionHeading', () => {
  return function MockSectionHeading({
    title,
    description,
  }: {
    title: string;
    description: string;
  }) {
    return (
      <div>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
    );
  };
});

// Mock Card component
jest.mock('@/components/landing/Card', () => {
  return function MockCard({
    children,
    role,
  }: React.PropsWithChildren<{ role?: string }>) {
    return <div role={role}>{children}</div>;
  };
});

describe('FeaturesSection', () => {
  test('renders features section title', () => {
    render(<FeaturesSection />);

    const title = screen.getByRole('heading', {
      name: /Powerful Features Built for You/i,
    });

    expect(title).toBeInTheDocument();
  });

  test('renders section description', () => {
    render(<FeaturesSection />);

    const description = screen.getByText(
      /Everything you need to stay organized./i
    );

    expect(description).toBeInTheDocument();
  });

  test('renders all 6 features', () => {
    render(<FeaturesSection />);

    const features = [
      'Quick Task Creation',
      'Smart Due Dates',
      'Priority Levels',
      'Tags & Filtering',
      'Multilingual Support',
      'AI-Ready Architecture',
    ];

    features.forEach((feature) => {
      expect(screen.getByText(feature)).toBeInTheDocument();
    });
  });

  test('renders feature descriptions', () => {
    render(<FeaturesSection />);

    const descriptions = [
      'Add tasks with due dates and priorities.',
      'Never miss a deadline.',
      'Focus on what matters most.',
      'Organize with custom tags.',
      'Use in your preferred language.',
      'Built for the future.',
    ];

    descriptions.forEach((desc) => {
      expect(screen.getByText(desc)).toBeInTheDocument();
    });
  });

  test('renders "Learn More" button for each feature', () => {
    render(<FeaturesSection />);

    const buttons = screen.getAllByRole('button', {
      name: /Learn More/i,
    });

    // Should have 6 buttons, one for each feature
    expect(buttons).toHaveLength(6);
  });

  test('each Learn More button has appropriate aria-label', () => {
    render(<FeaturesSection />);

    const quickTaskButton = screen.getByLabelText(
      /Learn more about Quick Task Creation/i
    );
    const aiButton = screen.getByLabelText(/Learn more about AI-Ready/i);

    expect(quickTaskButton).toBeInTheDocument();
    expect(aiButton).toBeInTheDocument();
  });

  test('section has proper ARIA labels for accessibility', () => {
    render(<FeaturesSection />);

    const section = screen.getByRole('region', {
      name: /Features section/i,
    });

    expect(section).toBeInTheDocument();
  });

  test('features are rendered as a list with ARIA roles', () => {
    render(<FeaturesSection />);

    const featureList = screen.getByRole('list', {
      name: /Feature list with descriptions/i,
    });

    expect(featureList).toBeInTheDocument();

    // Each feature should be a list item
    const listItems = screen.getAllByRole('listitem');
    expect(listItems).toHaveLength(6);
  });

  test('responsive classes are applied', () => {
    const { container } = render(<FeaturesSection />);

    const section = container.querySelector('section');

    // Check for responsive padding classes
    expect(section).toHaveClass(
      'py-12',
      'sm:py-16',
      'md:py-20',
      'lg:py-28'
    );
  });

  test('grid layout is responsive', () => {
    const { container } = render(<FeaturesSection />);

    const grid = container.querySelector('.grid');

    // Check for responsive grid classes: 1 col mobile, 2 tablet, 3 desktop
    expect(grid).toHaveClass(
      'grid-cols-1',
      'md:grid-cols-2',
      'lg:grid-cols-3'
    );
  });

  test('feature cards have minimum height', () => {
    const { container } = render(<FeaturesSection />);

    const cards = container.querySelectorAll('[role="listitem"]');

    // Each card should have class for minimum height
    cards.forEach((card) => {
      expect(card).toHaveClass('min-h-[280px]');
    });
  });

  test('feature icons are not read by screen readers', () => {
    const { container } = render(<FeaturesSection />);

    // Find emoji icons and verify they have aria-hidden
    const icons = container.querySelectorAll('[aria-hidden="true"]');

    expect(icons.length).toBeGreaterThan(0);

    // Verify icons have role="img"
    icons.forEach((icon) => {
      expect(icon).toHaveAttribute('role', 'img');
    });
  });

  test('has proper color contrast for text', () => {
    const { container } = render(<FeaturesSection />);

    // Feature titles should have proper contrast
    const titles = container.querySelectorAll('h3');

    titles.forEach((title) => {
      expect(title).toHaveClass(
        'text-gray-900',
        'dark:text-white'
      );
    });

    // Descriptions should have adequate contrast
    const descriptions = container.querySelectorAll(
      'p:not([role="status"])'
    );

    descriptions.forEach((desc) => {
      expect(desc).toHaveClass(
        'text-gray-600',
        'dark:text-gray-400'
      );
    });
  });

  test('buttons are keyboard accessible', async () => {
    const user = userEvent.setup();
    render(<FeaturesSection />);

    const buttons = screen.getAllByRole('button', {
      name: /Learn More/i,
    });

    // Tab to first button
    await user.tab();

    expect(buttons[0]).toHaveFocus();

    // Tab to next button
    await user.tab();

    expect(buttons[1]).toHaveFocus();
  });

  test('card sections have proper semantic structure', () => {
    const { container } = render(<FeaturesSection />);

    // Each feature card should contain a title, description, and button
    const cards = container.querySelectorAll('[role="listitem"]');

    cards.forEach((card) => {
      const heading = card.querySelector('h3');
      const paragraph = card.querySelector('p');
      const button = card.querySelector('button');

      expect(heading).toBeInTheDocument();
      expect(paragraph).toBeInTheDocument();
      expect(button).toBeInTheDocument();
    });
  });

  test('renders without errors', () => {
    expect(() => render(<FeaturesSection />)).not.toThrow();
  });
});
