import { test, expect } from '@playwright/test';

/**
 * E2E tests for authentication flow.
 *
 * Tests:
 * - User registration → dashboard
 * - User login → logout
 * - Session persistence across page refreshes
 */

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage before each test
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
  });

  test('should complete registration flow and redirect to dashboard', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');

    // Switch to signup tab
    await page.click('text=Sign Up');

    // Fill in registration form
    const timestamp = Date.now();
    const email = `test${timestamp}@example.com`;
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', 'password123');

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL('/dashboard', { timeout: 10000 });

    // Verify user is on dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('text=Welcome to your Dashboard')).toBeVisible();
    await expect(page.locator(`text=${email}`)).toBeVisible();
  });

  test('should complete login → logout flow', async ({ page }) => {
    // First, create a test user (registration)
    await page.goto('/login');
    await page.click('text=Sign Up');

    const timestamp = Date.now();
    const email = `test${timestamp}@example.com`;
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');

    // Now logout
    await page.click('text=Logout');

    // Wait for redirect to landing page
    await page.waitForURL('/', { timeout: 5000 });
    await expect(page).toHaveURL('/');

    // Try to access dashboard (should redirect to login)
    await page.goto('/dashboard');
    await page.waitForURL('/login', { timeout: 5000 });
    await expect(page).toHaveURL('/login');

    // Now login with same credentials
    await page.fill('input[id="login-email"]', email);
    await page.fill('input[id="login-password"]', 'password123');
    await page.click('button[type="submit"]');

    // Should be back on dashboard
    await page.waitForURL('/dashboard', { timeout: 10000 });
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator(`text=${email}`)).toBeVisible();
  });

  test('should persist session across page refreshes', async ({ page }) => {
    // Register and login
    await page.goto('/login');
    await page.click('text=Sign Up');

    const timestamp = Date.now();
    const email = `test${timestamp}@example.com`;
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');

    // Verify logged in
    await expect(page.locator(`text=${email}`)).toBeVisible();

    // Refresh the page
    await page.reload();

    // Should still be logged in
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator(`text=${email}`)).toBeVisible();

    // Open in new tab (simulate)
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator(`text=${email}`)).toBeVisible();
  });

  test('should show validation errors for invalid inputs', async ({ page }) => {
    await page.goto('/login');
    await page.click('text=Sign Up');

    // Try to submit with short password
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'short');
    await page.click('button[type="submit"]');

    // Should show validation error
    await expect(page.locator('text=/Password must be at least 8 characters/i')).toBeVisible();

    // Try invalid email
    await page.fill('input[type="email"]', 'invalid-email');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Should show email validation error
    await expect(page.locator('text=/valid email/i')).toBeVisible();
  });

  test('should handle login with incorrect credentials', async ({ page }) => {
    await page.goto('/login');

    // Try to login with non-existent user
    await page.fill('input[id="login-email"]', 'nonexistent@example.com');
    await page.fill('input[id="login-password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Should show error message
    await expect(page.locator('text=/Invalid email or password/i')).toBeVisible();

    // Should still be on login page
    await expect(page).toHaveURL('/login');
  });
});
