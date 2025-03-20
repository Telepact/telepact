import commonjs from "@rollup/plugin-commonjs";
import fs from "fs";
import path from "path";

const license = fs
    .readFileSync(path.resolve("node_modules/msgpackr/LICENSE"), "utf-8")
    .split("\n")
    .map((line) => `    ${line}`)
    .join("\n");

export default {
    input: "node_modules/msgpackr/index.js", // Entry point for the dependency
    output: {
        file: "dist/msgpackr.iife.js",
        format: "iife",
        name: "msgpackr",
        sourcemap: true,
        banner: `/*

${license}
*/

/*
    This file is a Rollup redistribution of the original \`msgpackr\` npm package.
*/
`,
    },
    plugins: [commonjs()],
};
