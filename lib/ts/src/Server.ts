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

import { DefaultSerialization } from './DefaultSerialization';
import { Serializer } from './Serializer';
import { ServerBinaryEncoder } from './internal/binary/ServerBinaryEncoder';
import { Message } from './Message';
import { TelepactSchema } from './TelepactSchema';
import { constructBinaryEncoding } from './internal/binary/ConstructBinaryEncoding';
import { processBytes } from './internal/ProcessBytes';
import { Serialization } from './Serialization';
import { ServerBase64Encoder } from './internal/binary/ServerBase64Encoder';

export class Server {
    handler: (message: Message) => Promise<Message>;
    onError: (error: any) => void;
    onRequest: (message: Message) => void;
    onResponse: (message: Message) => void;
    telepactSchema: TelepactSchema;
    serializer: Serializer;

    constructor(telepactSchema: TelepactSchema, handler: (message: Message) => Promise<Message>, options: ServerOptions) {
        this.handler = handler;
        this.onError = options.onError;
        this.onRequest = options.onRequest;
        this.onResponse = options.onResponse;

        this.telepactSchema = telepactSchema;

        const binaryEncoding = constructBinaryEncoding(this.telepactSchema);
        const binaryEncoder = new ServerBinaryEncoder(binaryEncoding);
        const base64Encoder = new ServerBase64Encoder();

        this.serializer = new Serializer(options.serialization, binaryEncoder, base64Encoder);

        if (!('struct.Auth_' in this.telepactSchema.parsed) && options.authRequired) {
            throw new Error(
                'Unauthenticated server. Either define a non-empty `struct._Auth` in your schema or set `options.authRequired` to `false`.',
            );
        }
    }

    async process(requestMessageBytes: Uint8Array, overrideHeaders: Record<string, object> = {}): Promise<Uint8Array> {
        return await processBytes(
            requestMessageBytes,
            overrideHeaders,
            this.serializer,
            this.telepactSchema,
            this.onError,
            this.onRequest,
            this.onResponse,
            this.handler,
        );
    }
}

export class ServerOptions {
    onError: (error: any) => void;
    onRequest: (message: Message) => void;
    onResponse: (message: Message) => void;
    authRequired: boolean;
    serialization: Serialization;

    constructor() {
        this.onError = (e: any) => {};
        this.onRequest = (m: Message) => {};
        this.onResponse = (m: Message) => {};
        this.authRequired = true;
        this.serialization = new DefaultSerialization();
    }
}
