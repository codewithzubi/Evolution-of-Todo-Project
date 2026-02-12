# Quickstart Guide: Public Landing Page Testing

**Feature**: 003-landing-page
**Date**: 2026-02-09
**Purpose**: Test scenarios and acceptance criteria for landing page implementation

## Prerequisites

- Frontend development server running (`npm run dev` in frontend/)
- Modern browser (Chrome, Firefox, Safari, or Edge)
- Responsive design testing tools (browser DevTools or physical devices)

## Test Scenarios

### Scenario 1: Hero Section Loads Correctly

**User Story**: View Hero Section and Understand Value Proposition (US1)

**Test Steps**:
1. Navigate to `http://localhost:3000/`
2. Verify page loads in under 2 seconds
3. Observe hero section above the fold (no scrolling required)

**Expected Results**:
- ✅ Large headline visible (48-72px font size)
- ✅ Subheadline explaining value proposition visible
- ✅ Primary CTA button ("Get Started" or "Sign Up Free") visible and prominent
- ✅ Phone mockup visible on right side (desktop) or below headline (mobile)
- ✅ Dark gradient background with subtle animations (fade-in effects)
- ✅ Phone mockup shows dashboard interface with sample tasks

**Acceptance Criteria**:
- Hero section occupies full viewport height on desktop
- All text is readable with sufficient contrast (WCAG AA)
- CTA button has minimum 44x44px touch target on mobile
- Phone mockup displays task cards with checkboxes, titles, and status badges

---

### Scenario 2: Phone Mockup Displays Dashboard Preview

**User Story**: View Hero Section and Understand Value Proposition (US1)

**Test Steps**:
1. Navigate to landing page
2. Locate phone mockup in hero section
3. Examine mockup content

**Expected Results**:
- ✅ Realistic device frame (iPhone-style with rounded corners and notch)
- ✅ Dashboard interface visible inside device frame
- ✅ Sample tasks displayed with checkboxes, titles, and status badges
- ✅ Sidebar with filters visible (All Tasks, Pending, Completed)
- ✅ Proper shadows and depth on device frame
- ✅ Mockup scales responsively on different screen sizes

**Acceptance Criteria**:
- Phone mockup is positioned on right side on desktop (>1024px)
- Phone mockup is below headline on mobile (<768px)
- Mockup maintains aspect ratio across all breakpoints
- Image loads with priority (no delayed appearance)

---

### Scenario 3: Features Section Displays Correctly

**User Story**: Explore Features Section (US2)

**Test Steps**:
1. Navigate to landing page
2. Scroll down from hero section
3. Observe features section

**Expected Results**:
- ✅ 3-4 feature cards displayed in responsive grid
- ✅ Each card has icon, title, and short description
- ✅ Desktop: 4 columns (or 2x2 grid for 4 cards)
- ✅ Tablet: 2 columns
- ✅ Mobile: 1 column (stacked vertically)
- ✅ Hover effects on cards (desktop only): elevation, border glow, or scale

**Feature Card Content**:
1. **Simple Task Management** - Icon: CheckCircle - "Add, edit, complete tasks effortlessly"
2. **Smart Filtering** - Icon: Filter - "View all, pending, or completed tasks"
3. **Secure & Private** - Icon: Lock - "Your tasks, your data, fully isolated"
4. **Always Accessible** - Icon: Globe - "Works on any device, anywhere"

**Acceptance Criteria**:
- Cards have equal height in each row
- Icons are 24px (1.5rem) size
- Text is readable with sufficient contrast
- Hover effects are smooth (0.3s transition)

---

### Scenario 4: CTA Buttons Navigate to Login

**User Story**: Click CTA and Navigate to Signup (US3)

**Test Steps**:
1. Navigate to landing page
2. Click primary CTA button in hero section
3. Verify redirect to `/login`
4. Return to landing page
5. Scroll to bottom
6. Click final CTA button
7. Verify redirect to `/login`

**Expected Results**:
- ✅ Hero CTA button redirects to `/login` page
- ✅ Final CTA section displays centered text ("Ready to get organized?")
- ✅ Final CTA button ("Get Started") redirects to `/login` page
- ✅ Navigation occurs in under 3 seconds
- ✅ CTA buttons show hover effects (color change, elevation, or scale)

