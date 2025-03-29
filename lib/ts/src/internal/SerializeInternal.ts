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

import { SerializationError } from '../SerializationError';
import { Serialization } from '../Serialization';
import { Message } from '../Message';
import { BinaryEncoder } from '../internal/binary/BinaryEncoder';
import { Base64Encoder } from './binary/Base64Encoder';

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
        throw new SerializationError(error as Error);
    }
}
