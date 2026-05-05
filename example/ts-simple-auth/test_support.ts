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

import { ChildProcessWithoutNullStreams, spawn } from 'node:child_process';
import { once } from 'node:events';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export type PythonServer = {
    process: ChildProcessWithoutNullStreams;
    port: number;
    stdout(): string;
    stderr(): string;
};

function delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function startPythonServer(): Promise<PythonServer> {
    const here = path.dirname(fileURLToPath(import.meta.url));
    const cwd = path.resolve(here, '..');
    const python = path.join(cwd, '.venv', 'bin', 'python');
    const script = path.join(cwd, 'server.py');
    const child = spawn(python, ['-u', script, '--port', '0'], { cwd }) as ChildProcessWithoutNullStreams;

    let stdout = '';
    let stderr = '';

    child.stdout.setEncoding('utf8');
    child.stdout.on('data', (chunk: string) => {
        stdout += chunk;
    });

    child.stderr.setEncoding('utf8');
    child.stderr.on('data', (chunk: string) => {
        stderr += chunk;
    });

    const startedAt = Date.now();
    while (Date.now() - startedAt < 10000) {
        const ready = stdout.match(/READY (\d+)/);
        if (ready) {
            return {
                process: child,
                port: Number(ready[1]),
                stdout: () => stdout,
                stderr: () => stderr,
            };
        }
        if (child.exitCode !== null) {
            throw new Error(`python server exited early: ${stderr || stdout}`);
        }
        await delay(50);
    }

    child.kill('SIGTERM');
    await once(child, 'exit');
    throw new Error(`timed out waiting for python server: ${stderr || stdout}`);
}

export async function stopPythonServer(server: PythonServer): Promise<void> {
    if (server.process.exitCode !== null) {
        return;
    }

    server.process.kill('SIGTERM');
    await once(server.process, 'exit');
}

export async function waitForLog(server: PythonServer, text: string): Promise<void> {
    const startedAt = Date.now();
    while (Date.now() - startedAt < 10000) {
        if (server.stdout().includes(text)) {
            return;
        }
        if (server.process.exitCode !== null) {
            throw new Error(`python server exited while waiting for log: ${server.stderr() || server.stdout()}`);
        }
        await delay(50);
    }

    throw new Error(`timed out waiting for log ${JSON.stringify(text)} in ${server.stdout()}`);
}

export async function postBytes(url: string, requestBytes: Uint8Array): Promise<Uint8Array> {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: Buffer.from(requestBytes),
    });
    return new Uint8Array(await response.arrayBuffer());
}
