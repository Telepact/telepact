//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { createServer, IncomingMessage, Server as HttpServer, ServerResponse } from 'node:http';
import * as fs from 'node:fs';
import * as path from 'node:path';
import { FunctionRouter, Message, Response, Server, ServerOptions, TelepactSchema, TelepactSchemaFiles } from 'telepact';

const files = new TelepactSchemaFiles('api', fs, path);
const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
const options = new ServerOptions();
options.authRequired = false;

async function trackPackage(_functionName: string, _requestMessage: Message): Promise<Message> {
    return new Message({}, {
        'Ok_': {
            'package': {
                'trackingId': 'PKG-42',
                'recipient': 'Ada Lovelace',
                'city': 'London',
            },
            'latestEvent': {
                'Dropoff': {
                    'location': 'Front desk',
                    'signedBy': 'M. Singh',
                },
            },
            'note': 'Left with building reception.',
        },
    });
}

const functionRouter = new FunctionRouter({ 'fn.trackPackage': trackPackage });
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
