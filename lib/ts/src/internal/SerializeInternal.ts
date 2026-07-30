//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { SerializationError } from '../SerializationError.js';
import { Serialization } from '../Serialization.js';
import { Message } from '../Message.js';
import { BinaryEncoder } from '../internal/binary/BinaryEncoder.js';
import { Base64Encoder } from './binary/Base64Encoder.js';

export function serializeInternal(
    message: Message,
    binaryEncoder: BinaryEncoder,
    base64Encoder: Base64Encoder,
    serializer: Serialization,
): Uint8Array {
    const headers: Record<string, any> = message.headers;

    let serializeAsBinary: boolean;
    if ('@binary_' in headers) {
        serializeAsBinary = headers['@binary_'] === true;
        delete headers['@binary_'];
    } else {
        serializeAsBinary = false;
    }

    const messageAsPseudoJson: any[] = [message.headers, message.body];

    try {
        if (serializeAsBinary) {
            try {
                const encodedMessage = binaryEncoder.encode(messageAsPseudoJson);
                return serializer.toMsgpack(encodedMessage);
            } catch (error) {
                // We can still submit as JSON
                const base64EncodedMessage = base64Encoder.encode(messageAsPseudoJson);
                return serializer.toJson(base64EncodedMessage);
            }
        } else {
            const base64EncodedMessage = base64Encoder.encode(messageAsPseudoJson);
            return serializer.toJson(base64EncodedMessage);
        }
    } catch (error) {
        throw new SerializationError(error, serializeAsBinary ? 'encoding Telepact message as binary or JSON fallback' : 'encoding Telepact message as JSON');
    }
}