**Acceptance Criteria**:
- Both CTA buttons use Next.js Link component (client-side navigation)
- Buttons are visually prominent with high contrast
- Buttons meet minimum touch target size (44x44px) on mobile
- Hover states provide clear visual feedback

---

### Scenario 5: Responsive Design Across Breakpoints

**User Story**: All user stories (responsive requirement)

**Test Steps**:
1. Open landing page in browser DevTools
2. Test at mobile breakpoint (375px width)
3. Test at tablet breakpoint (768px width)
4. Test at desktop breakpoint (1280px width)
5. Test at large desktop (1920px width)

**Expected Results**:

**Mobile (<768px)**:
- ✅ Single column layout
- ✅ Headline at top, phone mockup below (stacked)
- ✅ Feature cards in single column
- ✅ CTA buttons full-width or centered
- ✅ Text remains readable (no horizontal scroll)

**Tablet (768-1024px)**:
- ✅ Hero section may remain stacked or transition to two-column
- ✅ Feature cards in 2-column grid
- ✅ Generous spacing maintained

**Desktop (>1024px)**:
- ✅ Two-column hero (headline left, mockup right)
- ✅ Feature cards in 4-column grid
- ✅ Container max-width: 1280px with horizontal padding
- ✅ Centered content with whitespace on sides

**Acceptance Criteria**:
- No horizontal scrolling at any breakpoint
- All content readable and accessible
- Touch targets meet minimum size on mobile
- Layout adapts smoothly between breakpoints

---

### Scenario 6: Performance and Core Web Vitals

**User Story**: All user stories (performance requirement)

**Test Steps**:
1. Open Chrome DevTools
2. Navigate to Lighthouse tab
3. Run Lighthouse audit (Desktop and Mobile)
4. Review Core Web Vitals in Performance tab

**Expected Results**:
- ✅ Page load time: <2 seconds
- ✅ LCP (Largest Contentful Paint): <2.5s
- ✅ FID (First Input Delay): <100ms
- ✅ CLS (Cumulative Layout Shift): <0.1
- ✅ Lighthouse Performance score: 90+
- ✅ Lighthouse Accessibility score: 95+
- ✅ Lighthouse SEO score: 100

**Acceptance Criteria**:
- All Core Web Vitals in "Good" range (green)
- No render-blocking resources above the fold
- Images optimized (WebP format, proper sizing)
- Minimal JavaScript bundle size (<50KB)

---

### Scenario 7: SEO and Metadata

**User Story**: All user stories (SEO requirement)

**Test Steps**:
1. Navigate to landing page
2. View page source (Ctrl+U or Cmd+U)
3. Inspect <head> section
4. Use browser extensions (e.g., SEO Meta in 1 Click)

**Expected Results**:
- ✅ Title tag present and descriptive
- ✅ Meta description present (150-160 characters)
- ✅ Open Graph tags (og:title, og:description, og:image, og:url)
- ✅ Twitter Card tags (twitter:card, twitter:title, twitter:description)
- ✅ Canonical URL specified
- ✅ Viewport meta tag present
- ✅ Semantic HTML5 elements (<header>, <section>, <main>)
- ✅ Alt text on all images

**Acceptance Criteria**:
- Lighthouse SEO score: 100
- All meta tags properly formatted
- Structured data (JSON-LD) for organization/website schema
- No broken links or missing resources

---

### Scenario 8: Accessibility Testing

**User Story**: All user stories (accessibility requirement)

**Test Steps**:
1. Navigate to landing page
2. Use keyboard only (Tab, Enter, Shift+Tab)
3. Test with screen reader (NVDA, JAWS, or VoiceOver)
4. Run Lighthouse accessibility audit
5. Check color contrast with browser tools

**Expected Results**:
- ✅ All interactive elements keyboard accessible
- ✅ Focus indicators visible on all focusable elements
- ✅ Screen reader announces all content correctly
- ✅ Alt text on all images (phone mockup, feature icons)
- ✅ Sufficient color contrast (WCAG AA: 4.5:1 for text, 3:1 for large text)
- ✅ No accessibility violations in Lighthouse audit
- ✅ Semantic HTML structure (headings hierarchy)

