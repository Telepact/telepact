import commonjs from '@rollup/plugin-commonjs';

export default {
    input: 'node_modules/msgpackr/index.js', // Entry point for the dependency
    output: {
        file: 'dist/msgpackr.iife.js',
        format: 'iife',
        name: 'msgpackr',
        sourcemap: true,
    },
    plugins: [commonjs()],
};
