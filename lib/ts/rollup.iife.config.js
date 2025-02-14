import typescript from '@rollup/plugin-typescript';
import json from '@rollup/plugin-json';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';

export default {
    input: 'src/index.ts',
    output: {
        file: 'dist/index.iife.js',
        format: 'iife',
        name: 'UApi',
        sourcemap: true,
    },
    plugins: [resolve(), commonjs(), typescript(), json()],
    // Do not mark dependencies as external to include them in the bundle
};
