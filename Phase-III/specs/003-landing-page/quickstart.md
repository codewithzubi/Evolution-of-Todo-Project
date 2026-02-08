# Quick Start Guide: Landing Page Development

**Feature**: Public Landing Page (003-landing-page)
**Path**: `frontend/src/app/(landing)/`
**Tech Stack**: Next.js 16+, React 18, TypeScript, Tailwind CSS, next-intl
**Duration**: Estimated 15-20 developer days (5 weeks)

---

## Prerequisites

- **Node.js**: v18+ (same as existing project)
- **Next.js**: 16.1+ (already in project)
- **Git**: Cloned `003-landing-page` branch from main
- **IDE**: VS Code or similar with TypeScript support
- **Package Manager**: npm or yarn (same as project)

---

## Environment Setup

### 1. Branch & Dependencies

```bash
# Switch to feature branch
cd /mnt/c/Users/Zubair\ Ahmed/Desktop/Phase2
git checkout 003-landing-page

# Install any new dependencies (next-intl)
cd frontend
npm install next-intl

# Verify Next.js version
npm list next
# Output: next@16.1.6 (or higher)
```

### 2. Directory Structure

```bash
# Create landing-specific directories
mkdir -p src/app/\(landing\)
mkdir -p src/components/landing
mkdir -p src/i18n/locales
mkdir -p src/hooks
mkdir -p src/types
mkdir -p public/images/{hero-bg,feature-icons,app-screenshots,illustrations}
mkdir -p tests/landing/{e2e,component,unit}
```

### 3. Environment Variables

No new environment variables required for landing page. Existing `NEXT_PUBLIC_*` variables should be used.

---

## Project File Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── (landing)/
│   │   │   ├── page.tsx              # Main landing page
│   │   │   ├── layout.tsx            # Landing layout (header, footer)
│   │   │   ├── metadata.ts           # SEO metadata
│   │   │   └── globals.css           # Landing-specific styles (if needed)
│   │   ├── layout.tsx                # Root layout
│   │   └── ... (existing routes)
│   ├── components/
│   │   ├── landing/
│   │   │   ├── HeroSection.tsx
│   │   │   ├── ProblemSection.tsx
│   │   │   ├── SolutionSection.tsx
│   │   │   ├── FeaturesSection.tsx
│   │   │   ├── HowItWorksSection.tsx
│   │   │   ├── PreviewSection.tsx
│   │   │   ├── TargetAudienceSection.tsx
│   │   │   ├── PricingSection.tsx
│   │   │   ├── FinalCTASection.tsx
│   │   │   ├── LandingHeader.tsx
│   │   │   ├── LanguageSelector.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── index.ts              # Barrel export
│   │   ├── layout/
│   │   └── common/
│   ├── hooks/
│   │   └── useLanguage.ts            # Language switching hook
│   ├── i18n/
│   │   ├── config.ts                 # i18n configuration
│   │   ├── middleware.ts             # Language routing middleware
│   │   ├── locales/
│   │   │   ├── en.json               # English translations
│   │   │   ├── ur.json               # Urdu translations
│   │   │   └── ur-roman.json         # Roman Urdu translations
│   │   └── translate.ts              # Translation helper
│   ├── types/
│   │   └── landing.ts                # Landing page types
│   └── styles/
│       └── landing.css               # Landing-specific styles (if needed)
├── public/
│   ├── images/
│   │   ├── hero-bg.png               # Hero background image
│   │   ├── hero-bg.webp              # WebP format
│   │   ├── feature-icons/
│   │   │   ├── tasks.svg
│   │   │   ├── calendar.svg
│   │   │   └── ...
│   │   ├── app-screenshots/
│   │   │   ├── dashboard.png
│   │   │   ├── task-list.png
│   │   │   └── create-task-modal.png
│   │   └── illustrations/
│   │       └── ...
│   └── ... (existing public assets)
└── tests/
    ├── landing/
    │   ├── e2e/
    │   │   ├── landing.spec.ts       # Playwright E2E tests
    │   │   ├── conversion.spec.ts
    │   │   └── accessibility.spec.ts
    │   ├── component/
    │   │   ├── HeroSection.test.tsx  # React Testing Library
    │   │   ├── FeaturesSection.test.tsx
    │   │   └── ...
    │   └── unit/
    │       └── useLanguage.test.ts
    └── ... (existing tests)
```

---

## Development Workflow

### 1. Start Dev Server

```bash
cd frontend

# Start Next.js development server
npm run dev

# App runs at http://localhost:3000
# Landing page available at http://localhost:3000 (or http://localhost:3001 if port in use)
```

### 2. Create a Component

**Example**: HeroSection.tsx

```typescript
// src/components/landing/HeroSection.tsx
'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import Button from '@/components/common/Button';

