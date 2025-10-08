#!/usr/bin/env node

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

import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import { Command } from 'commander';

const program = new Command();

program
    .description('The Telepact Console is a web-based interface for inspecting and testing Telepact APIs.')
    .option('-p, --port <number>', 'port number', process.env.PORT || '4173')
    .option('-d, --debug', 'enable additional logging', false)
    .parse(process.argv);

const options = program.opts();
const port = parseInt(options.port, 10);

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PORT = port;
const BUILD_DIR = resolve(__dirname, 'build');

const app = express();

app.use('/', express.static(BUILD_DIR, {
	fallthrough: false
}));

app.use((err, req, res, next) => {
    if (err.code === 'ENOENT') {
        if (options.debug) {
            console.error(`File not found: ${req.path}`);
        }
        res.status(404).send('Not Found');
    } else {
        next(err);
    }
});

app.listen(PORT, () => {
    console.log(`Server running. Access at http://localhost:${PORT}`);
});
