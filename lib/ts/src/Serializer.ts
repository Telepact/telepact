//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { Message } from './Message.js';
import { Serialization } from './Serialization.js';
import { BinaryEncoder } from './internal/binary/BinaryEncoder.js';
import { serializeInternal } from './internal/SerializeInternal.js';
import { deserializeInternal } from './internal/DeserializeInternal.js';
import { Base64Encoder } from './internal/binary/Base64Encoder.js';

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