export default function HeroSection() {
  const t = useTranslations('hero');

  return (
    <section className="py-20 px-4 md:py-40 bg-gradient-to-r from-blue-50 to-white">
      <div className="container mx-auto max-w-4xl text-center">
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
          {t('headline')}
        </h1>
        <p className="text-lg md:text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          {t('subheadline')}
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
          <Link href="/auth/signup">
            <Button variant="primary" size="lg">
              {t('cta')}
            </Button>
          </Link>
        </div>
        <p className="text-sm text-gray-500">{t('trustline')}</p>
      </div>
    </section>
  );
}
```

### 3. Add Translations

**File**: `src/i18n/locales/en.json`

```json
{
  "hero": {
    "headline": "Manage Your Tasks with Ease",
    "subheadline": "The simple, free todo app for students, freelancers, and teams",
    "cta": "Get Started Free",
    "trustline": "No credit card required"
  },
  "problem": {
    "title": "Your Tasks Are All Over the Place",
    "items": [
      "Forgotten deadlines",
      "Scattered tasks across multiple apps",
      "Unclear priorities"
    ]
  }
}
```

### 4. Hot Reload & Testing

```bash
# Edit a component and save
# Next.js automatically reloads (Fast Refresh)

# Run tests
npm run test

# Run E2E tests
npm run test:e2e

# Check accessibility
npm run test:a11y
```

---

## Key Commands

```bash
# Development
npm run dev                    # Start dev server
npm run build                  # Build for production
npm run start                  # Start production server
npm run lint                   # Run ESLint
npm run format                 # Run Prettier (if configured)

# Testing
npm run test                   # Jest + React Testing Library
npm run test:e2e               # Playwright E2E tests
npm run test:a11y              # Accessibility audit (axe-core)
npm run test:performance       # Lighthouse CI

# Type checking
npm run type-check             # TypeScript check
```

---

## Component Development Checklist

For each section component, follow this checklist:

- [ ] Create component file in `src/components/landing/`
- [ ] Add TypeScript types in `src/types/landing.ts` (if needed)
- [ ] Import translations using `useTranslations()` hook
- [ ] Implement responsive design (mobile-first with Tailwind)
- [ ] Add ARIA labels and semantic HTML
- [ ] Test color contrast (4.5:1 for normal text)
- [ ] Add unit tests in `tests/landing/component/`
- [ ] Test on mobile (320px), tablet (768px), desktop (1024px+)
- [ ] Test keyboard navigation (Tab, Enter)
- [ ] Test with screen reader (NVDA/JAWS simulation)
- [ ] Run Lighthouse audit
- [ ] Commit with spec reference: `// [Task]: T-XXX, [From]: specs/003-landing-page/spec.md#FR-XXX`

---

## i18n (Internationalization) Setup

### Configuration File

**File**: `src/i18n/config.ts`

```typescript
import { notFound } from 'next/navigation';
import { getRequestConfig } from 'next-intl/server';

const locales = ['en', 'ur', 'ur-roman'];
const defaultLocale = 'en';

export const getConfig = async (locale: string) => {
  if (!locales.includes(locale as any)) notFound();
  return (await import(`./locales/${locale}.json`)).default;
};

export default getRequestConfig(async ({ locale }) => ({
  messages: await getConfig(locale),
}));
```

### Using Translations in Components

```typescript
'use client';

import { useTranslations } from 'next-intl';

export default function MyComponent() {
  const t = useTranslations();

  return (
    <h1>{t('hero.headline')}</h1>  // Namespace.key syntax
  );
}
```

---

## Testing Strategy

### Unit Tests (Jest + React Testing Library)

```typescript
// tests/landing/component/HeroSection.test.tsx
import { render, screen } from '@testing-library/react';
import HeroSection from '@/components/landing/HeroSection';
import { IntlProvider } from 'next-intl';

describe('HeroSection', () => {
  it('renders headline with correct text', () => {
    render(
      <IntlProvider locale="en" messages={{}}>
        <HeroSection />
      </IntlProvider>
    );

    const headline = screen.getByRole('heading', { level: 1 });
    expect(headline).toBeInTheDocument();
  });

  it('has accessible CTA button', () => {
    render(<HeroSection />);
    const button = screen.getByRole('link', { name: /get started/i });
    expect(button).toHaveAttribute('href', '/auth/signup');
  });
});
```

### E2E Tests (Playwright)

```typescript
// tests/landing/e2e/landing.spec.ts
import { test, expect } from '@playwright/test';

test('visitor can navigate hero to signup', async ({ page }) => {
  await page.goto('http://localhost:3000');

  const cta = page.getByRole('link', { name: /get started/i });
  await expect(cta).toBeVisible();

  await cta.click();
  await expect(page).toHaveURL('/auth/signup');
});

test('language selector works', async ({ page }) => {
  await page.goto('http://localhost:3000');

  const languageSelector = page.getByLabel('Language');
  await languageSelector.selectOption('ur');

  // Verify page reloaded with Urdu content
  const headline = page.getByRole('heading', { level: 1 });
  await expect(headline).toContainText(/مدیریت/); // Urdu text
});
```

