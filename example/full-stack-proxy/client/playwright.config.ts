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
const serverBinary = path.resolve(__dirname, '../server/bin/full-stack-proxy-server');
const apiDir = path.resolve(__dirname, '../api');
const proxyPython = path.resolve(__dirname, '../proxy/.venv/bin/python');
const proxyEntrypoint = path.resolve(__dirname, '../proxy/app.py');
const port = 4173;
const natsPort = 4222;
const healthPort = 8413;
const TEST_TIMEOUT_MS = 60 * 1000;

export default defineConfig({
  testDir: './tests',
  timeout: TEST_TIMEOUT_MS,
  use: {
    baseURL: `http://127.0.0.1:${port}`,
  },
  webServer: [
    {
      command: 'nats-server -D',
      port: natsPort,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: `${serverBinary} --nats-url nats://127.0.0.1:${natsPort} --subject rpc.demo.greet --api-dir ${apiDir} --health-port ${healthPort}`,
      port: healthPort,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: `${proxyPython} ${proxyEntrypoint} --host 127.0.0.1 --port ${port} --nats-url nats://127.0.0.1:${natsPort}`,
      port,
      reuseExistingServer: !process.env.CI,
    },
  ],
});
