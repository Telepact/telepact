//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { defineConfig } from '@playwright/test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const serverPython = path.resolve(__dirname, '../server/.venv/bin/python');
const serverEntrypoint = path.resolve(__dirname, '../server/app.py');
const port = 4173;
const TEST_TIMEOUT_MS = 60 * 1000;

export default defineConfig({
  testDir: './tests',
  timeout: TEST_TIMEOUT_MS,
  use: {
    baseURL: `http://127.0.0.1:${port}`,
  },
  webServer: {
    command: `${serverPython} ${serverEntrypoint} --host 127.0.0.1 --port ${port}`,
    port,
    reuseExistingServer: !process.env.CI,
  },
});
