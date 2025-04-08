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

import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import fs from 'fs';
import path from 'path';
import { JSDOM } from 'jsdom';
import prettier from 'prettier';

let basePath = process.env.BASE_PATH || undefined;

export default defineConfig({
    plugins: [
        sveltekit(),
        {
            name: 'extract-app-root-script',
            apply: 'build',
            async closeBundle() {
                const htmlFilePath = path.resolve(__dirname, 'build/index.html');
                const outputScriptPath = path.resolve(__dirname, 'build/app-root-script.js');

                // Read the HTML file
                let htmlContent = fs.readFileSync(htmlFilePath, 'utf8');

                // Extract the comment block at the top of the file
                const commentBlockLines = htmlContent.split('\n').filter(line => line.startsWith('<!--|'));
                const commentBlock = commentBlockLines.join('\n') + '\n';

                // Remove the comment block from the HTML content before parsing
                if (commentBlock) {
                    htmlContent = htmlContent.replace(commentBlock, '');
                }

                // Parse the HTML content
                const dom = new JSDOM(htmlContent);
                const document = dom.window.document;

                // Find the script under id="app-root"
                const appRootDiv = document.querySelector('#app-root');
                const scriptElement = appRootDiv?.querySelector('script');

                if (!scriptElement) {
                    console.warn('No script found under #app-root');
                    return;
                }

                // Extract the script content
                const scriptContent = scriptElement.textContent?.trim() || '';

				const formattedScriptContent = await prettier.format(scriptContent, { parser: 'babel' });

                // Write the script content to a new .js file
                fs.writeFileSync(outputScriptPath, formattedScriptContent, 'utf8');
                console.log(`Script content extracted and saved to ${outputScriptPath}`);

                // Remove the script element from the HTML
                scriptElement.remove();

                // Update the HTML to reference the new script file
                const newScriptElement = document.createElement('script');
				if (basePath) {
                	newScriptElement.src = `${basePath}/app-root-script.js`;
				} else {
					newScriptElement.src = `./app-root-script.js`;
				}
                appRootDiv.appendChild(newScriptElement);

                // Serialize the updated HTML
                let updatedHtmlContent = dom.serialize();

                // Use Prettier to format the HTML
                updatedHtmlContent = await prettier.format(updatedHtmlContent, { parser: 'html' });

                // Prepend the comment block
                updatedHtmlContent = commentBlock + updatedHtmlContent;

                // Write the updated HTML back to the file
                fs.writeFileSync(htmlFilePath, updatedHtmlContent, 'utf8');
                console.log(`HTML file updated and pretty-printed.`);
            }
        }
    ],
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
