//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

/** @type {import('tailwindcss').Config} */
export default {
	darkMode: 'class',
	content: ['./index.html', './src/**/*.{html,js,jsx,ts,tsx}'],
	theme: {
		extend: {
			colors: {
				vsBackground: '#1e1e1e'
			},
			flexGrow: {
				4: '4',
				8: '8'
			}
		}
	},
	plugins: [require('@tailwindcss/forms'), require('@tailwindcss/typography')]
};
