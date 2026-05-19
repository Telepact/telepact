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
import { SerializerMeasurementObserver, annotateSerializerMeasurement, measureSerializerStage, runMeasuredSerializerOperation } from '../SerializerMeasurement.js';
import { Serialization } from '../Serialization.js';
import { Message } from '../Message.js';
import { BinaryEncoder } from '../internal/binary/BinaryEncoder.js';
import { Base64Encoder } from './binary/Base64Encoder.js';

export function serializeInternal(
    message: Message,
    binaryEncoder: BinaryEncoder,
    base64Encoder: Base64Encoder,
    serializer: Serialization,
    measurementObserver?: SerializerMeasurementObserver,
): Uint8Array {
    const headers: Record<string, any> = message.headers;
    const binaryRequested = headers['@binary_'] === true;
    const packed = headers['@pac_'] === true;

    return runMeasuredSerializerOperation(
        'serialize',
        measurementObserver,
        {
            binaryRequested,
            transportEncoding: 'json',
            protocolEncoding: 'base64',
            packed,
            fellBackToJson: false,
        },
        () => {
            let serializeAsBinary: boolean;
            measureSerializerStage('serialize.headerDecision', () => {
                if ('@binary_' in headers) {
                    serializeAsBinary = headers['@binary_'] === true;
                    delete headers['@binary_'];
                } else {
                    serializeAsBinary = false;
                }
            });

            const messageAsPseudoJson: any[] = [message.headers, message.body];

            try {
                if (serializeAsBinary!) {
                    try {
                        const encodedMessage = measureSerializerStage('serialize.binary.encode', () => binaryEncoder.encode(messageAsPseudoJson));
                        annotateSerializerMeasurement({
                            transportEncoding: 'msgpack',
                            protocolEncoding: 'binary',
                            fellBackToJson: false,
                        });
                        return measureSerializerStage('serialize.msgpack.encode', () => serializer.toMsgpack(encodedMessage));
                    } catch (error) {
                        annotateSerializerMeasurement({
                            transportEncoding: 'json',
                            protocolEncoding: 'base64',
                            fellBackToJson: true,
                        });
                        const base64EncodedMessage = measureSerializerStage('serialize.base64.encode', () => base64Encoder.encode(messageAsPseudoJson));
                        return measureSerializerStage('serialize.json.encode', () => serializer.toJson(base64EncodedMessage));
                    }
                }

                const base64EncodedMessage = measureSerializerStage('serialize.base64.encode', () => base64Encoder.encode(messageAsPseudoJson));
                annotateSerializerMeasurement({
                    transportEncoding: 'json',
                    protocolEncoding: 'base64',
                    fellBackToJson: false,
                });
                return measureSerializerStage('serialize.json.encode', () => serializer.toJson(base64EncodedMessage));
            } catch (error) {
                throw new SerializationError(error, serializeAsBinary! ? 'encoding Telepact message as binary or JSON fallback' : 'encoding Telepact message as JSON');
            }
        },
    );
}
