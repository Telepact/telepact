import { test, expect } from '@playwright/test';

test('should display "Telepact" on page load', async ({ page }) => {
  await page.goto('http://localhost:5173'); // Update URL if necessary
  await expect(page.locator('text=Telepact')).toBeVisible();
});