### Accessibility Testing

```bash
# Run axe-core accessibility audit
npm run test:a11y

# Check WCAG AA compliance
# Expected: No violations, only warnings
```

---

## Performance Monitoring

### Lighthouse CI

```bash
# Run Lighthouse audit locally
npm run test:performance

# Expected scores:
# - Performance: 90+
# - SEO: 90+
# - Accessibility: 90+
# - Best Practices: 85+
```

### Core Web Vitals Targets

Monitor these metrics:
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1

---

## Git Workflow

### Committing Changes

```bash
# Each commit must reference spec and task ID
git add src/components/landing/HeroSection.tsx
git commit -m "Implement HeroSection component

// [Task]: T-001, [From]: specs/003-landing-page/spec.md#FR-001"

# Push to feature branch
git push origin 003-landing-page
```

### Creating Pull Request

When feature is complete:

```bash
# Push final commits
git push origin 003-landing-page

# Create PR to main
gh pr create \
  --title "Landing page implementation" \
  --body "Implements full landing page with 10 sections, multilingual support, accessibility, and performance optimizations."
```

---

## Common Tasks

### Adding a New Language

1. Duplicate `src/i18n/locales/en.json` → `src/i18n/locales/[new-locale].json`
2. Translate all keys
3. Update `src/i18n/config.ts` locale list: `const locales = ['en', 'ur', 'ur-roman', '[new-locale]']`
4. Test language switcher
5. Run Lighthouse audit (check for missing translations)

### Updating Landing Content

1. Edit JSON files in `src/i18n/locales/`
2. All translations update automatically on hot reload
3. Commit with message referencing which sections changed

### Adding a New Section

1. Create component in `src/components/landing/[NewSection].tsx`
2. Add translations to all JSON files
3. Import and add to `src/app/(landing)/page.tsx`
4. Add unit tests
5. Verify responsive design at all breakpoints
6. Run Lighthouse audit

---

## Debugging Tips

### TypeScript Errors

```bash
npm run type-check
# Shows all type errors; fix before committing
```

### Translation Missing Keys

```bash
# Look for console warnings about missing translation keys
# Usually shown in browser DevTools Console
```

### Performance Bottlenecks

```bash
# Use Chrome DevTools Lighthouse tab
# Or run: npm run test:performance

# Common issues:
# - Large images (use Next.js Image component with responsive sizes)
# - Unoptimized fonts (use next/font)
# - Render blocking scripts (defer or async)
```

### Accessibility Issues

```bash
# Use Chrome DevTools Accessibility tree
# Or screen reader (NVDA, JAWS, VoiceOver)

# Common issues:
# - Missing alt text on images
# - Poor color contrast
# - Missing form labels
```

---

## Documentation & Resources

### Next.js References
- [App Router Documentation](https://nextjs.org/docs/app)
- [Image Optimization](https://nextjs.org/docs/app/building-your-application/optimizing/images)
- [Metadata API](https://nextjs.org/docs/app/building-your-application/optimizing/metadata)

### i18n
- [next-intl Documentation](https://next-intl-docs.vercel.app/)

### Accessibility
- [WCAG 2.1 Level AA](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

### Testing
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [React Testing Library Queries](https://testing-library.com/docs/dom-testing-library/queries)

---

## Deployment Checklist

Before deploying landing page to production:

- [ ] All tests passing (unit, component, E2E, accessibility)
- [ ] Lighthouse scores 90+ for Performance, SEO, Accessibility
- [ ] Mobile responsiveness tested on real devices (iPhone, Android)
- [ ] All translations reviewed by native speakers
- [ ] SEO meta tags verified (title, description, og:image)
- [ ] Schema.org structured data validated
- [ ] Links tested (no 404s, external links working)
- [ ] Analytics script added (if applicable)
- [ ] Redirects configured (if changing URL structure)
- [ ] Performance monitoring enabled (Web Vitals, Lighthouse CI)
- [ ] Commit messages reference specs and task IDs
- [ ] PR reviewed and approved
- [ ] Deployed to staging for final QA
- [ ] Feature flag tested (if using feature flags)
- [ ] Monitoring alerts configured
- [ ] Rollback plan documented

---

## Support & Questions

For implementation questions:
1. Refer to spec.md for requirements
2. Check plan.md for architecture decisions
3. Search research.md for technical choices
4. Review existing task UI components for patterns
5. Ask on team Slack or create a discussion thread

Next step: `/sp.tasks` to generate specific implementation tasks.
