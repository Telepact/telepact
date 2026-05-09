//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import * as fs from 'node:fs';
import * as path from 'node:path';
import { once } from 'node:events';
import { FunctionRouter, Message, Server, ServerOptions, TelepactSchema, TelepactSchemaFiles } from 'telepact';
import { WebSocket, WebSocketServer } from 'ws';
import type { RawData } from 'ws';

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
