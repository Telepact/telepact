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

import { Message } from './Message';
import { Serialization } from './Serialization';
import { BinaryEncoder } from './internal/binary/BinaryEncoder';
import { serializeInternal } from './internal/SerializeInternal';
import { deserializeInternal } from './internal/DeserializeInternal';
import { Base64Encoder } from './internal/binary/Base64Encoder';

export class Serializer {
    /**
     * A serializer that converts a Message to and from a serialized form.
     */

    private serializationImpl: Serialization;
    private binaryEncoder: BinaryEncoder;
    private base64Encoder: Base64Encoder;

    constructor(serializationImpl: Serialization, binaryEncoder: BinaryEncoder, base64Encoder: Base64Encoder) {
        this.serializationImpl = serializationImpl;
        this.binaryEncoder = binaryEncoder;
        this.base64Encoder = base64Encoder;
    }

    public serialize(message: Message): Uint8Array {
        /**
         * Serialize a Message into a byte array.
         */
        return serializeInternal(message, this.binaryEncoder, this.base64Encoder, this.serializationImpl);
    }

    public deserialize(messageBytes: Uint8Array): Message {
        /**
         * Deserialize a Message from a byte array.
         */
        return deserializeInternal(messageBytes, this.serializationImpl, this.binaryEncoder, this.base64Encoder);
    }
}
