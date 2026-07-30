//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { DefaultSerialization } from './DefaultSerialization.js';
import { Serializer } from './Serializer.js';
import { ClientBinaryEncoder } from './internal/binary/ClientBinaryEncoder.js';
import { Message } from './Message.js';
import { clientHandleMessage } from './internal/ClientHandleMessage.js';
import { Serialization } from './Serialization.js';
import { DefaultBinaryEncodingCache } from './internal/binary/DefaultBinaryEncodingCache.js';
import { ClientBase64Encoder } from './internal/binary/ClientBase64Encoder.js';
import { LocalStorageBackedBinaryEncodingCache } from './internal/binary/LocalStorageBackedBinaryEncodingCache.js';

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
