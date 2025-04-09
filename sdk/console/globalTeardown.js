import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Resolve __dirname for ES module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const VERSION = fs.readFileSync(path.resolve(__dirname, '../../VERSION.txt'), 'utf-8').trim();

export default async () => {
	try {
		execSync(`docker rm -f $(docker ps -q --filter ancestor=telepact-console:${VERSION})`, { stdio: 'inherit' });
	} catch (error) {
		console.error('Error during global teardown:', error);
	}
};
