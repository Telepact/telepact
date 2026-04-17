import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const packageRoot = dirname(fileURLToPath(import.meta.url));

export const selfHostedRoot = resolve(packageRoot, 'build');
export const selfHostedIndexHtml = resolve(selfHostedRoot, 'index.html');
export const selfHostedOverrideJs = resolve(selfHostedRoot, 'override.js');

export default {
	selfHostedRoot,
	selfHostedIndexHtml,
	selfHostedOverrideJs
};
