//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { expect, test } from '@playwright/test';

test('reader session can authenticate but not access the admin report', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByText('server: healthy')).toBeVisible();
  await page.getByRole('button', { name: 'Who am I?' }).click();
  await expect(page.locator('#response-output')).toContainText('ErrorUnauthenticated_');

  await page.getByRole('button', { name: 'Sign in as reader' }).click();
  await expect(page.locator('#session-pill')).toContainText('reader');

  await page.getByRole('button', { name: 'Who am I?' }).click();
  await expect(page.locator('#response-output')).toContainText('Demo Reader');
  await expect(page.locator('#request-pill')).toContainText(/request id: [0-9a-f-]{36}/i);

  await page.getByRole('button', { name: 'Load admin report' }).click();
  await expect(page.locator('#response-output')).toContainText('ErrorUnauthorized_');
  await expect(page.locator('#ops-output')).toContainText('fn.adminReport');
});

test('admin session can access the admin report and see unknown errors stay generic', async ({ page }) => {
  await page.goto('/');

  await page.getByRole('button', { name: 'Sign in as admin' }).click();
  await expect(page.locator('#session-pill')).toContainText('admin');

  await page.getByRole('button', { name: 'Load admin report' }).click();
  await expect(page.locator('#response-output')).toContainText('requestCount');
  await expect(page.locator('#response-output')).toContainText('unknownErrorCount');

  await page.getByRole('button', { name: 'Trigger server bug' }).click();
  await expect(page.locator('#response-output')).toContainText('ErrorUnknown_');
  await expect(page.locator('#response-output')).toContainText('caseId');
  await expect(page.locator('#ops-output')).toContainText('telepact.error');
  await expect(page.locator('#ops-output')).toContainText('ErrorUnknown_');
});
