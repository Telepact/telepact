import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

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
		alias: { fs: 'data:text/javascript,export default {};' }
	},
	server: {
		fs: {
			allow: ['stub.js']
		}
	}
});
