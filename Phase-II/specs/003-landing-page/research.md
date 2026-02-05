# Research & Technical Decisions: Landing Page

**Phase**: Phase 0 - Research & Unknowns Resolution
**Date**: 2026-02-04
**Status**: ✅ COMPLETE (No unresolved clarifications)

---

## Executive Summary

All technical decisions for the landing page implementation have been made. No blocking research questions remain. The plan leverages existing project technologies (Next.js 16+, React 18, Tailwind CSS) with targeted additions (next-intl for i18n, Playwright for E2E testing).

---

## Research Decisions

### 1. Internationalization (i18n) Library

**Decision**: `next-intl`

**Rationale**:
- **Next.js native**: Built for Next.js 13+ App Router (perfect match for our setup)
- **TypeScript support**: Full type safety for translation keys
- **SSR/SSG compatible**: Works with Next.js static exports and server rendering
- **Middleware support**: Can handle URL-based language routing (`/en`, `/ur`, `/ur-roman`)
- **Simple setup**: Minimal configuration, straightforward JSON translation files
- **Community**: Well-maintained, used by many SaaS companies
- **Performance**: Negligible runtime overhead; translations pre-compiled

**Alternatives Considered**:
- **i18next**: More heavyweight, overkill for static landing page; better for larger apps with dynamic translations
- **react-i18next**: Requires additional setup; not Next.js optimized
- **Custom solution**: Would require maintaining own localization logic; reinventing the wheel

**Implementation Approach**:
1. Install `next-intl` package
2. Configure in `next.config.js`
3. Create middleware for language routing
4. Add translation JSON files for en, ur, ur-roman
5. Wrap landing page with `useTranslations()` hook

---

### 2. Styling & Component Approach

**Decision**: Tailwind CSS (existing) + semantic HTML components

**Rationale**:
- **Already in project**: No new dependency; consistent with existing codebase
- **Mobile-first**: Built-in responsive design system
- **Performance**: Minimal CSS output with PurgeCSS
- **Developer experience**: Utility-first approach enables rapid prototyping
- **Accessibility**: Works well with semantic HTML for screen readers

**Alternatives Considered**:
- **Styled Components / Emotion**: CSS-in-JS solutions; add runtime overhead; unnecessary for static content
- **Bootstrap**: Too opinionated; overkill for landing page
- **Material-UI**: Over-engineered for this use case; conflicts with existing brand
- **Custom CSS**: Duplicates work; maintenance burden

**Component Patterns**:
- Use existing button, card, heading components from task UI
- Create landing-specific section wrappers (HeroSection, FeaturesSection, etc.)
- Leverage Tailwind's responsive utilities for mobile/tablet/desktop

---

### 3. SEO & Metadata Management

**Decision**: Next.js `generateMetadata()` API + Schema.org structured data

**Rationale**:
- **Next.js 13.2+**: Built-in metadata API (no external dependency)
- **Dynamic per-page**: Can customize meta tags for each section if needed later
- **Schema.org**: Industry standard for search engine understanding
- **Future-proof**: Supports Open Graph, Twitter Cards, JSON-LD

**Alternatives Considered**:
- **Next.js Head component**: Older approach; replaced by metadata API in Next.js 13+
- **react-helmet**: Not recommended for Next.js 13+ App Router
- **SEO libraries (Yoast, SemRush)**: Unnecessary for simple landing page

**Structured Data**:
- SoftwareApplication schema (for Google rich snippets)
- Organization schema (for company branding)
- Breadcrumb schema (if multi-level sections)

---

### 4. Image Optimization

**Decision**: Next.js `<Image>` component + modern formats (WebP)

**Rationale**:
- **Automatic optimization**: AVIF/WebP with fallbacks, responsive srcsets
- **Lazy loading**: Images below the fold don't load until visible
- **Performance**: Reduces LCP, improves Core Web Vitals
- **Built-in**: No external library needed

**Alternatives Considered**:
- **Plain `<img>` tags**: Manual optimization; no lazy loading; slower
- **Third-party service (Cloudinary)**: Over-engineered; adds external dependency and cost
- **Manual srcsets**: Maintenance burden; error-prone

