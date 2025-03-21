import typescript from "@rollup/plugin-typescript";
import json from "@rollup/plugin-json";

export default {
    input: "src/index.ts",
    output: [
        {
            file: "dist/index.cjs.js",
            format: "cjs",
        },
        {
            file: "dist/index.esm.js",
            format: "es",
        },
        {
            file: "dist/index.iife.js",
            format: "iife",
            name: "Telepact",
        },
    ],
    plugins: [typescript(), json()],
    external: ["msgpackr", "crc-32"],
};
