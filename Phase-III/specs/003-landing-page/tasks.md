# Tasks: Public Landing Page

**Input**: Design documents from `/specs/003-landing-page/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, quickstart.md

**Tests**: Test-First Development (TDD) is required per constitution. Tests are included for all user stories.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/app/`, `frontend/components/`, `tests/`
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for landing page components

- [ ] T001 Create landing components directory structure at frontend/components/landing/
- [ ] T002 [P] Create test directory structure at tests/unit/landing/ and tests/e2e/
- [ ] T003 [P] Verify shadcn/ui Button component exists in frontend/components/ui/button.tsx
- [ ] T004 [P] Verify shadcn/ui Card component exists in frontend/components/ui/card.tsx
- [ ] T005 [P] Create dashboard preview image placeholder at frontend/public/images/dashboard-preview.png (or prepare to use CSS-only mockup)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Configure Next.js metadata exports in frontend/app/layout.tsx for SEO (title, description, Open Graph)
- [ ] T007 [P] Add CSS animation keyframes to frontend/app/globals.css (fade-in, slide-up, prefers-reduced-motion)
- [ ] T008 [P] Configure Tailwind custom colors in tailwind.config.ts (dark mode palette: zinc-950, neutral-900, blue-500/purple-500)
- [ ] T009 [P] Verify Lucide Icons package installed and import test icons (CheckCircle, Filter, Lock, Globe)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Hero Section and Understand Value Proposition (Priority: P1) 🎯 MVP

**Goal**: Display compelling hero section with headline, subheadline, CTA button, and phone mockup showing dashboard preview

**Independent Test**: Visit root URL (/), verify hero section loads with all elements visible above the fold without scrolling

### Tests for User Story 1 (TDD - Write FIRST, ensure they FAIL)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Unit test for HeroSection component in tests/unit/landing/hero-section.test.tsx (renders headline, subheadline, CTA, mockup)
- [ ] T011 [P] [US1] Unit test for PhoneMockup component in tests/unit/landing/phone-mockup.test.tsx (renders device frame, dashboard image, alt text)
- [ ] T012 [P] [US1] E2E test for hero section visibility in tests/e2e/landing-page.spec.ts (above the fold, responsive layout)

### Implementation for User Story 1

- [ ] T013 [P] [US1] Create PhoneMockup component in frontend/components/landing/phone-mockup.tsx (CSS device frame, Next.js Image with priority, dashboard preview)
- [ ] T014 [US1] Create HeroSection component in frontend/components/landing/hero-section.tsx (headline, subheadline, CTA button, PhoneMockup, responsive grid layout)
- [ ] T015 [US1] Add hero section to landing page in frontend/app/page.tsx (import HeroSection, add metadata export, semantic HTML)
- [ ] T016 [US1] Add CSS animations for hero section in frontend/app/globals.css (fade-in for headline, slide-up for mockup, staggered delays)
- [ ] T017 [US1] Verify hero section tests pass and hero displays correctly on all breakpoints (mobile, tablet, desktop)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Explore Features Section (Priority: P1)

**Goal**: Display 3-4 feature cards in responsive grid with icons, titles, and descriptions

**Independent Test**: Scroll to features section, verify 4 cards displayed in responsive grid (4 columns desktop, 2 tablet, 1 mobile)

### Tests for User Story 2 (TDD - Write FIRST, ensure they FAIL)

- [ ] T018 [P] [US2] Unit test for FeatureCard component in tests/unit/landing/feature-card.test.tsx (renders icon, title, description, hover effects)
- [ ] T019 [P] [US2] Unit test for FeaturesSection component in tests/unit/landing/features-section.test.tsx (renders 4 cards, responsive grid)
- [ ] T020 [P] [US2] E2E test for features section in tests/e2e/landing-page.spec.ts (scroll to section, verify grid layout, hover effects)

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create FeatureCard component in frontend/components/landing/feature-card.tsx (shadcn Card, Lucide icon, title, description, hover effects)
- [ ] T022 [US2] Create FeaturesSection component in frontend/components/landing/features-section.tsx (4 feature cards with content, responsive CSS Grid)
- [ ] T023 [US2] Add features section to landing page in frontend/app/page.tsx (import FeaturesSection below hero)
- [ ] T024 [US2] Add feature card content: "Simple Task Management" (CheckCircle), "Smart Filtering" (Filter), "Secure & Private" (Lock), "Always Accessible" (Globe)
- [ ] T025 [US2] Verify features section tests pass and cards display correctly on all breakpoints

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Click CTA and Navigate to Signup (Priority: P1)

**Goal**: CTA buttons in hero and final section redirect to /login page

**Independent Test**: Click any CTA button, verify redirect to /login page in under 3 seconds

### Tests for User Story 3 (TDD - Write FIRST, ensure they FAIL)

