//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { createServer, IncomingMessage, Server as HttpServer, ServerResponse } from 'node:http';
import * as fs from 'node:fs';
import * as path from 'node:path';
import { FunctionRouter, Server, ServerOptions, TelepactSchema, TelepactSchemaFiles } from 'telepact';
import type { Response, TypedMessage } from 'telepact';
import { GreetInput, GreetOutput, TypedServerHandler, greet } from './gen/genTypes.js';

const files = new TelepactSchemaFiles('api', fs, path);
const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
const options = new ServerOptions();
options.authRequired = false;

class GreetingHandler extends TypedServerHandler {
    async greet(_headers: Record<string, any>, input: GreetInput): Promise<TypedMessage<GreetOutput>> {
        return {
            headers: {},
            body: greet.Output.from_Ok_({
                message: `Hello ${input.subject()} from generated code!`,
            }),
        };
    }
}

const functionRouter = new FunctionRouter(new GreetingHandler().functionRoutes());
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
