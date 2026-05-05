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

import { Serializer } from '../Serializer.js';
import { TelepactSchema } from '../TelepactSchema.js';
import { Message } from '../Message.js';
import { handleMessage } from '../internal/HandleMessage.js';
import { parseRequestMessage } from '../internal/ParseRequestMessage.js';
import { Response } from '../Response.js';
import { SerializationError } from '../SerializationError.js';
import { TelepactError } from '../TelepactError.js';
import { UpdateHeaders } from '../Server.js';
import { buildUnknownErrorMessage } from './UnknownError.js';

export type ErrorHandler = (error: TelepactError) => void;
export type RequestHandler = (message: Message) => void;
export type ResponseHandler = (message: Message) => void;
export type AuthHandler = (headers: Record<string, any>) => Record<string, any> | Promise<Record<string, any>>;
export type FunctionRouter = {
    route: (message: Message) => Promise<Message>;
    requiresAuthentication: (functionName: string) => boolean;
};
export type Middleware = (requestMessage: Message, functionRouter: FunctionRouter) => Promise<Message>;

export async function processBytes(
    requestMessageBytes: Uint8Array,
    updateHeaders: UpdateHeaders | undefined,
    serializer: Serializer,
    telepactSchema: TelepactSchema,
    onError: ErrorHandler,
    onRequest: RequestHandler,
    onResponse: ResponseHandler,
    onAuth: AuthHandler,
    middleware: Middleware,
    functionRouter: FunctionRouter,
): Promise<Response> {
    try {
        const requestMessage = parseRequestMessage(requestMessageBytes, serializer, telepactSchema, onError);

        try {
            onRequest(requestMessage);
        } catch (error) {
            // Handle error
        }

        const responseMessage = await handleMessage(
            requestMessage,
            updateHeaders,
            telepactSchema,
            middleware,
            functionRouter,
            onError,
            onAuth,
        );

        try {
            onResponse(responseMessage);
        } catch (error) {
            // Handle error
        }

        let responseBytes: Uint8Array;
        try {
            responseBytes = serializer.serialize(responseMessage);
        } catch (error) {
            const wrapped = error instanceof SerializationError
                ? new TelepactError('telepact response serialization failed', 'serialization', error)
                : new TelepactError('telepact server processing failed while serializing the response', 'serialization', error);
            try {
                onError(wrapped);
            } catch (error) {
                // Handle error
            }
            const unknownResponseBytes = serializer.serialize(buildUnknownErrorMessage(wrapped));
            return { bytes: unknownResponseBytes, headers: {} };
        }

        return { bytes: responseBytes, headers: responseMessage.headers };
    } catch (error) {
        const wrapped = error instanceof TelepactError
            ? error
            : error instanceof SerializationError
                ? new TelepactError('telepact response serialization failed', 'serialization', error)
                : new TelepactError('telepact server processing failed', undefined, error);
        try {
            onError(wrapped);
        } catch (error) {
            // Handle error
        }

        const responseBytes = serializer.serialize(buildUnknownErrorMessage(wrapped));

        return { bytes: responseBytes, headers: {} };
    }
}
