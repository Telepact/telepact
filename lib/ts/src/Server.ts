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

import { DefaultSerialization } from './DefaultSerialization.js';
import { Serializer } from './Serializer.js';
import { ServerBinaryEncoder } from './internal/binary/ServerBinaryEncoder.js';
import { Message } from './Message.js';
import { TelepactSchema } from './TelepactSchema.js';
import { constructBinaryEncoding } from './internal/binary/ConstructBinaryEncoding.js';
import { processBytes } from './internal/ProcessBytes.js';
import { Serialization } from './Serialization.js';
import { ServerBase64Encoder } from './internal/binary/ServerBase64Encoder.js';
import { Response } from './Response.js';
import { FunctionRouter, FunctionRoutes } from './FunctionRouter.js';
import { createInternalFunctionRoutes } from './internal/CreateInternalFunctionRoutes.js';
import { TelepactError } from './TelepactError.js';

export type Middleware = (requestMessage: Message, functionRouter: FunctionRouter) => Promise<Message>;
export type AuthHandler = (headers: Record<string, any>) => Record<string, any> | Promise<Record<string, any>>;
export type UpdateHeaders = (headers: Record<string, any>) => void;
export { FunctionRouter } from './FunctionRouter.js';
export type { FunctionRoute, FunctionRoutes } from './FunctionRouter.js';

export class Server {
    functionRouter: FunctionRouter;
    middleware: Middleware;
    onError: (error: TelepactError) => void;
    onRequest: (message: Message) => void;
    onResponse: (message: Message) => void;
    onAuth: AuthHandler;
    telepactSchema: TelepactSchema;
    serializer: Serializer;

    constructor(telepactSchema: TelepactSchema, functionRouter: FunctionRouter | FunctionRoutes, options: ServerOptions) {
        const normalizedFunctionRouter =
            functionRouter instanceof FunctionRouter ? functionRouter : new FunctionRouter(functionRouter);

        normalizedFunctionRouter.functionRoutes = {
            ...normalizedFunctionRouter.functionRoutes,
            ...createInternalFunctionRoutes(telepactSchema),
        };
        this.functionRouter = normalizedFunctionRouter;
        this.middleware = options.middleware;
        this.onError = options.onError;
        this.onRequest = options.onRequest;
        this.onResponse = options.onResponse;
        this.onAuth = options.onAuth;

        this.telepactSchema = telepactSchema;

        const binaryEncoding = constructBinaryEncoding(this.telepactSchema);
        const binaryEncoder = new ServerBinaryEncoder(binaryEncoding);
        const base64Encoder = new ServerBase64Encoder();

        this.serializer = new Serializer(options.serialization, binaryEncoder, base64Encoder);

        if (!('union.Auth_' in this.telepactSchema.parsed) && options.authRequired) {
            throw new Error(
                'Unauthenticated server. Either define a `union.Auth_` in your schema or set `options.authRequired` to `false`.',
            );
        }
    }

    async process(requestMessageBytes: Uint8Array, updateHeaders?: UpdateHeaders): Promise<Response> {
        return await processBytes(
            requestMessageBytes,
            updateHeaders,
            this.serializer,
            this.telepactSchema,
            this.onError,
            this.onRequest,
            this.onResponse,
            this.onAuth,
            this.middleware,
            this.functionRouter,
        );
    }
}

export class ServerOptions {
    onError: (error: TelepactError) => void;
    onRequest: (message: Message) => void;
    onResponse: (message: Message) => void;
    onAuth: AuthHandler;
    middleware: Middleware;
    authRequired: boolean;
    serialization: Serialization;

    constructor() {
        this.onError = (_error: TelepactError) => {};
        this.onRequest = (m: Message) => {};
        this.onResponse = (m: Message) => {};
        this.onAuth = (headers: Record<string, any>) => ({});
        this.middleware = async (requestMessage: Message, functionRouter: FunctionRouter): Promise<Message> =>
            await functionRouter.route(requestMessage);
        this.authRequired = true;
        this.serialization = new DefaultSerialization();
    }
}
