import commonjs from '@rollup/plugin-commonjs';

export default {
    input: 'node_modules/crc-32/crc32.js', // Entry point for the dependency
    output: {
        file: 'dist/crc32.iife.js',
        format: 'iife',
        name: 'crc32',
        sourcemap: true,
    },
    plugins: [commonjs()],
};
