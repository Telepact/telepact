//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
	base: './',
	publicDir: 'static',
    plugins: [
		tailwindcss(),
		react()
    ],
	build: {
		outDir: 'build',
		commonjsOptions: {
			include: [/lib/, /node_modules/]
		}
	},
	resolve: {
		alias: { fs: 'data:text/javascript,export default {};' }
	},
});