**Image Sources**:
- Hero background: High-quality illustration or solid color + gradient
- Feature icons: SVG or small PNG (256x256)
- App screenshots: PNG/JPG optimized to <100KB each
- Logos: SVG for infinite scaling

---

### 5. Testing Strategy

**Decision**: Playwright (E2E) + React Testing Library (unit/component) + Lighthouse CI

**Rationale**:
- **Playwright**: Cross-browser E2E testing (Chrome, Firefox, Safari, Edge); excellent for conversion funnels
- **React Testing Library**: Encourages testing user interactions, not implementation details
- **Lighthouse CI**: Automated performance/SEO/accessibility audits on each build
- **No flakiness**: All tools are stable and widely used

**Alternatives Considered**:
- **Cypress**: Good for E2E, but slower than Playwright; overkill for landing page
- **Jest alone**: Only tests logic, not user interactions
- **Manual testing**: Not scalable; misses regressions

**Test Coverage**:
- E2E: Hero CTA → signup flow, language switching, responsive behavior, accessibility
- Component: Each section renders correctly, translations apply
- Performance: Lighthouse scores maintained above thresholds
- Accessibility: WCAG AA compliance (axe-core scanning)

---

### 6. Animation & Interactivity

**Decision**: CSS transitions (Tailwind) + optional Framer Motion for advanced animations (post-MVP)

**Rationale**:
- **CSS transitions**: Zero JavaScript overhead; smooth, performant; sufficient for basic effects
- **Framer Motion**: Optional library for scroll effects, parallax, complex animations (can add later)
- **User preference**: Respect `prefers-reduced-motion` for accessibility

**Alternatives Considered**:
- **GreenSock (GSAP)**: Powerful but overkill for landing page; adds 100KB to bundle
- **Animate.css**: Library; not recommended for Next.js
- **Heavy animations**: Risk of poor performance on mobile; violates performance budget

**Animations (MVP)**:
- Hover effects on buttons/cards (CSS)
- Smooth scroll to sections (CSS scroll-behavior)
- Fade-in sections on scroll (optional; Framer Motion if time permits)

---

### 7. Accessibility Compliance

**Decision**: WCAG AA standard (Level AA) - no exceptions

**Rationale**:
- **Legal/ethical**: Ensures landing page is accessible to users with disabilities
- **Business**: Expands addressable market; improves SEO (Google rewards accessibility)
- **Spec requirement**: Landing page spec requires WCAG AA compliance

**Compliance Checklist**:
- ✅ Color contrast 4.5:1 (normal), 3:1 (large text)
- ✅ Keyboard navigation (no click-only interactions)
- ✅ Semantic HTML (`<main>`, `<section>`, `<article>`, proper heading hierarchy)
- ✅ ARIA labels for non-semantic elements
- ✅ Alt text for all images
- ✅ Form labels (`<label>` associated with inputs)
- ✅ No time-dependent content
- ✅ Respects `prefers-reduced-motion` media query

**Testing Tools**:
- axe-core (automated accessibility scanning)
- NVDA/JAWS (screen reader manual testing)
- Chrome DevTools Accessibility panel
- WAVE Web Accessibility Evaluation Tool

---

### 8. Responsive Design & Mobile-First Approach

**Decision**: Mobile-first with Tailwind breakpoints (sm, md, lg, xl)

**Rationale**:
- **Mobile majority**: 70%+ of web traffic is mobile; optimizing for mobile ensures good experience for majority
- **Tailwind built-in**: Breakpoints are well-designed; no custom media queries needed
- **Performance**: Progressive enhancement; mobile users get essential content first
- **Spec requirement**: Landing page must work on 320px - 1920px

**Breakpoints**:
- Default (mobile): 320px - 639px
- `sm`: 640px (tablets)
- `md`: 768px (larger tablets)
- `lg`: 1024px (desktops)
- `xl`: 1280px (large desktops)

**Mobile Optimizations**:
- Single-column layout on mobile
- Touch-friendly button sizes (48px minimum)
- Large text (16px minimum for readability)
- Avoid horizontal scrolling
- Prioritize above-the-fold content

