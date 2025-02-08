import typescript from '@rollup/plugin-typescript';
import json from '@rollup/plugin-json';

export default {
    input: 'src/index.ts',
    output: [
        {
            file: 'dist/index.cjs.js',
            format: 'cjs',
            sourcemap: true,
        },
        {
            file: 'dist/index.esm.js',
            format: 'es',
            sourcemap: true,
        },
    ],
    plugins: [typescript(), json()],
    external: ['fs', 'path', 'msgpackr', 'crc-32'], // Mark these dependencies as external
};
