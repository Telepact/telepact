//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import { expect, test } from '@playwright/test';

test('production example runs end to end in the browser', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'Telepact production example' })).toBeVisible();

  const result = page.locator('#result');
  const observability = page.locator('#observability');

  await page.getByRole('button', { name: 'Load dashboard' }).click();
  await expect(result).toContainText('ErrorUnauthenticated_');
  await expect(result).toContainText('missing or invalid session cookie');

  await page.getByRole('button', { name: 'Sign in as viewer' }).click();
  await expect(result).toContainText('"role": "viewer"');

  await page.getByRole('button', { name: 'Load dashboard' }).click();
  await expect(result).toContainText('Casey Viewer');
  await expect(result).toContainText('Canary deployment remains healthy');

  await page.getByRole('button', { name: 'Load admin audit' }).click();
  await expect(result).toContainText('ErrorUnauthorized_');

  await page.getByRole('button', { name: 'Sign in as admin' }).click();
  await expect(result).toContainText('"role": "admin"');

  await page.getByRole('button', { name: 'Load admin audit' }).click();
  await expect(result).toContainText('role-change review queue is empty');

  await page.getByRole('button', { name: 'Trigger crash' }).click();
  await expect(result).toContainText('ErrorUnknown_');

  await page.getByRole('button', { name: 'Refresh observability' }).click();
  await expect(observability).toContainText('fn.viewerDashboard');
  await expect(observability).toContainText('fn.adminAudit');
  await expect(observability).toContainText('fn.debugCrash');
  await expect(observability).toContainText('exception');
});
