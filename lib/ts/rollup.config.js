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

import typescript from "@rollup/plugin-typescript";
import json from "@rollup/plugin-json";
import fs from "fs";
import path from "path";

const stripLicensePlugin = () => {
    return {
      name: 'strip-license-plugin',
      transform(code, id) {
        const lines = code.split('\n');
        const filteredLines = lines.filter(line => !line.trim().startsWith('//|'));
        return {
          code: filteredLines.join('\n'),
          map: null,
        };
      },
    };
  };

const licenseHeader = fs.readFileSync(path.resolve("rollup.config.js"), "utf-8")
    .split("\n")
    .filter(line => line.startsWith("//|"))
    .join("\n") + '\n';

export default {
    input: "src/index.ts",
    output: [
        {
            file: "dist/index.cjs.js",
            format: "cjs",
            banner: licenseHeader
        },
        {
            file: "dist/index.esm.js",
            format: "es",
            banner: licenseHeader
        },
        {
            file: "dist/index.iife.js",
            format: "iife",
            name: "Telepact",
            banner: licenseHeader
        },
    ],
    plugins: [stripLicensePlugin(), typescript(), json()],
    external: ["msgpackr", "crc-32"],
};
