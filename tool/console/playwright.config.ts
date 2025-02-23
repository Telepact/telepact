import type { PlaywrightTestConfig } from '@playwright/test';

const config: PlaywrightTestConfig = {
	webServer: [
		{
			command: 'npm run dev',
			port: 5173,
			reuseExistingServer: !process.env.CI
		},
		{
			command: 'uapi_example',
			port: 8000,
			reuseExistingServer: !process.env.CI,
			stdout: 'pipe'
		}
	],
	testDir: 'tests',
	testMatch: /(.+\.)?(test|spec)\.[jt]s/,
	use: {
		baseURL: 'http://localhost:5173'
	}
};

export default config;
