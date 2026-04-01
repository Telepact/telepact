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

import { createServer, Server as HttpServer } from 'node:http';
import * as fs from 'node:fs';
import * as path from 'node:path';
import { RawData, WebSocketServer } from 'ws';
import { Message, Server, ServerOptions, TelepactSchema, TelepactSchemaFiles } from 'telepact';

function delay(milliseconds: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

function toUint8Array(data: RawData): Uint8Array {
    if (data instanceof ArrayBuffer) {
        return new Uint8Array(data);
    }

    if (Array.isArray(data)) {
        return new Uint8Array(Buffer.concat(data));
    }

    return new Uint8Array(data);
}

export function createExampleServer(): HttpServer {
    const files = new TelepactSchemaFiles('api', fs, path);
    const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
    const options = new ServerOptions();
    options.authRequired = false;

    const telepactServer = new Server(schema, async (message) => {
        if (message.getBodyTarget() !== 'fn.greet') {
            throw new Error(`Unknown function: ${message.getBodyTarget()}`);
        }

        const payload = message.getBodyPayload() as { subject: string; 'delayMs!'?: number };
        if (payload['delayMs!'] !== undefined) {
            await delay(payload['delayMs!']);
        }

        return new Message({}, {
            Ok_: {
                message: `Hello ${payload.subject}!`,
            },
        });
    }, options);

    const httpServer = createServer((_request, response) => {
        response.writeHead(404);
        response.end();
    });

    const websocketServer = new WebSocketServer({ server: httpServer, path: '/ws/telepact' });
    websocketServer.on('connection', (socket) => {
        socket.on('message', async (requestBytes: RawData) => {
            try {
                const telepactResponse = await telepactServer.process(toUint8Array(requestBytes));
                socket.send(Buffer.from(telepactResponse.bytes));
            } catch (error) {
                socket.close(1011, error instanceof Error ? error.message : String(error));
            }
        });
    });

    httpServer.on('close', () => websocketServer.close());
    return httpServer;
}
