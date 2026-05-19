//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
const natsPort = 4322;
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
      command: `nats-server -D -p ${natsPort}`,
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
