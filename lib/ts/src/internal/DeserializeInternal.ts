//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { Serialization } from '../Serialization.js';
import { BinaryEncoder } from '../internal/binary/BinaryEncoder.js';
import { Message } from '../Message.js';
import { InvalidMessage } from '../internal/validation/InvalidMessage.js';
import { InvalidMessageBody } from '../internal/validation/InvalidMessageBody.js';
import { Base64Encoder } from './binary/Base64Encoder.js';

export function deserializeInternal(
    messageBytes: Uint8Array,
    serializer: Serialization,
    binaryEncoder: BinaryEncoder,
    base64Encoder: Base64Encoder
): Message {
    let messageAsPseudoJson: any;
    let isMsgPack: boolean;

    try {
        if (messageBytes[0] === 0x92) {
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
        finalMessageAsPseudoJsonList = base64Encoder.decode(messageAsPseudoJsonList);
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
