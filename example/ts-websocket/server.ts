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

import * as fs from 'node:fs';
import * as path from 'node:path';
import { once } from 'node:events';
import { FunctionRouter, Message, Server, ServerOptions, TelepactSchema, TelepactSchemaFiles } from 'telepact';
import { RawData, WebSocket, WebSocketServer } from 'ws';

const files = new TelepactSchemaFiles('api', fs, path);
const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
const options = new ServerOptions();
options.authRequired = false;

async function greet(functionName: string, requestMessage: Message): Promise<Message> {
    const argument = requestMessage.body[functionName] as Record<string, string>;
    const subject = argument['subject'];
    return new Message({}, {
        'Ok_': {
            'message': `Hello ${subject} from WebSocket!`,
        },
    });
}

const functionRouter = new FunctionRouter({ 'fn.greet': greet });
const telepactServer = new Server(schema, functionRouter, options);

function rawDataToBytes(data: RawData): Uint8Array {
    if (typeof data === 'string') {
        return new TextEncoder().encode(data);
    }
    if (data instanceof ArrayBuffer) {
        return new Uint8Array(data);
    }
    if (Array.isArray(data)) {
        return new Uint8Array(Buffer.concat(data));
    }
    return new Uint8Array(data);
}

export async function createWebSocketServer(host = '127.0.0.1', port = 0): Promise<WebSocketServer> {
    const server = new WebSocketServer({ host, port, path: '/ws/telepact' });
    server.on('connection', (websocket: WebSocket) => {
        websocket.on('message', (data: RawData, isBinary: boolean) => {
            void (async () => {
                const response = await telepactServer.process(rawDataToBytes(data));
                if (isBinary) {
                    websocket.send(response.bytes);
                    return;
                }
                websocket.send(Buffer.from(response.bytes).toString('utf-8'));
            })().catch((error: unknown) => {
                websocket.close(1011, String(error));
            });
        });
    });
    await once(server, 'listening');
    return server;
}
