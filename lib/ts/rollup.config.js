//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import commonjs from "@rollup/plugin-commonjs";
import json from "@rollup/plugin-json";
import nodeResolve from "@rollup/plugin-node-resolve";
import typescript from "@rollup/plugin-typescript";
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
    plugins: [stripLicensePlugin(), nodeResolve(), commonjs(), typescript(), json()],
    external: ["msgpackr", "crc-32"],
};
