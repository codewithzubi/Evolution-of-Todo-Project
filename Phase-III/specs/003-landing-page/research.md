# Research & Architectural Decisions: Public Landing Page

**Feature**: 003-landing-page
**Date**: 2026-02-09
**Status**: Phase 0 Complete

## Overview

This document captures research findings and architectural decisions for implementing a high-performance, conversion-optimized landing page using Next.js 16.1.6 Server Components.

## Key Decisions

### 1. Phone Mockup Implementation Strategy

**Decision**: Use CSS-only device frame with static image/screenshot for dashboard preview

**Rationale**:
- Performance: CSS device frame is lightweight (<5KB) vs SVG mockup libraries (50-100KB)
- Flexibility: Easy to update dashboard screenshot without code changes
- Core Web Vitals: Static image with proper optimization (WebP, lazy loading) ensures fast LCP
- Maintenance: No external dependencies for device frame rendering

**Alternatives Considered**:
- **Rejected: react-device-frameset library** - Adds 80KB bundle size, overkill for static mockup
- **Rejected: Interactive iframe embed** - Violates performance constraints (<2s load time), adds complexity
- **Rejected: Pure SVG device frame** - More complex to maintain, no significant benefit over CSS

**Implementation Approach**:
- CSS device frame with border-radius, box-shadow, and notch using pseudo-elements
- Next.js Image component for dashboard screenshot (automatic WebP conversion, lazy loading)
- Responsive scaling using CSS clamp() for fluid sizing across breakpoints

---

### 2. Animation Strategy

**Decision**: CSS animations only (no JavaScript animation libraries)

**Rationale**:
- Performance: CSS animations are GPU-accelerated, don't block main thread
- Bundle size: Zero JavaScript overhead (Framer Motion adds ~60KB)
- Core Web Vitals: No layout shift (CLS), no interaction delay (FID)
- Simplicity: Fade-in and slide-up animations achievable with pure CSS

**Alternatives Considered**:
- **Rejected: Framer Motion** - Excellent library but adds 60KB+ bundle size, overkill for simple fade-ins
- **Rejected: GSAP** - Professional-grade but unnecessary for landing page animations
- **Rejected: Intersection Observer + JS** - More complex than CSS, no benefit for simple animations

**Implementation Approach**:
- CSS `@keyframes` for fade-in and slide-up animations
- `animation-delay` for staggered entrance effects
- `prefers-reduced-motion` media query for accessibility
- Tailwind CSS animation utilities where applicable

---

### 3. Performance Optimization for Core Web Vitals

**Decision**: Multi-layered optimization strategy targeting Lighthouse 90+ scores

**Rationale**:
- Success criteria requires LCP <2.5s, FID <100ms, CLS <0.1
- Next.js 16.1.6 provides built-in optimizations (Image component, font optimization)
- Static page enables aggressive caching and CDN delivery

**Optimization Techniques**:

**LCP (Largest Contentful Paint) <2.5s**:
- Hero headline uses system font stack (no web font download delay)
- Phone mockup image: Next.js Image with priority flag, WebP format, proper sizing
- Critical CSS inlined in <head>
- No render-blocking resources above the fold

**FID (First Input Delay) <100ms**:
- Server Components by default (zero client-side JavaScript for static content)
- CTA buttons use native <Link> (no JavaScript event handlers)
- No heavy JavaScript libraries loaded

**CLS (Cumulative Layout Shift) <0.1**:
- Explicit width/height on all images (phone mockup, feature icons)
- No dynamic content injection after initial render
- Font loading with font-display: swap and size-adjust
- Reserved space for all above-the-fold content

**Alternatives Considered**:
- **Rejected: Client-side rendering** - Slower initial load, worse Core Web Vitals
- **Rejected: Static Site Generation (SSG)** - Server Components provide same benefits with more flexibility

---

### 4. SEO Optimization for Next.js App Router

**Decision**: Use Next.js 16.1.6 Metadata API with comprehensive meta tags

**Rationale**:
- App Router provides type-safe metadata generation
- Success criteria requires Lighthouse SEO score of 100
- Proper meta tags improve social sharing and search visibility

**Implementation Approach**:
- Export `metadata` object from page.tsx with title, description, Open Graph tags
- Semantic HTML5 elements (<header>, <section>, <main>)
- Structured data (JSON-LD) for organization/website schema
- Canonical URL, robots meta tag, viewport meta tag
- Alt text on all images (phone mockup, feature icons)

**Alternatives Considered**:
- **Rejected: react-helmet** - Not compatible with App Router, unnecessary
- **Rejected: Manual <head> manipulation** - Metadata API is type-safe and recommended

---

### 5. Responsive Design Pattern for Hero Section

**Decision**: CSS Grid with mobile-first breakpoints (Tailwind responsive utilities)

**Rationale**:
- Spec requires: desktop (headline left, mockup right), mobile (stacked vertical)
- CSS Grid provides clean two-column layout with automatic stacking
- Tailwind breakpoints align with spec (mobile <768px, tablet 768-1024px, desktop >1024px)

**Implementation Approach**:
- Mobile: Single column, headline → CTA → phone mockup (vertical stack)
- Tablet: Same as mobile or early transition to two-column
- Desktop: Two-column grid (60/40 split), headline left, mockup right
- Fluid typography using clamp() for headline sizing (48px-72px)
- Container max-width: 1280px with horizontal padding

**Alternatives Considered**:
- **Rejected: Flexbox** - Grid is more semantic for two-dimensional layout
- **Rejected: Absolute positioning** - Fragile, accessibility issues, hard to maintain

