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

import { Serialization } from '../Serialization';
import { BinaryEncoder } from '../internal/binary/BinaryEncoder';
import { Message } from '../Message';
import { InvalidMessage } from '../internal/validation/InvalidMessage';
import { InvalidMessageBody } from '../internal/validation/InvalidMessageBody';

export function deserializeInternal(
    messageBytes: Uint8Array,
    serializer: Serialization,
    binaryEncoder: BinaryEncoder,
): Message {
    let messageAsPseudoJson: any;
    let isMsgPack: boolean;

    try {
        if (messageBytes[0] === 0x92) {
            // MsgPack
            isMsgPack = true;
            messageAsPseudoJson = serializer.fromMsgpack(messageBytes);
        } else {
            isMsgPack = false;
            messageAsPseudoJson = serializer.fromJson(messageBytes);
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
    if (isMsgPack) {
        finalMessageAsPseudoJsonList = binaryEncoder.decode(messageAsPseudoJsonList);
    } else {
        finalMessageAsPseudoJsonList = messageAsPseudoJsonList;
    }

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
}
