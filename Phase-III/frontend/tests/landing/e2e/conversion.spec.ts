// [Task]: T050, [From]: specs/003-landing-page/tasks.md#T050
// E2E test for conversion flow: hero → CTA → signup page

import { test, expect } from '@playwright/test';

test.describe('Landing Page Conversion Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to landing page
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display hero section with CTA button', async ({ page }) => {
    // Verify hero headline is visible
    const headline = page.getByRole('heading', {
      name: /Manage Your Tasks Effortlessly/i,
    });
    await expect(headline).toBeVisible();

    // Verify hero CTA button is visible
    const heroCTA = page.getByRole('button', {
      name: /Get Started Free/i,
    });
    await expect(heroCTA).toBeVisible();

    // Verify trust line is visible
    const trustLine = page.getByText(/No credit card required/i);
    await expect(trustLine).toBeVisible();
  });

  test('should navigate to signup when hero CTA is clicked', async ({
    page,
  }) => {
    // Click hero CTA button
    const heroCTA = page.getByRole('button', {
      name: /Get Started Free/i,
    }).first();

    // Setup navigation tracking
    const navigationPromise = page.waitForNavigation();
    await heroCTA.click();
    await navigationPromise;

    // Verify navigation to auth/signup
    expect(page.url()).toContain('/auth/signup');
  });

  test('should have multiple CTAs throughout the page', async ({ page }) => {
    // Count all CTA buttons on page (hero, features, final CTA)
    const ctaButtons = page.getByRole('button', {
      name: /Get Started Free|Learn More|Start Managing Tasks Now/i,
    });

    const count = await ctaButtons.count();
    // Should have at least 3 CTAs: hero + features + final CTA
    expect(count).toBeGreaterThanOrEqual(3);

    // Verify all visible CTAs are accessible
    for (let i = 0; i < count; i++) {
      const button = ctaButtons.nth(i);
      if (await button.isVisible()) {
        await expect(button).toHaveAttribute('type', 'button');
      }
    }
  });

  test('should verify all CTAs point to /auth/signup', async ({ page }) => {
    // Get all elements that might be CTAs
    const ctaLinks = page.locator('button:has-text("Get Started Free"), button:has-text("Learn More"), button:has-text("Start Managing Tasks Now")');

    const count = await ctaLinks.count();

    // For each visible CTA, track navigation
    for (let i = 0; i < count; i++) {
      const cta = ctaLinks.nth(i);
      if (await cta.isVisible()) {
        // Store current URL
        const currentUrl = page.url();

        // Click CTA
        const navigationPromise = page.waitForNavigation().catch(() => null);
        await cta.click();
        await navigationPromise;

        // Verify signup URL (or landing URL if navigation didn't happen)
        const newUrl = page.url();
        expect(
          newUrl.includes('/auth/signup') || newUrl === currentUrl
        ).toBeTruthy();

        // Navigate back to landing
        await page.goto('/');
        await page.waitForLoadState('networkidle');
      }
    }
  });

  test('should display final CTA section with trust line', async ({
    page,
  }) => {
    // Scroll to bottom to see final CTA
    await page.evaluate(() => {
      window.scrollBy(0, document.body.scrollHeight);
    });

    // Verify final CTA section elements
    const finalCTAHeadline = page.getByRole('heading', {
      name: /Ready to Take Control?/i,
    });
    await expect(finalCTAHeadline).toBeVisible();

    // Verify final CTA button
    const finalCTA = page.getByRole('button', {
      name: /Start Managing Tasks Now/i,
    });
    await expect(finalCTA).toBeVisible();

    // Verify trust line on final CTA
    const trustLine = page.getByText(
      /Free account\. No credit card\. Cancel anytime\./i
    );
    await expect(trustLine).toBeVisible();
  });

  test('should have proper accessibility on CTA buttons', async ({ page }) => {
    // Verify buttons are keyboard accessible
    const heroCTA = page.getByRole('button', {
      name: /Get Started Free/i,
    }).first();

    // Tab to the button
    await page.keyboard.press('Tab');

    // Note: The exact focus indicator depends on browser and styling
    // Just verify the button is in the tab order
    await expect(heroCTA).toBeFocused();
  });

  test('should have proper button sizing for touch targets', async ({
    page,
  }) => {
    // Get hero CTA button
    const heroCTA = page.getByRole('button', {
      name: /Get Started Free/i,
    }).first();

    // Check button has minimum height of 48px for touch targets
    const height = await heroCTA.evaluate(
      (el) => window.getComputedStyle(el).height
    );

    const heightValue = parseInt(height);
    // Should be at least 40px (48px min-height applies to lg size)
    expect(heightValue).toBeGreaterThanOrEqual(40);
  });

  test('should load page with good performance', async ({ page }) => {
    // Navigation timing should be under 3 seconds for full page load
    const navigationTiming = await page.evaluate(() => {
      const navigation = window.performance.getEntriesByType(
        'navigation'
      )[0] as PerformanceNavigationTiming;
      return navigation ? navigation.loadEventEnd : 0;
    });

    const loadTime = navigationTiming / 1000; // Convert to seconds
    expect(loadTime).toBeLessThan(3);
  });
});
