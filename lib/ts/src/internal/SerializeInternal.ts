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

import { SerializationError } from '../SerializationError.js';
import { Serialization } from '../Serialization.js';
import { Message } from '../Message.js';
import { BinaryEncoder } from '../internal/binary/BinaryEncoder.js';
import { Base64Encoder } from './binary/Base64Encoder.js';
import { BinaryEncoderUnavailableError } from './binary/BinaryEncoderUnavailableError.js';

export function serializeInternal(
    message: Message,
    binaryEncoder: BinaryEncoder,
    base64Encoder: Base64Encoder,
    serializer: Serialization,
): Uint8Array {
    const messageHeaders: Record<string, any> = { ...message.headers };

    const serializeAsBinary = messageHeaders['@binary_'] === true;
    delete messageHeaders['@binary_'];

    const messageAsPseudoJson: any[] = [messageHeaders, message.body];

    try {
        if (serializeAsBinary) {
            try {
                return binaryEncoder.encodeToMsgpack(messageAsPseudoJson, serializer);
            } catch (error) {
                if (!(error instanceof BinaryEncoderUnavailableError)) {
                    throw error;
                }
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
