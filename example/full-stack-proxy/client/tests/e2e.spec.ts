//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { expect, test } from '@playwright/test';

test('browser request reaches the Go Telepact server through the Python proxy', async ({ page }) => {
  await page.goto('/');

  await expect(page.locator('#health-pill')).toContainText('proxy: connected');
  await page.getByRole('button', { name: 'Send greeting' }).click();

  await expect(page.locator('#outcome-pill')).toContainText('Ok_');
  await expect(page.locator('#response-output')).toContainText('Hello Telepact from the Go Telepact server!');
  await expect(page.locator('#response-output')).toContainText('rpc.demo.greet');
  await expect(page.locator('#path-pill')).toContainText('POST /rpc/rpc.demo.greet');
});

test('browser uses a fixed missing-subject route and surfaces proxy transport failures', async ({ page }) => {
  await page.goto('/');

  await page.getByRole('button', { name: 'Use missing subject' }).click();

  await expect(page.locator('#outcome-pill')).toContainText('transport failure');
  await expect(page.locator('#response-output')).toContainText('rpc.demo.missing');
  await expect(page.locator('#response-output')).toContainText('proxy returned');
  await expect(page.locator('#path-pill')).toContainText('POST /rpc/rpc.demo.missing');
});
