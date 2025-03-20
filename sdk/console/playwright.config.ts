import type { PlaywrightTestConfig } from '@playwright/test';

const config: PlaywrightTestConfig = {
	webServer: [
		{
			command: 'npm run dev',
			port: 5173,
			reuseExistingServer: !process.env.CI
		},
		{
			command: 'msgpact mock --dir tests/schema',
			port: 8080,
			reuseExistingServer: !process.env.CI,
			stdout: 'pipe'
		}
	],
	testDir: 'tests',
	testMatch: /(.+\.)?(test|spec)\.[jt]s/,
	use: {
		baseURL: 'http://localhost:5173',
		contextOptions: {
			permissions: ['clipboard-read']
		}
	}
};

export default config;
