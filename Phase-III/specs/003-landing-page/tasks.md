# Tasks: Public Landing Page

**Input**: Design documents from `/specs/003-landing-page/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md
**Branch**: `003-landing-page` | **Date**: 2026-02-04

**Notes**:
- Tasks are organized by user story (US1-US6) to enable independent implementation
- Tests are OPTIONAL (not explicitly requested in spec, included for best practices)
- All tasks reference Task IDs, priority (P1/P2), user story, and exact file paths

---

## Format: `[ID] [P?] [Story] Description with exact file path`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story (US1-US6) from spec.md
- **File paths**: Exact `frontend/src/...` paths for implementation

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and i18n foundation (blocking prerequisite for all user stories)

- [ ] T001 Install next-intl package and add to frontend/package.json dependencies
- [ ] T002 Create i18n configuration in frontend/src/i18n/config.ts with language constants
- [ ] T003 Create i18n middleware in frontend/src/i18n/middleware.ts for URL-based language routing
- [ ] T004 [P] Create translation JSON files: frontend/src/i18n/locales/en.json (English master)
- [ ] T005 [P] Create translation JSON files: frontend/src/i18n/locales/ur.json (Urdu translations)
- [ ] T006 [P] Create translation JSON files: frontend/src/i18n/locales/ur-roman.json (Roman Urdu translations)
- [ ] T007 Create translation helper/hook in frontend/src/hooks/useLanguage.ts for component integration
- [ ] T008 Create landing page types in frontend/src/types/landing.ts (LandingPageProps, FeatureItem, etc.)
- [ ] T009 Create landing page route structure: frontend/src/app/(landing)/ directory with layout.tsx
- [ ] T010 [P] Create public image directories: frontend/public/images/{hero-bg,feature-icons,app-screenshots,illustrations}
- [ ] T011 Create base utility components: frontend/src/components/landing/index.ts (barrel export)

**Checkpoint**: i18n framework configured, routes set up, ready for component implementation

---

## Phase 2: Foundational (Core Components & Styling)

**Purpose**: Reusable components and styling that multiple stories depend on

**⚠️ CRITICAL**: Must complete before user story components can be built

- [ ] T012 [P] Create LandingHeader component in frontend/src/components/landing/LandingHeader.tsx with logo and nav
- [ ] T013 [P] Create LanguageSelector component in frontend/src/components/landing/LanguageSelector.tsx with en/ur/ur-roman toggle
- [ ] T014 [P] Create Footer component in frontend/src/components/landing/Footer.tsx with links (privacy, terms, GitHub, social)
- [ ] T015 [P] Create reusable Button component wrapper in frontend/src/components/landing/Button.tsx (primary, secondary variants)
- [ ] T016 [P] Create reusable SectionHeading component in frontend/src/components/landing/SectionHeading.tsx
- [ ] T017 [P] Create reusable Card component wrapper in frontend/src/components/landing/Card.tsx
- [ ] T018 [P] Create CTA Button component in frontend/src/components/landing/CTAButton.tsx with link to signup
- [ ] T019 Create landing page layout: frontend/src/app/(landing)/layout.tsx (wrapper with header and footer)
- [ ] T020 Create SEO metadata helper: frontend/src/app/(landing)/metadata.ts with generateMetadata() function
- [ ] T021 Create landing page root component: frontend/src/app/(landing)/page.tsx (assembles all sections)
- [ ] T022 Add Tailwind CSS styling for landing page sections (colors, typography, spacing, responsive breakpoints)
- [ ] T023 Create Next.js Image optimization setup for hero-bg.png and screenshot images

**Checkpoint**: Foundation ready - all section components can now be built independently

---

## Phase 3: User Story 1 - Discover and Understand the App (Priority: P1) 🎯 MVP

**Goal**: New visitors quickly understand what the app does, what problems it solves, and that it's free to start. Must display within 5 seconds with clear headline, subheadline, features, and value proposition.

**Independent Test**: Visit landing page, verify within 5 seconds: (1) understand app purpose, (2) understand problem solved, (3) see "free to start" message. Acceptance scenarios in spec.md#US1.

### Implementation for User Story 1

- [ ] T024 [P] [US1] Create HeroSection component in frontend/src/components/landing/HeroSection.tsx with headline, subheadline, CTA, trust line
- [ ] T025 [P] [US1] Create ProblemSection component in frontend/src/components/landing/ProblemSection.tsx listing 3-4 pain points (forgotten deadlines, scattered tasks, unclear priorities)
- [ ] T026 [P] [US1] Create SolutionSection component in frontend/src/components/landing/SolutionSection.tsx explaining clean dashboard and ease of task creation
- [ ] T027 [P] [US1] Create FeaturesSection component in frontend/src/components/landing/FeaturesSection.tsx displaying 5-6 core features (task creation, due dates, priority, tags, multilingual, AI-ready)
- [ ] T028 [US1] Add Hero section translations to frontend/src/i18n/locales/en.json (headline, subheadline, CTA, trustline) - [Task]: T028, [From]: specs/003-landing-page/spec.md#FR-002
- [ ] T029 [US1] Add Problem section translations to frontend/src/i18n/locales/en.json (title, 3-4 pain points) - [Task]: T029, [From]: specs/003-landing-page/spec.md#FR-003
- [ ] T030 [US1] Add Solution section translations to frontend/src/i18n/locales/en.json (content about clean dashboard and ease) - [Task]: T030, [From]: specs/003-landing-page/spec.md#FR-004
- [ ] T031 [US1] Add Features section translations to frontend/src/i18n/locales/en.json (5-6 features with descriptions) - [Task]: T031, [From]: specs/003-landing-page/spec.md#FR-005
- [ ] T032 [US1] Integrate Hero, Problem, Solution, Features sections into frontend/src/app/(landing)/page.tsx
- [ ] T033 [US1] Add responsive design for Hero section on mobile (320px), tablet (768px), desktop (1920px+)
- [ ] T034 [US1] Add responsive design for Problem/Solution/Features sections on all breakpoints
- [ ] T035 [US1] Verify color contrast meets WCAG AA (4.5:1 for normal text, 3:1 for large text)
- [ ] T036 [US1] Add semantic HTML and ARIA labels to Hero/Problem/Solution/Features sections
- [ ] T037 [US1] Test Hero section loads in <2.5s LCP on standard 4G (measure with Lighthouse)
- [ ] T038 [US1] Create component tests for HeroSection in frontend/tests/landing/component/HeroSection.test.tsx
- [ ] T039 [US1] Create component tests for FeaturesSection in frontend/tests/landing/component/FeaturesSection.test.tsx

**Checkpoint**: User Story 1 complete - visitors understand app value, can see features, <2.5s load time

---

## Phase 4: User Story 2 - Convert from Visitor to User (Priority: P1)

**Goal**: Convinced visitors can easily sign up with clear CTAs, no friction, and confidence (no credit card required).

**Independent Test**: Count CTAs on page (hero + features + footer), verify all lead to /auth/signup, verify "No credit card required" message visible. Acceptance scenarios in spec.md#US2.

### Implementation for User Story 2

- [ ] T040 [P] [US2] Create FinalCTASection component in frontend/src/components/landing/FinalCTASection.tsx with motivational message and "Start Managing Tasks Now" CTA
- [ ] T041 [US2] Add multiple CTA buttons to HeroSection (primary "Get Started Free" above fold)
- [ ] T042 [US2] Add secondary CTA buttons to FeaturesSection (each feature card can have CTA)
- [ ] T043 [US2] Add FinalCTASection CTA button to landing page above footer
- [ ] T044 [US2] Add trust line "No credit card required" to hero section and final CTA section
- [ ] T045 [US2] Add FinalCTA translations to frontend/src/i18n/locales/en.json (motivational message, CTA copy) - [Task]: T045, [From]: specs/003-landing-page/spec.md#FR-010
- [ ] T046 [US2] Verify all CTA buttons navigate to /auth/signup endpoint correctly
- [ ] T047 [US2] Test CTA button styling (prominent, accessible, clear copy: "Get Started Free", "Start Managing Tasks Now")
- [ ] T048 [US2] Add responsive CTA button sizing on mobile (48px minimum height for touch targets)
- [ ] T049 [US2] Verify CTA button hover/focus states for accessibility and UX
- [ ] T050 [US2] Create E2E test for conversion flow in frontend/tests/landing/e2e/conversion.spec.ts (hero → CTA → signup page)
- [ ] T051 [US2] Measure CTA click-through rate setup (baseline for 15-20% target)

**Checkpoint**: User Story 2 complete - clear CTAs throughout page, conversion flow tested, <2.5s load maintained

---

## Phase 5: User Story 3 - Choose the App Over Alternatives (Priority: P2)

**Goal**: Competitive differentiation: visitors see target personas, unique features (multilingual, clean UI, free-to-start), and understand advantages.

**Independent Test**: Review "Who Is This For" section (identifies students, freelancers, developers, small teams), verify unique features highlighted (multilingual, clean UI, free-to-start). Acceptance scenarios in spec.md#US3.

### Implementation for User Story 3

- [ ] T052 [P] [US3] Create TargetAudienceSection component in frontend/src/components/landing/TargetAudienceSection.tsx with 4 persona cards (students, freelancers, developers, small teams)
- [ ] T053 [US3] Add target audience translations to frontend/src/i18n/locales/en.json (persona titles, descriptions) - [Task]: T053, [From]: specs/003-landing-page/spec.md#FR-008
- [ ] T054 [US3] Integrate TargetAudienceSection into frontend/src/app/(landing)/page.tsx
- [ ] T055 [US3] Verify unique features are highlighted throughout page (multilingual support, clean UI, free-to-start, easy task creation)
- [ ] T056 [US3] Add responsive design for TargetAudienceSection (persona cards stack on mobile, grid on desktop)
- [ ] T057 [US3] Add semantic HTML and ARIA labels to persona cards
- [ ] T058 [US3] Create component tests for TargetAudienceSection in frontend/tests/landing/component/TargetAudienceSection.test.tsx
- [ ] T059 [US3] Verify footer links functional (privacy, terms, GitHub, contact) in frontend/src/components/landing/Footer.tsx

**Checkpoint**: User Story 3 complete - target audience identified, differentiation clear

---

## Phase 6: User Story 4 - Access the App if Already Registered (Priority: P2)

**Goal**: Returning users can access login quickly from header/footer without friction.

**Independent Test**: Verify "Log In" and "Sign Up" links visible in header and footer, both functional, lead to /auth/login. Acceptance scenarios in spec.md#US4.

### Implementation for User Story 4

- [ ] T060 [P] [US4] Add "Log In" link to LandingHeader component in frontend/src/components/landing/LandingHeader.tsx
- [ ] T061 [P] [US4] Add "Sign Up" link to LandingHeader component in frontend/src/components/landing/LandingHeader.tsx
- [ ] T062 [US4] Add "Log In" and "Sign Up" links to Footer component in frontend/src/components/landing/Footer.tsx
- [ ] T063 [US4] Verify header login/signup links navigate to /auth/login and /auth/signup respectively
- [ ] T064 [US4] Verify footer login/signup links navigate correctly
- [ ] T065 [US4] Add responsive header navigation (hamburger menu on mobile, full nav on desktop) for login/signup links
- [ ] T066 [US4] Test keyboard navigation for header/footer links (Tab, Enter, focus visible)
- [ ] T067 [US4] Add ARIA labels to header/footer navigation links for screen readers
- [ ] T068 [US4] Create E2E test for returning user access in frontend/tests/landing/e2e/landing.spec.ts (verify header/footer links)

**Checkpoint**: User Story 4 complete - returning users can quickly access login

---

## Phase 7: User Story 5 - Explore Features and Pricing (Priority: P3)

**Goal**: Prospects can review detailed features (5-6 list), pricing (free tier details, no credit card), and app preview (screenshots).

**Independent Test**: Verify "Key Features" section has 5-6 features with descriptions, "Pricing" section explains free tier and "no credit card", "App Preview" shows screenshots/modal descriptions. Acceptance scenarios in spec.md#US5.

### Implementation for User Story 5

- [ ] T069 [P] [US5] Create HowItWorksSection component in frontend/src/components/landing/HowItWorksSection.tsx with 3-step flow (Sign up → Create tasks → Track & complete)
- [ ] T070 [P] [US5] Create PreviewSection component in frontend/src/components/landing/PreviewSection.tsx displaying app screenshots (dashboard, task list, create-task modal)
- [ ] T071 [P] [US5] Create PricingSection component in frontend/src/components/landing/PricingSection.tsx emphasizing "Free to start", "No credit card required", "Optional upgrade later"
- [ ] T072 [US5] Add How It Works translations to frontend/src/i18n/locales/en.json (3 steps with descriptions) - [Task]: T072, [From]: specs/003-landing-page/spec.md#FR-006
- [ ] T073 [US5] Add App Preview translations to frontend/src/i18n/locales/en.json (description of screenshots, feature highlights) - [Task]: T073, [From]: specs/003-landing-page/spec.md#FR-007
- [ ] T074 [US5] Add Pricing translations to frontend/src/i18n/locales/en.json ("Free to start", "No credit card required", free tier details) - [Task]: T074, [From]: specs/003-landing-page/spec.md#FR-009
- [ ] T075 [US5] Integrate HowItWorks, Preview, Pricing sections into frontend/src/app/(landing)/page.tsx
- [ ] T076 [US5] Add responsive design for How It Works section (steps in column on mobile, row on desktop)
- [ ] T077 [US5] Add responsive design for Preview section (screenshots stack on mobile, side-by-side on desktop)
- [ ] T078 [US5] Add responsive design for Pricing section (card layout responsive)
- [ ] T079 [US5] Optimize app screenshot images (lazy load, next/image, WebP format, <100KB total per screenshot)
- [ ] T080 [US5] Add semantic HTML and ARIA labels to How It Works/Preview/Pricing sections
- [ ] T081 [US5] Create component tests for HowItWorksSection in frontend/tests/landing/component/HowItWorksSection.test.tsx
- [ ] T082 [US5] Create component tests for PreviewSection in frontend/tests/landing/component/PreviewSection.test.tsx
- [ ] T083 [US5] Create component tests for PricingSection in frontend/tests/landing/component/PricingSection.test.tsx

**Checkpoint**: User Story 5 complete - detailed features, pricing, and app preview visible

---

## Phase 8: User Story 6 - Access in Multiple Languages (Priority: P2)

**Goal**: Visitors can switch between English, Urdu, and Roman Urdu. All content translated, rendering correct.

**Independent Test**: Verify language selector works (en ↔ ur ↔ ur-roman), all sections display translated content, Urdu renders correctly (RTL), Roman Urdu renders correctly (Latin chars). Acceptance scenarios in spec.md#US6.

### Implementation for User Story 6

- [ ] T084 [P] [US6] Complete Urdu translations in frontend/src/i18n/locales/ur.json (all 10 sections: hero, problem, solution, features, how-it-works, preview, target-audience, pricing, final-CTA, footer)
- [ ] T085 [P] [US6] Complete Roman Urdu translations in frontend/src/i18n/locales/ur-roman.json (all 10 sections with Latin character support)
- [ ] T086 [P] [US6] Validate Urdu translations with native speakers (glossary for technical terms, cultural appropriateness)
- [ ] T087 [P] [US6] Validate Roman Urdu translations with native speakers (Latin character rendering, consistency)
- [ ] T086 [US6] Implement language selector in LandingHeader to switch between en/ur/ur-roman dynamically
- [ ] T087 [US6] Test language selector saves preference to localStorage (persists across page reloads)
- [ ] T088 [US6] Test language selector updates URL to reflect chosen language (?lang=ur, ?lang=ur-roman)
- [ ] T089 [US6] Verify Urdu content renders correctly (RTL support, font rendering, character encoding UTF-8)
- [ ] T090 [US6] Verify Roman Urdu content renders correctly (Latin characters, proper spacing, diacritics if any)
- [ ] T091 [US6] Test all section components display translated content when language changes
- [ ] T092 [US6] Add RTL CSS support for Urdu sections (text-align, direction: rtl, padding/margin adjustments)
- [ ] T093 [US6] Test CTA buttons and links work correctly in all languages (no broken navigation)
- [ ] T094 [US6] Create E2E test for language switching in frontend/tests/landing/e2e/landing.spec.ts (verify en → ur → ur-roman switching)
- [ ] T095 [US6] Verify SEO meta tags update with language (hreflang links if multi-language version needed)

**Checkpoint**: User Story 6 complete - all 3 languages supported, translations validated, language switching works

---

## Phase 9: Accessibility & Performance Polish

**Purpose**: Ensure WCAG AA compliance, performance targets met, and cross-browser testing

- [ ] T096 [P] Validate page color contrast meets WCAG AA (4.5:1 normal, 3:1 large) using axe-core in frontend/tests/landing/e2e/accessibility.spec.ts
- [ ] T097 [P] Test keyboard navigation (Tab, Shift+Tab, Enter) through all interactive elements on landing page
- [ ] T098 [P] Test landing page with screen reader (NVDA/JAWS simulation) - verify semantic HTML + ARIA labels work
- [ ] T099 [P] Verify focus visible on all interactive elements (buttons, links, form inputs if any)
- [ ] T100 [P] Verify prefers-reduced-motion respected for animations (CSS animations reduce/removed for users with motion sensitivity)
- [ ] T101 Run Lighthouse audit targeting: Performance 90+, SEO 90+, Accessibility 90+, Best Practices 85+ in frontend/tests/landing/
- [ ] T102 Verify page load time < 2 seconds on standard 4G throttle (measured via Lighthouse)
- [ ] T103 Verify LCP (Largest Contentful Paint) < 2.5s, FID < 100ms, CLS < 0.1
- [ ] T104 Optimize images (WebP, AVIF with fallbacks, lazy loading, next/image component)
- [ ] T105 Verify <100KB total CSS + JS (excluding dependencies)
- [ ] T106 Test page in Chrome, Firefox, Safari, Edge (latest 2 versions each)
- [ ] T107 [P] Test on iOS Safari (iPhone 12+) for mobile responsiveness
- [ ] T108 [P] Test on Android Chrome for mobile responsiveness
- [ ] T109 [P] Test on iPad Safari (tablet) for tablet responsiveness
- [ ] T110 Verify SEO meta tags: title, description, og:image, og:title, og:description, twitter:card
- [ ] T111 Add Schema.org structured data (SoftwareApplication, Organization) in frontend/src/app/(landing)/metadata.ts
- [ ] T112 Submit landing page to Google Search Console for indexing
- [ ] T113 Verify all external links work (GitHub, social, privacy, terms) - no 404s or timeouts

**Checkpoint**: Accessibility and performance targets met, browser compatibility verified

---

## Phase 10: Testing & Verification

**Purpose**: Comprehensive E2E and integration testing, conversion metrics setup

- [ ] T114 [P] Create E2E test suite in frontend/tests/landing/e2e/landing.spec.ts covering all user journeys
- [ ] T115 [P] Create E2E conversion flow test in frontend/tests/landing/e2e/conversion.spec.ts (hero → CTA → signup page)
- [ ] T116 [P] Create E2E language switching test in frontend/tests/landing/e2e/landing.spec.ts (en ↔ ur ↔ ur-roman)
- [ ] T117 [P] Create E2E accessibility test in frontend/tests/landing/e2e/accessibility.spec.ts (WCAG AA, keyboard nav, screen reader)
- [ ] T118 [P] Create E2E responsive design test in frontend/tests/landing/e2e/landing.spec.ts (mobile 320px, tablet 768px, desktop 1920px)
- [ ] T119 Create unit test for useLanguage hook in frontend/tests/landing/unit/useLanguage.test.ts
- [ ] T120 Create component test for Footer in frontend/tests/landing/component/Footer.test.tsx
- [ ] T121 Create component test for LandingHeader in frontend/tests/landing/component/LandingHeader.test.tsx
- [ ] T122 Create component test for LanguageSelector in frontend/tests/landing/component/LanguageSelector.test.tsx
- [ ] T123 Create component test for CTAButton in frontend/tests/landing/component/CTAButton.test.tsx
- [ ] T124 Run full test suite: `npm run test` (unit + component) in frontend/
- [ ] T125 Run E2E tests: `npm run test:e2e` in frontend/
- [ ] T126 Run Lighthouse CI: `npm run test:performance` in frontend/ (Performance 90+, SEO 90+, Accessibility 90+)
- [ ] T127 Verify all tests pass before deployment

**Checkpoint**: All tests passing, metrics baseline established (load time, CTA CTR, conversion funnel)

---

## Phase 11: Documentation & Deployment

**Purpose**: Documentation, deployment checklist, and production readiness

- [ ] T128 Update frontend/DEVELOPMENT.md with landing page setup instructions (install next-intl, i18n config, running locally)
- [ ] T129 Add landing page to frontend/README.md with overview, features, languages supported
- [ ] T130 Create deployment checklist: frontend/DEPLOYMENT.md (pre-deployment, go-live, post-launch monitoring)
- [ ] T131 [P] Set up Lighthouse CI in CI/CD pipeline to monitor performance/SEO/accessibility on every commit
- [ ] T132 [P] Set up analytics tracking (Google Analytics snippet, conversion event tracking - optional, can be added post-MVP)
- [ ] T133 [P] Configure redirects if needed (e.g., old domain → new landing page domain)
- [ ] T134 Test staging deployment: deploy landing page to staging environment, verify all links and functions work
- [ ] T135 Final QA verification: test all acceptance scenarios from spec.md (US1-US6) on staging
- [ ] T136 Deploy to production: `git push origin 003-landing-page && merge to main && deploy`
- [ ] T137 [P] Monitor landing page metrics (load time, CTA CTR, bounce rate, conversion funnel) post-launch
- [ ] T138 [P] Set up alerts for performance regression (Lighthouse scores <90, load time >2s)
- [ ] T139 Collect user feedback post-launch (surveys, heatmaps, user testing)
- [ ] T140 [P] Plan iterative improvements based on metrics (A/B test CTAs, optimize low-performing sections)

**Checkpoint**: Landing page deployed to production, monitoring active, documentation complete

---

## Summary & Execution Strategy

### Task Count & Organization

**Total Tasks**: 140 (T001-T140)

**By User Story**:
- **Setup & Foundation**: T001-T023 (23 tasks)
- **User Story 1 (US1 - Discover)**: T024-T039 (16 tasks, P1 MVP-critical)
- **User Story 2 (US2 - Convert)**: T040-T051 (12 tasks, P1 MVP-critical)
- **User Story 3 (US3 - Differentiate)**: T052-T059 (8 tasks, P2)
- **User Story 4 (US4 - Return Users)**: T060-T068 (9 tasks, P2)
- **User Story 5 (US5 - Explore)**: T069-T083 (15 tasks, P3)
- **User Story 6 (US6 - Multilingual)**: T084-T095 (12 tasks, P2)
- **Accessibility & Performance**: T096-T113 (18 tasks)
- **Testing & Verification**: T114-T127 (14 tasks)
- **Documentation & Deployment**: T128-T140 (13 tasks)

### Parallelization Opportunities

**Phase 1 (Setup)**: T004-T006, T010 can run in parallel (different files)
**Phase 2 (Foundation)**: T012-T017 can run in parallel (independent components)
**Phase 3 (US1)**: T024-T027 can run in parallel (different section components)
**Phase 5 (US3)**: T052-T053 can run in parallel
**Phase 6 (US4)**: T060-T062 can run in parallel
**Phase 7 (US5)**: T069-T071, T076-T079 can run in parallel
**Phase 8 (US6)**: T084-T087, T088-T095 can run in parallel
**Phase 9 (A11y/Performance)**: T096-T109 can run in parallel (independent audits)
**Phase 10 (Testing)**: T114-T123 can run in parallel (different test files)
**Phase 11 (Deployment)**: T131-T133, T137-T140 can run in parallel

### MVP Scope (Recommended First Release)

**MVP**: User Stories 1 + 2 (Discover + Convert) = Essential for landing page success

- Complete: T001-T051 (Setup + Foundation + US1 + US2)
- Achieves: <2s load, hero + features + CTAs, 15-20% CTA CTR target
- Timeline: ~2 weeks (10 developer days)
- Testing: Component tests + E2E conversion flow (T038-T039, T050)
- Deploy: Production-ready with core functionality

### Phase 2 Release (Post-MVP)

**Phase 2**: Add User Stories 3-6 (Differentiation + Return Users + Features + Multilingual)

- Complete: T052-T095
- Adds: Target audience, login access, detailed features, 3-language support
- Timeline: ~2-3 weeks additional

### Phase 3 Release (Polish)

**Phase 3**: Accessibility, Performance, Comprehensive Testing, Deployment

- Complete: T096-T140
- Adds: WCAG AA compliance, full test coverage, performance optimization, monitoring
- Timeline: ~1 week

### Independent Test Criteria (Per User Story)

**US1 (Discover)**: Visit page, within 5 seconds understand: (1) app purpose, (2) problem solved, (3) free-to-start message

**US2 (Convert)**: Count CTAs (hero, features, footer), verify all lead to /auth/signup, verify "No credit card required"

**US3 (Differentiate)**: Review "Who Is This For" (identifies 4 personas), verify unique features (multilingual, clean UI, free)

**US4 (Return Users)**: Verify "Log In" and "Sign Up" links in header and footer, both functional to auth endpoints

**US5 (Explore)**: Verify 5-6 features section, free tier explanation, app preview/screenshots present

**US6 (Multilingual)**: Switch en ↔ ur ↔ ur-roman, verify all content translates, Urdu RTL renders, Roman Urdu Latin chars work

### Suggested Starting Tasks (Day 1)

```
1. T001: npm install next-intl
2. T002-T003: i18n config and middleware
3. T004-T006: Translation JSON files (en/ur/ur-roman)
4. T007-T009: Types, hooks, route structure
5. T012-T017: Foundation components (Header, Footer, Language Selector, Button, etc.)
6. T024-T027: Core US1 sections (Hero, Problem, Solution, Features)
```

---

## Notes for Implementation

- Every task must reference `[Task]: T-XXX, [From]: specs/003-landing-page/spec.md#FR-XXX` in code comments
- Use `frontend/src/` paths consistently throughout
- Tests are optional but strongly recommended for landing page reliability
- Language switching should use both URL parameter (`?lang=ur`) and localStorage for persistence
- Prioritize Lighthouse CI automation to prevent performance regression
- Consider A/B testing CTAs post-MVP to optimize 15-20% CTR target

---

**Status**: ✅ READY FOR IMPLEMENTATION

Next: Begin Phase 1 (Setup) with T001-T011. Estimated completion: 16-20 developer days (~3-4 weeks for full feature with all phases).
