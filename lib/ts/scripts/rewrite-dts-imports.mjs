import { readdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

const DISTSRC = path.resolve('dist/src');

const shouldRewrite = (specifier) => specifier.startsWith('.') && !specifier.endsWith('.js') && !specifier.endsWith('.json');

const rewriteText = (text) => text
  .replaceAll(/from\s+(['"])(\.[^'"]+)\1/g, (match, quote, specifier) => {
    return shouldRewrite(specifier) ? `from ${quote}${specifier}.js${quote}` : match;
  })
  .replaceAll(/import\((['"])(\.[^'"]+)\1\)/g, (match, quote, specifier) => {
    return shouldRewrite(specifier) ? `import(${quote}${specifier}.js${quote})` : match;
  });

async function walk(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      await walk(fullPath);
      continue;
    }
    if (!entry.isFile() || !fullPath.endsWith('.d.ts')) continue;
    const original = await readFile(fullPath, 'utf8');
    const rewritten = rewriteText(original);
    if (rewritten !== original) {
      await writeFile(fullPath, rewritten);
    }
  }
}

await walk(DISTSRC);