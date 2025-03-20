import type { PlaywrightTestConfig } from '@playwright/test';

const config: PlaywrightTestConfig = {
	webServer: [
		{
			command: 'npm run dev:test',
			port: 3001
		},
		{
			command: 'msgpact mock --port 8085 --dir tests/schema --generated-collection-length-min 2 --generated-collection-length-max 2',
			port: 8085,
			stdout: 'pipe'
		}
	],
	testDir: 'tests',
	testMatch: /(.+\.)?(test|spec)\.[jt]s/,
	use: {
		baseURL: 'http://localhost:3001',
		contextOptions: {
			permissions: ['clipboard-read']
		}
	}
};

export default config;
