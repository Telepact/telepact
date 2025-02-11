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
        const srcDir = resolve(__dirname, 'node_modules/uapi-console/build');
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
