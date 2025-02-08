import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import path from 'path';

const stub = path.resolve(__dirname, 'stub.js');

export default defineConfig({
	plugins: [sveltekit()],
	optimizeDeps: {
		include: ['../../lib/ts']
	},
	build: {
		commonjsOptions: {
			include: [/lib/, /node_modules/]
		}
	},
	resolve: {
		alias: {
			fs: stub,
			module: stub
		}
	}
});