---

### 6. Feature Cards Layout Strategy

**Decision**: CSS Grid with responsive column count (4 → 2 → 1)

**Rationale**:
- Spec requires: 4 columns desktop, 2 columns tablet, 1 column mobile
- CSS Grid auto-fit/auto-fill provides automatic responsive behavior
- Equal-height cards without JavaScript

**Implementation Approach**:
- Desktop: `grid-template-columns: repeat(4, 1fr)` or `repeat(auto-fit, minmax(250px, 1fr))`
- Tablet: `md:grid-cols-2`
- Mobile: `grid-cols-1` (default)
- Gap: 24px (1.5rem) for visual breathing room
- Card hover effects: CSS transform + box-shadow transition

**Alternatives Considered**:
- **Rejected: Flexbox with flex-wrap** - Less predictable column behavior
- **Rejected: Manual breakpoint management** - Grid auto-fit is more maintainable

---

### 7. Icon Strategy

**Decision**: Lucide React icons imported individually (tree-shakeable)

**Rationale**:
- Constitution requires Lucide Icons for consistency
- Individual imports ensure only used icons are bundled
- React components integrate seamlessly with Next.js

**Implementation Approach**:
- Import specific icons: `import { CheckCircle, Filter, Lock, Globe } from 'lucide-react'`
- Feature cards: CheckCircle (Simple Task Management), Filter (Smart Filtering), Lock (Secure & Private), Globe (Always Accessible)
- Icon size: 24px (1.5rem) for feature cards
- Color: Accent color (blue/purple) or white depending on context

**Alternatives Considered**:
- **Rejected: SVG sprite sheet** - More complex setup, no benefit over tree-shaking
- **Rejected: Icon font** - Accessibility issues, flash of unstyled content

---

### 8. Color Scheme & Design Tokens

**Decision**: Tailwind CSS custom theme extending default dark mode colors

**Rationale**:
- Spec requires dark mode with specific color palette
- Tailwind provides excellent dark mode utilities
- Custom theme ensures consistency across components

**Color Palette**:
- Background: `#0a0a0a` (zinc-950), `#171717` (neutral-900)
- Text: `#ffffff` (white), `#fafafa` (neutral-50)
- Accent: `#3b82f6` (blue-500) or `#8b5cf6` (purple-500) for CTA buttons
- Gradient: `from-zinc-950 via-neutral-900 to-zinc-950` for hero background

**Implementation Approach**:
- Extend Tailwind config with custom colors if needed
- Use semantic class names: `bg-background`, `text-foreground`, `text-accent`
- shadcn/ui components already provide dark mode support

**Alternatives Considered**:
- **Rejected: CSS variables only** - Tailwind utilities provide better DX
- **Rejected: Styled-components** - Adds runtime overhead, not needed for static page

---

## Technology Stack Summary

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| Framework | Next.js | 16.1.6 | Constitution-locked, App Router for Server Components |
| Styling | Tailwind CSS | Latest | Constitution-approved, utility-first responsive design |
| Icons | Lucide React | Latest | Constitution-required, tree-shakeable React components |
| Components | shadcn/ui | Latest | Constitution-approved, Button and Card components |
| Typography | System font stack | N/A | Zero latency, excellent fallback (Inter/Geist if available) |
| Images | Next.js Image | Built-in | Automatic optimization, WebP conversion, lazy loading |
| Animations | CSS @keyframes | Native | Zero bundle size, GPU-accelerated, accessible |
| Testing | Vitest + Playwright | Latest | Unit tests for components, E2E for navigation |

---

## Performance Budget

| Metric | Target | Strategy |
|--------|--------|----------|
| Page Load Time | <2s | Server Components, optimized images, minimal JS |
| LCP | <2.5s | Priority image loading, system fonts, critical CSS |
| FID | <100ms | Minimal client-side JS, native browser interactions |
| CLS | <0.1 | Explicit dimensions, no dynamic content injection |
| Bundle Size (JS) | <50KB | Server Components, tree-shaking, no animation libraries |
| Lighthouse Performance | 90+ | All optimizations combined |
| Lighthouse Accessibility | 95+ | Semantic HTML, alt text, ARIA labels, keyboard nav |
| Lighthouse SEO | 100 | Metadata API, structured data, semantic HTML |

---

## Risk Mitigation

### Risk 1: Phone Mockup Image Size Impacts LCP
**Mitigation**:
- Use Next.js Image with priority flag
- Optimize source image to <100KB (WebP format)
- Provide multiple sizes for responsive loading
- Consider CSS-only mockup if image optimization insufficient

### Risk 2: Animations Cause Layout Shift (CLS)
**Mitigation**:
- Use transform and opacity only (don't animate width/height/margin)
- Reserve space for all content before animation starts
- Test with Lighthouse CLS measurement

### Risk 3: Feature Cards Not Accessible
**Mitigation**:
- Use semantic HTML (article, h3, p)
- Ensure sufficient color contrast (WCAG AA)
- Keyboard navigation for hover states
- Screen reader testing

---

## Open Questions

None - all technical decisions resolved. Landing page is straightforward static implementation with well-established patterns.

---

## Next Steps

Proceed to Phase 1:
1. ~~Generate data-model.md~~ (N/A - no database entities for static page)
2. ~~Generate contracts/~~ (N/A - no API endpoints for frontend-only page)
3. Generate quickstart.md (test scenarios for landing page)
4. Update agent context (CLAUDE.md)
5. Re-evaluate Constitution Check (expected: still PASS)
