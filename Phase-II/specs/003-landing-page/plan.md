# Implementation Plan: Public Landing Page

**Branch**: `003-landing-page` | **Date**: 2026-02-04 | **Spec**: [specs/003-landing-page/spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-landing-page/spec.md`

**Note**: This plan implements the public landing page for the Evolution of Todo app, designed to drive user discovery and conversion.

## Summary

Build a professional, responsive, and multilingual (English/Urdu/Roman Urdu) landing page that serves as the primary entry point for the Todo app. The landing page must communicate the app's core value proposition, address user pain points, showcase key features, and drive signup conversion. Requirements: <2s load time, 80% visitor comprehension in 30 seconds, 15-20% CTA conversion rate, WCAG AA accessibility, fully responsive (mobile/tablet/desktop), optimized for SEO, and support for three languages with proper localization.

## Technical Context

**Language/Version**: TypeScript 5+, React 18+, Next.js 16+ (App Router)
**Primary Dependencies**: Next.js 16+, React 18+, Tailwind CSS 3.x, i18n library (next-intl or similar), Framer Motion (optional for animations), TypeScript
**Storage**: None (static content, configuration-driven)
**Testing**: Playwright (E2E), Jest + React Testing Library (unit/component), Lighthouse (performance/SEO/accessibility audits)
**Target Platform**: Web (Chrome, Firefox, Safari, Edge; desktop, tablet, mobile)
**Project Type**: Web (frontend-only, single-page application)
**Performance Goals**: Page load < 2 seconds (on standard 4G), Core Web Vitals: LCP <2.5s, FID <100ms, CLS <0.1, SEO score 90+, Lighthouse performance 90+
**Constraints**: Mobile-first responsive design (320px-1920px), WCAG AA accessibility compliance, multilingual support (3 languages), zero external JavaScript dependencies (use built-in Next.js), SEO-optimized meta tags, no tracking/analytics scripts blocking render
**Scale/Scope**: Single public landing page (~10-15 sections), static content, 3 language variants, ~20-30 React components (header, hero, feature card, CTA button, etc.), estimated 2000-3000 lines of code (JSX + styles)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Spec-First Development**: Feature specification complete with 6 user stories, 18 functional requirements, 12 success criteria, and 4 edge cases. All requirements testable and unambiguous. ✅ PASS

✅ **Progressive Evolution Architecture**: Landing page is frontend-only, stateless, and does not depend on backend services. Integrates with existing signup/login endpoints only. ✅ PASS

✅ **Clean Architecture & Stateless Services**: Landing page is a stateless React application; no session management or state persistence required. Uses static content model. ✅ PASS

✅ **Monorepo & Folder Sovereignty**: Landing page lives in `frontend/src/app/(landing)/` directory within existing Next.js monorepo. Follows existing project structure and naming conventions. ✅ PASS

✅ **Type Safety & Validation**: All UI components use TypeScript types, props are validated, translations use typed keys. ✅ PASS

✅ **Spec Traceability & Testing**: All features map to specific functional requirements. Testing strategy includes E2E (Playwright), component (React Testing Library), performance (Lighthouse), and accessibility (axe) audits. ✅ PASS

✅ **Security & Data Privacy**: Landing page does not collect, store, or transmit user data. Links to privacy policy and terms. No authentication required. ✅ PASS

✅ **Documentation & Knowledge Transfer**: Plan includes quickstart, component architecture, translation strategy, and deployment checklist. ✅ PASS

**Re-check after Phase 1**: Design decisions (component hierarchy, styling approach, i18n strategy) to be validated.

## Project Structure

### Documentation (this feature)

```text
specs/003-landing-page/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (TBD: /sp.plan command)
├── data-model.md        # Phase 1 output (TBD: /sp.plan command)
├── quickstart.md        # Phase 1 output (TBD: /sp.plan command)
├── contracts/           # Phase 1 output (TBD: /sp.plan command)
├── checklists/
│   └── requirements.md  # Quality checklist (completed)
└── tasks.md             # Phase 2 output (TBD: /sp.tasks command)
```

### Source Code (repository root)

**Structure Decision**: Web application (Next.js 16+ frontend-only). Landing page is a new route in the existing frontend application, built as a stateless React component hierarchy.

```text
frontend/
├── src/
│   ├── app/
│   │   ├── (landing)/          # NEW: Landing page route group
│   │   │   ├── page.tsx        # Main landing page (root page component)
│   │   │   ├── layout.tsx      # Landing-specific layout (header, footer)
│   │   │   └── metadata.ts     # SEO metadata (dynamic)
│   │   ├── layout.tsx          # Root layout (shared across app)
│   │   └── ... (existing routes)
│   ├── components/
│   │   ├── landing/            # NEW: Landing-specific components
│   │   │   ├── HeroSection.tsx
│   │   │   ├── ProblemSection.tsx
│   │   │   ├── SolutionSection.tsx
│   │   │   ├── FeaturesSection.tsx
│   │   │   ├── HowItWorksSection.tsx
│   │   │   ├── PreviewSection.tsx
│   │   │   ├── TargetAudienceSection.tsx
│   │   │   ├── PricingSection.tsx
│   │   │   ├── FinalCTASection.tsx
│   │   │   ├── LanguageSelector.tsx
│   │   │   └── LandingHeader.tsx
│   │   ├── layout/             # Existing layout components
│   │   └── common/             # Existing shared components
│   ├── hooks/
│   │   └── useLanguage.ts      # NEW: Language/i18n hook
│   ├── i18n/                   # NEW: Internationalization setup
│   │   ├── config.ts
│   │   ├── locales/
│   │   │   ├── en.json
│   │   │   ├── ur.json
│   │   │   └── ur-roman.json
│   │   └── translate.ts
│   ├── styles/                 # Existing global styles
│   └── types/
│       └── landing.ts          # NEW: Landing page types
├── public/
│   ├── images/                 # NEW: Landing page assets
│   │   ├── hero-bg.png
│   │   ├── feature-icons/
│   │   ├── app-screenshots/
│   │   └── illustrations/
│   └── ... (existing public assets)
└── tests/
    ├── landing/                # NEW: Landing page tests
    │   ├── e2e/
    │   │   ├── landing.spec.ts (Playwright)
    │   │   ├── conversion.spec.ts
    │   │   └── accessibility.spec.ts
    │   ├── component/
    │   │   ├── HeroSection.test.tsx
    │   │   ├── FeaturesSection.test.tsx
    │   │   └── ...
    │   └── unit/
    │       └── useLanguage.test.ts
    └── ... (existing tests)
```

**Key Design Decisions**:
1. **Route Structure**: Landing page at root (`/`) using Next.js App Router with a route group `(landing)` to scope layout and components.
2. **Internationalization**: Use next-intl library with static translations in JSON files (en.json, ur.json, ur-roman.json). Language selector in header to switch dynamically.
3. **Component Organization**: Each section (hero, features, pricing, etc.) is a separate React component for reusability and testability.
4. **Styling**: Tailwind CSS (existing in project) with utility classes; no additional CSS-in-JS libraries.
5. **SEO & Metadata**: Use Next.js `generateMetadata()` for dynamic OG tags, meta descriptions; add structured data (Schema.org) for rich snippets.
6. **Performance**: Lazy-load images with `<Image>` component from Next.js; defer animations; code-split by section if needed.
7. **Accessibility**: Use semantic HTML (`<main>`, `<section>`, `<article>`), ARIA labels, proper heading hierarchy, keyboard navigation, color contrast ratios meeting WCAG AA.
8. **Testing Strategy**:
   - E2E: Playwright tests for conversion flow (hero → CTA → signup), language switching, responsive behavior.
   - Component: React Testing Library for individual sections (hero, features, etc.).
   - Performance: Lighthouse CI for continuous monitoring of load time, SEO, accessibility, performance scores.

## Complexity Tracking

> **No Constitution Check violations detected. All design decisions align with project principles.**

---

## Phase 0: Research & Unknowns Resolution

**Status**: ✅ COMPLETE (no unknowns requiring external research)

### Resolved Questions

1. **Language/i18n Library**: ✅ Decided on `next-intl` (industry standard for Next.js multilingual apps, supports static exports, SSR).
2. **Styling Approach**: ✅ Tailwind CSS (existing in project, no new dependencies needed).
3. **Component Library**: ✅ Use existing component patterns from task UI (button, card, section, etc.); no external UI library needed.
4. **SEO Strategy**: ✅ Next.js built-in metadata API + dynamic meta tags; no additional SEO tools required.
5. **Image Optimization**: ✅ Use Next.js `<Image>` component for automatic optimization and lazy loading.
6. **Animation Library**: ✅ Optional Framer Motion for subtle scroll effects; not required for MVP. Can be added later.
7. **Analytics**: ✅ Google Analytics optional; not blocking feature. Can be added post-launch.

### Output
No external research needed; all design decisions documented in Technical Context and Project Structure sections.

---

## Phase 1: Design & Contracts

### 1.1 Data Model

**Landing Page Configuration Model** (`data-model.md` TBD):

The landing page uses a static content configuration model; no dynamic data storage required. All content is defined in i18n translation files and component constants.

**Entities**:
- **LanguageConfig**: Supported languages (en, ur, ur-roman) with locale settings
- **SectionContent**: Hero, Problem, Solution, Features, HowItWorks, Preview, TargetAudience, Pricing, FinalCTA, Footer (defined in translation files)
- **FeatureItem**: Icon, title, description for each feature (array in config)
- **CTAButton**: Text, link destination, styling variant (primary/secondary)
- **TranslationKey**: Nested object structure for i18n strings

### 1.2 API Contracts

**Landing Page Endpoints** (`contracts/` TBD):

The landing page is fully static with no backend API calls during normal viewing. However, CTA links point to existing backend endpoints:

| Endpoint | Purpose | Expected Response |
|----------|---------|-------------------|
| `/auth/signup` | Navigate to signup form | HTML page (handled by existing auth system) |
| `/auth/login` | Navigate to login form | HTML page (handled by existing auth system) |
| Privacy Policy (static) | Link to privacy document | HTML or PDF |
| Terms of Service (static) | Link to T&Cs document | HTML or PDF |
| GitHub/Social (external) | Links to external profiles | External site |

**Language Configuration Endpoints**:
- Language preference stored in browser localStorage or URL parameter (`?lang=ur`)
- No server-side session needed

### 1.3 Component Architecture

**Proposed Component Hierarchy** (`quickstart.md` TBD):

```
LandingPage (root)
├── LandingHeader
│   ├── Logo
│   ├── LanguageSelector
│   └── HeaderCTA (Desktop)
├── Main
│   ├── HeroSection
│   │   ├── Headline
│   │   ├── Subheadline
│   │   ├── CTAButton (Primary)
│   │   └── TrustLine
│   ├── ProblemSection
│   │   ├── SectionHeading
│   │   └── ProblemCard[] (x3-4)
│   ├── SolutionSection
│   │   ├── SectionHeading
│   │   └── SolutionContent
│   ├── FeaturesSection
│   │   ├── SectionHeading
│   │   └── FeatureCard[] (x5-6)
│   ├── HowItWorksSection
│   │   ├── SectionHeading
│   │   └── StepCard[] (x3)
│   ├── PreviewSection
│   │   ├── SectionHeading
│   │   └── ScreenshotCarousel
│   ├── TargetAudienceSection
│   │   ├── SectionHeading
│   │   └── PersonaCard[] (x4)
│   ├── PricingSection
│   │   ├── SectionHeading
│   │   └── PricingHighlight
│   ├── FinalCTASection
│   │   ├── ClosingMessage
│   │   └── CTAButton (Secondary)
│   └── Footer
│       ├── Logo
│       ├── Links (Privacy, Terms, GitHub)
│       ├── Copyright
│       └── SocialLinks

Utility Components:
├── Button (variants: primary, secondary, text)
├── Card (wrapper for sections)
├── SectionHeading
├── LanguageSelector
└── ResponsiveImage (with lazy loading)
```

### 1.4 Styling & Responsive Design

**Breakpoints** (Tailwind CSS):
- Mobile: 320px - 767px (`sm` and below)
- Tablet: 768px - 1024px (`md`)
- Desktop: 1025px+ (`lg` and above)

**Color Palette**:
- Primary: Blue (from existing app theme)
- Secondary: Gray
- Accent: Green (for CTAs, positive actions)
- Background: White/Off-white
- Text: Dark gray/Black
- Error/Warning: Red/Orange (for future notifications)

**Typography**:
- Heading 1 (H1): 48px (desktop), 32px (mobile) - Hero headline
- Heading 2 (H2): 36px (desktop), 24px (mobile) - Section headings
- Body: 16px - Default text
- Small: 14px - Metadata, captions

### 1.5 Internationalization Strategy

**i18n Library**: `next-intl` (supports middleware, static exports, TypeScript)

**File Structure**:
```
src/i18n/
├── config.ts              # i18n config (locales, default)
├── middleware.ts          # URL-based language routing (if needed)
├── locales/
│   ├── en.json            # English (master/source language)
│   ├── ur.json            # Urdu (Nastaliq/Naskh script)
│   └── ur-roman.json      # Roman Urdu (Latin transliteration)
└── translate.ts           # Helper function for server-side translation
```

**Content Translation Structure**:
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
    "items": ["Forgotten deadlines", "Scattered tasks", "Unclear priorities"]
  },
  ...
}
```

**Language Switching**: User selects language via dropdown/toggle in header; preference saved to localStorage and reflected in URL (`/en`, `/ur`, `/ur-roman`).

### 1.6 SEO & Metadata Strategy

**Meta Tags**:
```html
<title>Evolution Todo - Free Task Management App</title>
<meta name="description" content="Simple, free task management for students, freelancers, and teams. No credit card required.">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta property="og:title" content="Evolution Todo - Task Management">
<meta property="og:description" content="...">
<meta property="og:image" content="[hero-image-url]">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
```

**Structured Data** (Schema.org):
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Evolution Todo",
  "description": "Free task management app",
  "url": "https://example.com",
  "applicationCategory": "ProductivityApplication",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "ratingCount": "100"
  }
}
```

### 1.7 Performance & Accessibility Targets

**Performance**:
- Lighthouse Performance Score: 90+
- Largest Contentful Paint (LCP): <2.5s
- First Input Delay (FID): <100ms
- Cumulative Layout Shift (CLS): <0.1
- Page load time: <2s on standard 4G

**Accessibility** (WCAG AA):
- Color contrast ratio: 4.5:1 (normal text), 3:1 (large text)
- Keyboard navigation: All interactive elements focusable, logical tab order
- Screen reader support: Semantic HTML, ARIA labels, alt text for images
- Motion: Reduce motion preference respected (`prefers-reduced-motion`)
- Responsive: Works on 320px width devices

**Testing Tools**:
- Lighthouse CI (automated performance/SEO/accessibility audits)
- axe DevTools (accessibility scanning)
- Playwright (E2E testing, cross-browser)
- React Testing Library (unit/component tests)

---

## Phase 1 Outputs Summary

✅ **plan.md** (this file): Technical context, architecture decisions, component hierarchy, i18n strategy, SEO approach
📝 **research.md** (TBD): None needed (no open technical questions)
📝 **data-model.md** (TBD): Static content configuration, no database entities
📝 **contracts/** (TBD): Landing page routing, CTA navigation, language API
📝 **quickstart.md** (TBD): Developer setup, environment variables, running locally, build commands

---

## Next Phase: `/sp.tasks`

Once this plan is reviewed and approved, the next step is to generate a tasks.md file using `/sp.tasks` command. This will break down the implementation into specific, testable tasks with dependencies, estimated complexity, and acceptance criteria.

**Expected task areas** (preview):
- T1-T5: Component development (HeroSection, FeaturesSection, etc.)
- T6-T8: i18n setup and translation integration
- T9-T10: SEO metadata and structured data
- T11-T13: Responsive design and accessibility testing
- T14-T15: E2E and performance testing
- T16: Deployment and verification

---

## Architecture Decision Record (ADR)

### Decision: Static Content Model vs. CMS

**Context**: Landing page content needs to be easily updateable but also language-aware and performant.

**Options**:
1. **Static JSON files** (chosen): Content in i18n JSON files, rebuilt on each change, minimal runtime overhead, fully typed.
2. **Headless CMS** (Sanity, Contentful): More flexibility for non-developers, but adds external dependency, higher latency, increased cost.
3. **Database** (PostgreSQL): Over-engineered for static marketing content; unnecessary query overhead.

**Decision**: Static JSON files with i18n framework.

**Rationale**: Aligns with Constitution principle of stateless services; keeps landing page decoupled from backend; simple to translate; fast performance; version-controlled content.

**Trade-offs**: Less flexible for content teams without code access; requires rebuild/redeploy for content updates. Mitigated by clear documentation and simple JSON structure.

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Translation quality/completeness (Urdu, Roman Urdu) | Medium | Hire professional translator; validate with native speakers; include glossary for technical terms |
| Performance on mobile networks | High | Lazy load images; aggressive code splitting; measure with Lighthouse CI on 4G throttling |
| SEO effectiveness (new domain/page) | Medium | Implement proper meta tags, Schema.org; submit to Google Search Console; monitor rankings monthly |
| Accessibility gaps not caught in testing | Low | Use automated tools (axe); manual screen reader testing; WCAG AA self-assessment |
| Conversion rate lower than 15-20% baseline | Medium | A/B test CTA placement, copy, colors; analyze analytics; iterate based on user feedback |
| Browser compatibility issues | Low | Test in modern browsers (Chrome, Firefox, Safari, Edge); use graceful degradation for unsupported features |
