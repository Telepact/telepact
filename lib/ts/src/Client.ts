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

import { DefaultClientBinaryStrategy } from './DefaultClientBinaryStrategy';
import { DefaultSerialization } from './DefaultSerialization';
import { Serializer } from './Serializer';
import { ClientBinaryEncoder } from './internal/binary/ClientBinaryEncoder';
import { Message } from './Message';
import { processRequestObject } from './internal/ProcessRequestObject';
import { Serialization } from './Serialization';
import { ClientBinaryStrategy } from './ClientBinaryStrategy';

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
        this.serializer = new Serializer(options.serializationImpl, new ClientBinaryEncoder(options.binaryStrategy));
    }

    async request(requestMessage: Message): Promise<Message> {
        return await processRequestObject(
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
    binaryStrategy: ClientBinaryStrategy;

    constructor() {
        this.useBinary = false;
        this.alwaysSendJson = true;
        this.timeoutMsDefault = 5000;
        this.serializationImpl = new DefaultSerialization();
        this.binaryStrategy = new DefaultClientBinaryStrategy();
    }
}
