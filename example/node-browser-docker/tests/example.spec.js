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

import { execFileSync } from 'node:child_process';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import { test, expect } from '@playwright/test';

const exampleDir = path.resolve(process.cwd());
const composeArgs = ['compose', '-f', path.join(exampleDir, 'docker-compose.yml')];

function dockerCompose(...args) {
  execFileSync('docker', [...composeArgs, ...args], {
    cwd: exampleDir,
    stdio: 'inherit',
  });
}

test.beforeAll(async () => {
  dockerCompose('down', '-v', '--remove-orphans');
  dockerCompose('up', '--build', '-d');
  await new Promise((resolve) => setTimeout(resolve, 5000));
});

test.afterAll(async () => {
  dockerCompose('down', '-v', '--remove-orphans');
});

test('runs the browser + node + docker flow end to end', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Telepact browser + Node + Docker example' })).toBeVisible();

  await page.getByRole('button', { name: '2. Load dashboard with @select_' }).click();
  await expect(page.locator('#dashboard-output')).toContainText('ErrorUnauthenticated_');

  await page.getByRole('button', { name: '1. Start demo session' }).click();
  await expect(page.locator('#session-status')).toContainText('demo-session');

  await page.getByRole('button', { name: '2. Load dashboard with @select_' }).click();
  await expect(page.locator('#dashboard-output')).toContainText('Ada Lovelace');
  await expect(page.locator('#dashboard-output')).toContainText('order-1001');
  await expect(page.locator('#dashboard-output')).toContainText('packing');
  await expect(page.locator('#dashboard-output')).not.toContainText('2599');
  await expect(page.locator('#dashboard-output')).toContainText('firstOrderDetails!');

  await page.getByRole('button', { name: '3. Follow function link' }).click();
  await expect(page.locator('#details-output')).toContainText('shippingEta');
  await expect(page.locator('#details-output')).toContainText('cmVjZWlwdDp');
  await expect(page.locator('#binary-status')).not.toContainText(': 0');

  const fetchedDir = fs.mkdtempSync(path.join(os.tmpdir(), 'telepact-node-browser-docker-'));
  execFileSync('telepact', [
    'fetch',
    '--http-url',
    'http://127.0.0.1:8080/api/telepact',
    '--output-dir',
    fetchedDir,
  ], {
    cwd: exampleDir,
    stdio: 'inherit',
  });
  execFileSync('telepact', [
    'compare',
    '--old-schema-dir',
    path.join(exampleDir, 'gateway-api'),
    '--new-schema-dir',
    fetchedDir,
  ], {
    cwd: exampleDir,
    stdio: 'inherit',
  });
});
