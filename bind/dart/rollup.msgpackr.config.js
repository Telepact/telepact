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
        file: "rollup/msgpackr.iife.js",
        format: "iife",
        name: "msgpackr",
        sourcemap: true,
        banner: `/*

${license}
*/

/*
    This file is an IIFE bundle of the npm package \`msgpackr\`.
*/
`,
    },
    plugins: [commonjs()],
};