**Acceptance Criteria**:
- Lighthouse Accessibility score: 95+
- No ARIA violations
- Keyboard navigation works for all interactive elements
- Screen reader can navigate and understand all content

---

### Scenario 9: Cross-Browser Compatibility

**User Story**: All user stories (browser compatibility requirement)

**Test Steps**:
1. Test landing page in Chrome (latest)
2. Test landing page in Firefox (latest)
3. Test landing page in Safari (latest)
4. Test landing page in Edge (latest)

**Expected Results**:
- ✅ Layout renders correctly in all browsers
- ✅ Animations work smoothly in all browsers
- ✅ CTA buttons function correctly in all browsers
- ✅ Phone mockup displays correctly in all browsers
- ✅ No console errors in any browser

**Acceptance Criteria**:
- Visual consistency across all major browsers
- No browser-specific bugs or layout issues
- Graceful degradation for older browsers (if applicable)

---

### Scenario 10: Edge Cases

**Test Steps**:
1. Access landing page while already authenticated (logged in)
2. Test on very small screen (<320px width)
3. Test with slow 3G connection (Chrome DevTools throttling)
4. Test with JavaScript disabled
5. Test with images disabled

**Expected Results**:

**Authenticated User**:
- ✅ Landing page still displays (no automatic redirect)
- ✅ CTA buttons still redirect to /login (or dashboard if logic added)

**Very Small Screen (<320px)**:
- ✅ Content remains readable (may require horizontal scroll)
- ✅ Phone mockup scales down appropriately

**Slow 3G Connection**:
- ✅ Page loads within acceptable time (may exceed 2s target)
- ✅ Progressive loading (content appears incrementally)
- ✅ No broken layout during loading

**JavaScript Disabled**:
- ✅ Static content displays correctly
- ✅ CTA buttons still navigate (using <a> tags or Next.js Link)
- ✅ No animations (graceful degradation)

**Images Disabled**:
- ✅ Alt text displays for phone mockup
- ✅ Layout remains intact (reserved space for images)
- ✅ Feature icons may not display (acceptable)

---

## Quick Validation Checklist

Use this checklist for rapid validation during development:

- [ ] Hero section loads above the fold
- [ ] Headline and subheadline visible and readable
- [ ] Phone mockup displays dashboard preview
- [ ] Primary CTA button visible and functional
- [ ] Features section displays 3-4 cards
- [ ] Feature cards have icons, titles, descriptions
- [ ] Final CTA section at bottom of page
- [ ] All CTA buttons redirect to /login
- [ ] Responsive design works (mobile, tablet, desktop)
- [ ] Page loads in under 2 seconds
- [ ] Core Web Vitals in "Good" range
- [ ] Lighthouse Performance: 90+
- [ ] Lighthouse Accessibility: 95+
- [ ] Lighthouse SEO: 100
- [ ] No console errors or warnings
- [ ] Keyboard navigation works
- [ ] Screen reader announces content correctly
- [ ] Cross-browser compatibility verified

---

## Troubleshooting

### Issue: Page loads slowly (>2s)
**Solution**: Check image optimization, reduce bundle size, enable caching

### Issue: CLS (Layout Shift) too high
**Solution**: Add explicit width/height to images, reserve space for content

### Issue: CTA buttons not redirecting
**Solution**: Verify Next.js Link component usage, check /login route exists

### Issue: Phone mockup not displaying
**Solution**: Check image path, verify Next.js Image component configuration

### Issue: Feature cards not responsive
**Solution**: Verify Tailwind grid classes, test breakpoints in DevTools

---

## Success Criteria Summary

Landing page is ready for production when:
- ✅ All 10 test scenarios pass
- ✅ Quick validation checklist complete
- ✅ Lighthouse scores meet targets (90+, 95+, 100)
- ✅ Core Web Vitals in "Good" range
- ✅ No accessibility violations
- ✅ Cross-browser compatibility verified
- ✅ Constitution compliance confirmed
