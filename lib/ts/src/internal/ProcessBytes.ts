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

import { Serializer } from '../Serializer';
import { TelepactSchema } from '../TelepactSchema';
import { Message } from '../Message';
import { handleMessage } from '../internal/HandleMessage';
import { parseRequestMessage } from '../internal/ParseRequestMessage';

export type ErrorHandler = (error: any) => void;
export type RequestHandler = (message: Message) => void;
export type ResponseHandler = (message: Message) => void;
export type MessageHandler = (message: Message) => Promise<Message>;

export async function processBytes(
    requestMessageBytes: Uint8Array,
    overrideHeaders: Record<string, object>,
    serializer: Serializer,
    telepactSchema: TelepactSchema,
    onError: ErrorHandler,
    onRequest: RequestHandler,
    onResponse: ResponseHandler,
    handler: MessageHandler,
): Promise<Uint8Array> {
    try {
        const requestMessage = parseRequestMessage(requestMessageBytes, serializer, telepactSchema, onError);

        try {
            onRequest(requestMessage);
        } catch (error) {
            // Handle error
        }

        const responseMessage = await handleMessage(requestMessage, overrideHeaders, telepactSchema, handler, onError);

        try {
            onResponse(responseMessage);
        } catch (error) {
            // Handle error
        }

        return serializer.serialize(responseMessage);
    } catch (error) {
        try {
            onError(error);
        } catch (error) {
            // Handle error
        }

        return serializer.serialize(new Message({}, { ErrorUnknown_: {} }));
    }
}
