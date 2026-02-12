# Landing Page Testing Checklist

## Pre-Testing Setup
- [ ] Dependencies installed (`npm install`)
- [ ] Environment variables configured (`.env.local` created from `.env.example`)
- [ ] Development server running (`npm run dev`)
- [ ] Browser opened to http://localhost:3000

## Visual Testing

### Hero Section
- [ ] Headline displays: "Never forget a task again."
- [ ] Subheadline displays: "Simple. Powerful. Yours."
- [ ] "Get Started" button is visible and prominent
- [ ] Phone mockup is visible on the right (desktop) or below (mobile)
- [ ] Phone mockup shows dashboard with sidebar and task cards
- [ ] Background gradient is visible (dark theme)
- [ ] Decorative gradient orbs are visible
- [ ] Animations play on page load (fade-in, slide-up)

### Phone Mockup
- [ ] Device frame renders correctly with notch
- [ ] Top navbar shows "My Tasks" title
- [ ] User avatar circle is visible in navbar
- [ ] Sidebar shows three filters: All, Pending, Done
- [ ] "All" filter is highlighted (blue background)
- [ ] Three task cards are visible
- [ ] Task 1: "Buy groceries" with Circle icon, Pending badge (orange)
- [ ] Task 2: "Finish report" with CheckCircle icon, Completed badge (green), strikethrough text
- [ ] Task 3: "Call dentist" with Circle icon, Pending badge (orange)
- [ ] All task cards have proper spacing and borders
- [ ] Phone mockup has realistic shadows

### Features Section
- [ ] Section heading: "Everything you need to stay organized"
- [ ] Section description is visible
- [ ] Four feature cards are displayed
- [ ] Feature 1: CheckCircle icon, "Simple Task Management"
- [ ] Feature 2: Filter icon, "Smart Filtering"
- [ ] Feature 3: Lock icon, "Secure & Private"
- [ ] Feature 4: Globe icon, "Always Accessible"
- [ ] Cards have staggered animation on scroll/load
- [ ] Hover effects work (border color, background, shadow)

### CTA Section
- [ ] Heading: "Ready to get organized?"
- [ ] Description text is visible
- [ ] "Get Started Free" button is prominent
- [ ] Decorative gradient orb is visible
- [ ] Section has proper spacing

### Login Page
- [ ] Navigate to /login works
- [ ] Login form is centered and visible
- [ ] Email and password inputs are functional
- [ ] "Sign In" button is visible
- [ ] "Sign up" link is visible
- [ ] "Back to home" link works

### Error Pages
- [ ] Navigate to /nonexistent shows 404 page
- [ ] 404 page shows "404" heading
- [ ] "Go Home" and "Sign In" buttons work
- [ ] Error boundary catches runtime errors (test by throwing error)

## Responsive Testing

### Mobile (375px)
- [ ] Hero section stacks vertically (headline above phone)
- [ ] Phone mockup is centered and sized appropriately
- [ ] CTA button is full width or centered
- [ ] Features grid shows 1 column
- [ ] All text is readable
- [ ] Touch targets are at least 44x44px
- [ ] No horizontal scrolling

### Tablet (768px)
- [ ] Hero section may stack or show side-by-side
- [ ] Features grid shows 2 columns
- [ ] Phone mockup is appropriately sized
- [ ] All spacing looks balanced

### Desktop (1024px+)
- [ ] Hero section shows side-by-side layout
- [ ] Phone mockup on right side
- [ ] Features grid shows 4 columns
- [ ] Content is centered with max-width container
- [ ] Decorative elements are visible

## Functionality Testing

### Navigation
- [ ] Hero "Get Started" button links to /login
- [ ] CTA "Get Started Free" button links to /login
- [ ] Login page "Back to home" link returns to /
- [ ] 404 page "Go Home" button returns to /
- [ ] 404 page "Sign In" button goes to /login

### Accessibility
- [ ] Tab navigation works through all interactive elements
- [ ] Focus indicators are visible
- [ ] Screen reader announces sections properly
- [ ] All images have alt text or aria-labels
- [ ] Heading hierarchy is correct (h1 → h2 → h3)
- [ ] Color contrast meets WCAG AA standards
- [ ] Animations respect prefers-reduced-motion

### Performance
- [ ] Page loads quickly (< 2 seconds on fast connection)
- [ ] No console errors in browser DevTools
- [ ] No layout shift during load (CLS)
- [ ] Images/assets load properly
- [ ] Animations are smooth (60fps)

## SEO Testing

### Meta Tags
- [ ] Page title is set correctly
- [ ] Meta description is present
- [ ] Open Graph tags are present (og:title, og:description, og:type)
- [ ] Twitter Card tags are present
- [ ] Viewport meta tag is set

### Semantic HTML
- [ ] Proper use of semantic elements (section, nav, main)
- [ ] Heading hierarchy is logical
- [ ] Links have descriptive text
- [ ] Buttons use button elements (not divs)

### Crawlability
- [ ] /robots.txt is accessible
- [ ] /sitemap.xml is accessible
- [ ] /manifest.json is accessible (PWA manifest)
- [ ] Favicon loads correctly

## Browser Testing
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

## Dark Mode Testing
- [ ] Dark theme is applied by default
- [ ] All text is readable on dark backgrounds
- [ ] Color contrast is sufficient
- [ ] Hover states are visible
- [ ] Focus states are visible

## Build Testing
- [ ] Production build succeeds (`npm run build`)
- [ ] No TypeScript errors
- [ ] No ESLint errors
- [ ] Build output is optimized
- [ ] Production server starts (`npm start`)
- [ ] Production site works correctly

## Known Issues / Future Work
- [ ] Icon assets (icon-192.png, icon-512.png) need to be created for PWA
- [ ] Analytics integration needed for tracking CTA clicks
- [ ] Performance metrics need real-world testing
- [ ] Unit tests need to be written (Vitest)
- [ ] E2E tests need to be written (Playwright)
- [ ] Login page needs actual authentication logic
- [ ] Backend API integration needed

## Sign-off
- [ ] All critical tests passed
- [ ] No blocking issues found
- [ ] Ready for deployment

**Tested by:** _________________
**Date:** _________________
**Notes:** _________________
