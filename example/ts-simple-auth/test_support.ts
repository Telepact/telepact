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

export type RunningPythonServer = {
    process: ChildProcessWithoutNullStreams;
    url: string;
};

export async function runPythonServer(): Promise<RunningPythonServer> {
    const python = path.join(process.cwd(), '.venv', 'bin', 'python');
    const child = spawn(python, ['server.py', '--port', '0'], {
        cwd: process.cwd(),
        stdio: ['ignore', 'pipe', 'pipe'],
    });

    let stderr = '';
    child.stderr.setEncoding('utf8');
    child.stderr.on('data', (chunk: string) => {
        stderr += chunk;
    });

    const port = await new Promise<number>((resolve, reject) => {
        child.stdout.setEncoding('utf8');
        child.stdout.on('data', (chunk: string) => {
            const match = chunk.match(/listening (\d+)/);
            if (match !== null) {
                resolve(Number.parseInt(match[1], 10));
            }
        });
        child.once('exit', (code, signal) => {
            reject(new Error(`python server exited early with code=${code} signal=${signal}\n${stderr}`));
        });
        child.once('error', reject);
    });

    return {
        process: child,
        url: `http://127.0.0.1:${port}/api/telepact`,
    };
}

export async function stopPythonServer(server: RunningPythonServer): Promise<void> {
    server.process.kill('SIGTERM');
    await once(server.process, 'exit');
}
