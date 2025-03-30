import { defineConfig, devices } from '@playwright/test';
import { spawn } from 'child_process';

export default defineConfig({
  testDir: './tests',
  timeout: 60 * 1000, // 1 minute
  webServer: {
    command: 'npm run serve',
    port: 5173
  },
});
