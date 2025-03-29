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

import { defineConfig } from 'vite';
import { resolve } from 'path';
import { promises as fs } from 'fs';

async function copyDir(src, dest) {
    await fs.mkdir(dest, { recursive: true });
    const entries = await fs.readdir(src, { withFileTypes: true });
  
    for (const entry of entries) {
      const srcPath = resolve(src, entry.name);
      const destPath = resolve(dest, entry.name);
  
      if (entry.isDirectory()) {
        await copyDir(srcPath, destPath);
      } else {
        await fs.copyFile(srcPath, destPath);
      }
    }
  }
  
  function copyFiles() {
    return {
      name: 'copy-files',
      writeBundle: async () => {
        const srcDir = resolve(__dirname, 'node_modules/telepact-console/build');
        const destDir = resolve(__dirname, 'dist');
        await copyDir(srcDir, destDir);
        //throw new Error('Interrupted');
      },
    };
  }

export default defineConfig({
  build: {
    rollupOptions: {
      input: './override.js',
      output: {
        entryFileNames: 'override.js',
        dir: resolve(__dirname, 'dist'),
      },
    },
  },
  plugins: [
    copyFiles()
  ],
  server: {
    port: 9000,
  },
});
