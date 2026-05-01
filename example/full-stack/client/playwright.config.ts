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

import { defineConfig } from '@playwright/test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const serverPython = path.resolve(__dirname, '../server/.venv/bin/python');
const serverEntrypoint = path.resolve(__dirname, '../server/app.py');
const port = 4173;

export default defineConfig({
  testDir: './tests',
  timeout: 60 * 1000,
  use: {
    baseURL: `http://127.0.0.1:${port}`,
  },
  webServer: {
    command: `${serverPython} ${serverEntrypoint} --host 127.0.0.1 --port ${port}`,
    port,
    reuseExistingServer: !process.env.CI,
  },
});
