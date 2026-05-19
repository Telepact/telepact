//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { defineConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Resolve __dirname for ES module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const VERSION = fs.readFileSync(path.resolve(__dirname, '../../VERSION.txt'), 'utf-8').trim();

export default defineConfig({
  testDir: './tests',
  timeout: 60 * 1000, // 1 minute
	webServer: [
		{
			command: `docker run --name telepact_console_self_host_test -p 8082:8080 telepact-console-self-host:${VERSION}`,
			port: 8082,
		}
	],
  globalTeardown: path.resolve(__dirname, 'teardown.js')
});
