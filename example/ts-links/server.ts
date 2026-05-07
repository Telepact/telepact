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
import { FunctionRouter, Message, Response, Server, ServerOptions, TelepactSchema, TelepactSchemaFiles } from 'telepact';

const files = new TelepactSchemaFiles('api', fs, path);
const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
const options = new ServerOptions();
options.authRequired = false;

async function createIssueLink(functionName: string, requestMessage: Message): Promise<Message> {
    const argument = requestMessage.body[functionName] as Record<string, string>;
    const title = argument['title'];
    return new Message({}, {
        'Ok_': {
            'todo': {
                'title': title,
            },
            'next!': {
                'fn.getFollowUp': {
                    'id': 'follow-up-1',
                },
            },
        },
    });
}

async function getFollowUp(functionName: string, requestMessage: Message): Promise<Message> {
    const argument = requestMessage.body[functionName] as Record<string, string>;
    const followUpId = argument['id'];
    return new Message({}, {
        'Ok_': {
            'summary': `Followed up on ${followUpId}`,
        },
    });
}

const functionRouter = new FunctionRouter({
    'fn.createIssueLink': createIssueLink,
    'fn.getFollowUp': getFollowUp,
});
const telepactServer = new Server(schema, functionRouter, options);

function readRequestBytes(request: IncomingMessage): Promise<Uint8Array> {
    return new Promise((resolve, reject) => {
        const chunks: Buffer[] = [];
        request.on('data', (chunk) => {
            chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
        });
        request.on('end', () => resolve(new Uint8Array(Buffer.concat(chunks))));
        request.on('error', reject);
    });
}

function writeTelepactResponse(responseWriter: ServerResponse, response: Response): void {
    responseWriter.statusCode = 200;
    responseWriter.setHeader('Content-Type', '@bin_' in response.headers ? 'application/octet-stream' : 'application/json');
    responseWriter.end(Buffer.from(response.bytes));
}

export function createHttpServer(): HttpServer {
    return createServer((request, responseWriter) => {
        void (async () => {
            if (request.method !== 'POST' || request.url !== '/api/telepact') {
                responseWriter.statusCode = 404;
                responseWriter.end();
                return;
            }

            const requestBytes = await readRequestBytes(request);
            const response = await telepactServer.process(requestBytes);
            writeTelepactResponse(responseWriter, response);
        })().catch((error: unknown) => {
            responseWriter.statusCode = 500;
            responseWriter.end(String(error));
        });
    });
}