- [ ] T026 [P] [US3] Unit test for CTASection component in tests/unit/landing/cta-section.test.tsx (renders centered text, button, Next.js Link)
- [ ] T027 [P] [US3] E2E test for CTA navigation in tests/e2e/landing-page.spec.ts (click hero CTA, verify /login redirect, click final CTA, verify /login redirect)

### Implementation for User Story 3

- [ ] T028 [P] [US3] Create CTASection component in frontend/components/landing/cta-section.tsx (centered text, shadcn Button with Next.js Link to /login)
- [ ] T029 [US3] Add CTA section to landing page in frontend/app/page.tsx (import CTASection at bottom)
- [ ] T030 [US3] Update HeroSection CTA button in frontend/components/landing/hero-section.tsx (ensure Next.js Link to /login, minimum 44x44px touch target)
- [ ] T031 [US3] Verify CTA tests pass and navigation works correctly (client-side routing, under 3 seconds)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T032 [P] Add structured data (JSON-LD) for organization/website schema in frontend/app/page.tsx metadata
- [ ] T033 [P] Optimize dashboard preview image (WebP format, <100KB, multiple sizes) at frontend/public/images/dashboard-preview.png
- [ ] T034 [P] Add explicit width/height to all images to prevent CLS (phone mockup, feature icons if using images)
- [ ] T035 [P] Verify semantic HTML structure (header, section, main, article elements) across all components
- [ ] T036 [P] Add ARIA labels and alt text for accessibility (phone mockup alt text, feature icons aria-label)
- [ ] T037 Run Lighthouse audit (Desktop and Mobile) and verify scores: Performance 90+, Accessibility 95+, SEO 100
- [ ] T038 Run Core Web Vitals check and verify: LCP <2.5s, FID <100ms, CLS <0.1
- [ ] T039 Test responsive design on all breakpoints (320px, 375px, 768px, 1024px, 1280px, 1920px)
- [ ] T040 Test cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- [ ] T041 Test keyboard navigation (Tab, Enter, Shift+Tab) and screen reader (NVDA/VoiceOver)
- [ ] T042 Test edge cases: authenticated user, slow 3G, JavaScript disabled, images disabled
- [ ] T043 Run quickstart.md validation checklist and verify all 10 test scenarios pass
- [ ] T044 Code cleanup and refactoring (remove console.logs, unused imports, format code)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent of US1 (different components)
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Integrates with US1 (hero CTA) but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD Red-Green-Refactor)
- Components before integration
- Individual components (PhoneMockup, FeatureCard) before container components (HeroSection, FeaturesSection)
- Integration into page.tsx after component completion
- Story complete and tests passing before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T005)
- All Foundational tasks marked [P] can run in parallel (T007-T009)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel (T010-T012, T018-T020, T026-T027)
- Component implementations within a story marked [P] can run in parallel (T013, T021, T028)
- All Polish tasks marked [P] can run in parallel (T032-T036)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write first):
Task: "Unit test for HeroSection component in tests/unit/landing/hero-section.test.tsx"
Task: "Unit test for PhoneMockup component in tests/unit/landing/phone-mockup.test.tsx"
Task: "E2E test for hero section visibility in tests/e2e/landing-page.spec.ts"

# After tests fail, launch component implementations together:
Task: "Create PhoneMockup component in frontend/components/landing/phone-mockup.tsx"
# Then create HeroSection (depends on PhoneMockup being available)
```

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together (TDD - write first):
Task: "Unit test for FeatureCard component in tests/unit/landing/feature-card.test.tsx"
Task: "Unit test for FeaturesSection component in tests/unit/landing/features-section.test.tsx"
Task: "E2E test for features section in tests/e2e/landing-page.spec.ts"

# After tests fail, launch component implementations together:
Task: "Create FeatureCard component in frontend/components/landing/feature-card.tsx"
# Then create FeaturesSection (depends on FeatureCard being available)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Hero Section)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready (hero section is the primary conversion driver)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - hero section!)
3. Add User Story 2 → Test independently → Deploy/Demo (hero + features)
4. Add User Story 3 → Test independently → Deploy/Demo (complete landing page)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Hero Section)
   - Developer B: User Story 2 (Features Section)
   - Developer C: User Story 3 (CTA Navigation)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD cycle: Write tests first (Red) → Implement (Green) → Refactor
- Verify tests fail before implementing (Red phase)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All 3 user stories are P1 (critical for conversion funnel)
- Landing page is frontend-only (no backend API calls, no database)
- Performance targets: <2s load, LCP <2.5s, FID <100ms, CLS <0.1
- Lighthouse targets: 90+ performance, 95+ accessibility, 100 SEO
- Constitution compliance: dark mode, shadcn/ui, Lucide Icons, responsive design
