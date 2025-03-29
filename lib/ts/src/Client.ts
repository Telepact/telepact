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
import { ClientBinaryEncoder } from './internal/binary/ClientBinaryEncoder';
import { Message } from './Message';
import { clientHandleMessage } from './internal/ClientHandleMessage';
import { Serialization } from './Serialization';
import { DefaultBinaryEncodingCache } from './internal/binary/DefaultBinaryEncodingCache';
import { ClientBase64Encoder } from './internal/binary/ClientBase64Encoder';
import { LocalStorageBackedBinaryEncodingCache } from './internal/binary/LocalStorageBackedBinaryEncodingCache';

export class Client {
    private adapter: (message: Message, serializer: Serializer) => Promise<Message>;
    private useBinaryDefault: boolean;
    private alwaysSendJson: boolean;
    private timeoutMsDefault: number;
    private serializer: Serializer;

    constructor(adapter: (message: Message, serializer: Serializer) => Promise<Message>, options: ClientOptions) {
        this.adapter = adapter;
        this.useBinaryDefault = options.useBinary;
        this.alwaysSendJson = options.alwaysSendJson;
        this.timeoutMsDefault = options.timeoutMsDefault;

        const binaryEncodingCache = options.localStorageCacheNamespace
            ? new LocalStorageBackedBinaryEncodingCache(options.localStorageCacheNamespace)
            : new DefaultBinaryEncodingCache();
        const binaryEncoder = new ClientBinaryEncoder(binaryEncodingCache);
        const base64Encoder = new ClientBase64Encoder();

        this.serializer = new Serializer(options.serializationImpl, binaryEncoder, base64Encoder);
    }

    async request(requestMessage: Message): Promise<Message> {
        return await clientHandleMessage(
            requestMessage,
            this.adapter,
            this.serializer,
            this.timeoutMsDefault,
            this.useBinaryDefault,
            this.alwaysSendJson,
        );
    }
}

export class ClientOptions {
    useBinary: boolean;
    alwaysSendJson: boolean;
    timeoutMsDefault: number;
    serializationImpl: Serialization;
    localStorageCacheNamespace: string

    constructor() {
        this.useBinary = false;
        this.alwaysSendJson = true;
        this.timeoutMsDefault = 5000;
        this.serializationImpl = new DefaultSerialization();
        this.localStorageCacheNamespace = ''
    }
}
