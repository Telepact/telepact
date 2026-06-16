//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { test, expect } from '@playwright/test';

test('should display "Telepact" on page load', async ({ page }) => {
  await page.goto('http://localhost:8082'); // Update URL if necessary
  await expect(page.getByRole('heading', { name: 'Telepact' })).toBeVisible();
});
