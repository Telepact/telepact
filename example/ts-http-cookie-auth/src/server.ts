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

import { createServer, IncomingMessage, Server as HttpServer, ServerResponse } from 'node:http';
import * as fs from 'node:fs';
import * as path from 'node:path';
import { FunctionRouter, Message, Server, ServerOptions, TelepactSchema, TelepactSchemaFiles } from 'telepact';

const VALID_SESSION = 'demo-session';

function readCookie(request: IncomingMessage, name: string): string | null {
    const cookieHeader = request.headers.cookie;
    if (!cookieHeader) {
        return null;
    }

    for (const entry of cookieHeader.split(';')) {
        const [key, value] = entry.trim().split('=', 2);
        if (key === name && value) {
            return decodeURIComponent(value);
        }
    }

    return null;
}

function collectRequestBytes(request: IncomingMessage): Promise<Uint8Array> {
    return new Promise((resolve, reject) => {
        const chunks: Buffer[] = [];
        request.on('data', (chunk) => chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk)));
        request.on('end', () => resolve(new Uint8Array(Buffer.concat(chunks))));
        request.on('error', reject);
    });
}

export function createExampleServer(): HttpServer {
    const files = new TelepactSchemaFiles('api', fs, path);
    const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
    const options = new ServerOptions();
    const functionRouter = new FunctionRouter();
    options.authRequired = false;
    options.onAuth = (headers) => {
        const auth = headers['@auth_'] as Record<string, string> | undefined;
        if (!auth || auth.sessionToken !== VALID_SESSION) {
            return {};
        }
        return { '@userId': 'user-123' };
    };

    functionRouter.registerAuthenticated('fn.me', async (headers) => {
        const userId = headers['@userId'];
        if (userId !== 'user-123') {
            return new Message({}, {
                ErrorUnauthenticated_: { 'message!': 'missing or invalid session cookie' },
            });
        }
        return new Message({}, {
            Ok_: { userId },
        });
    });

    options.middleware = async (requestMessage, router) => {
        if (requestMessage.headers['@userId'] !== 'user-123') {
            return new Message({}, {
                ErrorUnauthenticated_: { 'message!': 'missing or invalid session cookie' },
            });
        }
        return await router.route(requestMessage);
    };

    const telepactServer = new Server(schema, functionRouter, options);

    return createServer(async (request: IncomingMessage, response: ServerResponse) => {
        if (request.method !== 'POST' || request.url !== '/api/telepact') {
            response.writeHead(404);
            response.end();
            return;
        }

        try {
            const requestBytes = await collectRequestBytes(request);
            const sessionToken = readCookie(request, 'session');
            const overrideHeaders = sessionToken ? { '@auth_': { sessionToken } } : {};
            const telepactResponse = await telepactServer.process(requestBytes, overrideHeaders);
            const contentType = '@bin_' in telepactResponse.headers
                ? 'application/octet-stream'
                : 'application/json';
            response.writeHead(200, { 'content-type': contentType });
            response.end(Buffer.from(telepactResponse.bytes));
        } catch (error) {
            response.writeHead(500, { 'content-type': 'text/plain; charset=utf-8' });
            response.end(String(error));
        }
    });
}
