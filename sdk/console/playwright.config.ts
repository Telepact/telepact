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

import type { PlaywrightTestConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Resolve __dirname for ES module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const VERSION = fs.readFileSync(path.resolve(__dirname, '../../VERSION.txt'), 'utf-8').trim();

const config: PlaywrightTestConfig = {
	webServer: [
		{
			command: `docker run telepact-console:${VERSION}`,
			port: 3001
		},
		{
			command: 'telepact mock --port 8085 --dir tests/schema --generated-collection-length-min 2 --generated-collection-length-max 2',
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
