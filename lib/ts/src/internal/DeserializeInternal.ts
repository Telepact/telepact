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

import { Serialization } from '../Serialization.js';
import { SerializerMeasurementObserver, annotateSerializerMeasurement, measureSerializerStage, runMeasuredSerializerOperation } from '../SerializerMeasurement.js';
import { BinaryEncoder } from '../internal/binary/BinaryEncoder.js';
import { Message } from '../Message.js';
import { InvalidMessage } from '../internal/validation/InvalidMessage.js';
import { InvalidMessageBody } from '../internal/validation/InvalidMessageBody.js';
import { Base64Encoder } from './binary/Base64Encoder.js';

export function deserializeInternal(
    messageBytes: Uint8Array,
    serializer: Serialization,
    binaryEncoder: BinaryEncoder,
    base64Encoder: Base64Encoder,
    measurementObserver?: SerializerMeasurementObserver,
): Message {
    return runMeasuredSerializerOperation(
        'deserialize',
        measurementObserver,
        {
            binaryRequested: false,
            transportEncoding: 'json',
            protocolEncoding: 'base64',
            packed: false,
            fellBackToJson: false,
        },
        () => {
            let messageAsPseudoJson: any;
            let isMsgPack: boolean;

            try {
                if (messageBytes[0] === 0x92) {
                    isMsgPack = true;
                    annotateSerializerMeasurement({
                        transportEncoding: 'msgpack',
                        protocolEncoding: 'binary',
                    });
                    messageAsPseudoJson = measureSerializerStage('deserialize.msgpack.decode', () => serializer.fromMsgpack(messageBytes));
                } else {
                    isMsgPack = false;
                    annotateSerializerMeasurement({
                        transportEncoding: 'json',
                        protocolEncoding: 'base64',
                    });
                    messageAsPseudoJson = measureSerializerStage('deserialize.json.decode', () => serializer.fromJson(messageBytes));
                }
            } catch (e) {
                throw new InvalidMessage();
            }

            if (!Array.isArray(messageAsPseudoJson)) {
                throw new InvalidMessage();
            }

            const messageAsPseudoJsonList: any[] = messageAsPseudoJson;

            if (messageAsPseudoJsonList.length !== 2) {
                throw new InvalidMessage();
            }

            let finalMessageAsPseudoJsonList: any[];
            if (isMsgPack!) {
                finalMessageAsPseudoJsonList = measureSerializerStage('deserialize.binary.decode', () => binaryEncoder.decode(messageAsPseudoJsonList));
                const headers = finalMessageAsPseudoJsonList[0] as Map<string, any> | undefined;
                annotateSerializerMeasurement({
                    packed: headers instanceof Map && headers.get('@pac_') === true,
                });
            } else {
                finalMessageAsPseudoJsonList = measureSerializerStage('deserialize.base64.decode', () => base64Encoder.decode(messageAsPseudoJsonList));
                const headers = finalMessageAsPseudoJsonList[0] as Record<string, any> | undefined;
                annotateSerializerMeasurement({
                    packed: typeof headers === 'object' && headers !== null && headers['@pac_'] === true,
                });
            }

            return measureSerializerStage('deserialize.validation', () => {
                if (typeof finalMessageAsPseudoJsonList[0] !== 'object' || Array.isArray(finalMessageAsPseudoJsonList[0])) {
                    throw new InvalidMessage();
                }

                const headers: { [key: string]: any } = finalMessageAsPseudoJsonList[0];

                if (typeof finalMessageAsPseudoJsonList[1] !== 'object' || Array.isArray(finalMessageAsPseudoJsonList[1])) {
                    throw new InvalidMessage();
                }

                const body: { [key: string]: any } = finalMessageAsPseudoJsonList[1];

                if (Object.keys(body).length !== 1) {
                    throw new InvalidMessageBody();
                }

                if (typeof Object.values(body)[0] !== 'object' || Array.isArray(Object.values(body)[0])) {
                    throw new InvalidMessageBody();
                }

                return new Message(headers, body);
            });
        },
    );
}
