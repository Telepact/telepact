/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
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
	plugins: [require('@tailwindcss/forms')]
};
