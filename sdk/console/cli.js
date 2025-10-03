#!/usr/bin/env node

import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const args = process.argv.slice(2);
const portIndex = args.findIndex(arg => arg === '--port' || arg === '-p');
let port = process.env.PORT || 4173;

if (portIndex !== -1 && args[portIndex + 1]) {
    const parsedPort = parseInt(args[portIndex + 1], 10);
    if (!isNaN(parsedPort)) {
        port = parsedPort;
    }
}

const PORT = port;
const BUILD_DIR = resolve(__dirname, 'build');

const app = express();

app.use('/', express.static(BUILD_DIR));

app.use((req, res) => {
    res.sendFile(resolve(BUILD_DIR, 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running. Access at http://localhost:${PORT}`);
});