---

### 9. Performance Budgets & Targets

**Decision**: < 2 seconds load time, Lighthouse 90+ scores

**Rationale**:
- **User expectations**: 2-3 seconds is perceived as instant; >5s increases bounce rate
- **SEO impact**: Core Web Vitals are Google ranking factors
- **Spec requirement**: Landing page spec requires <2s load time

**Performance Targets**:
| Metric | Target | Justification |
|--------|--------|---------------|
| LCP (Largest Contentful Paint) | <2.5s | Hero content visible within 2.5s |
| FID (First Input Delay) | <100ms | CTAs responsive to clicks |
| CLS (Cumulative Layout Shift) | <0.1 | No layout jumps during load |
| Page Size | <100KB (JS + CSS) | Fast on 4G networks |
| Lighthouse Performance | 90+ | Industry best practice |
| Lighthouse SEO | 90+ | Proper metadata, mobile-friendly |
| Lighthouse Accessibility | 90+ | WCAG AA compliance |

**Optimizations**:
- Lazy load images below the fold
- Code split sections (if needed)
- Minify CSS/JS
- Use modern image formats (WebP, AVIF)
- Cache headers for static assets
- CDN for image delivery

---

### 10. Multi-Language Translation Workflow

**Decision**: Professional translation for Urdu and Roman Urdu; validate with native speakers

**Rationale**:
- **Quality**: Professional translators ensure culturally appropriate, idiomatic language
- **Native speakers**: Validate translations for correctness and nuance
- **Glossary**: Technical terms (e.g., "priority", "tags") translated consistently

**Workflow**:
1. Write master copy in English (clear, simple, concise)
2. Translate to Urdu (Nastaliq/Naskh script) with professional translator
3. Translate to Roman Urdu (Latin transliteration) with professional translator or community expert
4. Validate with 2-3 native speakers
5. Add translations to JSON files
6. Commit to git with translation metadata

**Common Pitfalls to Avoid**:
- Literal word-for-word translation (leads to unnatural phrasing)
- Using Google Translate without validation (can miss nuance, cultural context)
- Inconsistent terminology (maintain glossary)
- Not testing on RTL rendering (Urdu is RTL; need to validate layout)

---

### 11. Analytics & Tracking (Future, Post-MVP)

**Decision**: Optional Google Analytics; not required for MVP

**Rationale**:
- **Landing page MVP goal**: Drive signups; basic pageviews sufficient
- **Can be added later**: GA is non-blocking; add after MVP launch if needed
- **Privacy**: Minimize tracking on landing page; collect only what's needed

**Metrics to Track (if GA added)**:
- Sessions / Unique Visitors
- CTA click-through rate (conversion funnel)
- Time on page
- Bounce rate
- Language selection distribution
- Device/browser breakdown

**Implementation**: Google Tag Manager (GTM) for easier management; defer to post-MVP phase.

---

## Decision Matrix

| Decision | Choice | Confidence | Revisit Date |
|----------|--------|-----------|--------------|
| i18n Library | next-intl | 95% | Post-MVP if requirements change |
| Styling | Tailwind CSS | 100% (existing) | N/A |
| SEO | Next.js metadata API | 95% | Post-MVP if we add CMS |
| Images | Next.js Image component | 95% | N/A |
| Testing | Playwright + RTL + Lighthouse | 95% | N/A |
| Animations | CSS + optional Framer Motion | 85% | Post-MVP |
| Accessibility | WCAG AA | 100% (spec requirement) | N/A |
| Responsive | Mobile-first, Tailwind | 100% | N/A |
| Performance Target | <2s, Lighthouse 90+ | 90% | Post-MVP (may adjust based on metrics) |
| Translations | Professional + native validation | 95% | N/A |

---

## Conclusion

All technical decisions are defensible, aligned with project principles, and leverage existing technologies. No blocking research questions remain. Ready to proceed with `/sp.tasks` to generate implementation tasks.

**Next**: `/sp.tasks` to break down feature into specific, testable tasks with dependencies and complexity estimates.
