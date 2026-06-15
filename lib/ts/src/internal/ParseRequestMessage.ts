//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { Serializer } from '../Serializer.js';
import { TelepactSchema } from '../TelepactSchema.js';
import { Message } from '../Message.js';
import { BinaryEncoderUnavailableError } from '../internal/binary/BinaryEncoderUnavailableError.js';
import { BinaryEncodingMissing } from '../internal/binary/BinaryEncodingMissing.js';
import { InvalidMessage } from '../internal/validation/InvalidMessage.js';
import { InvalidMessageBody } from '../internal/validation/InvalidMessageBody.js';
import { TelepactError } from '../TelepactError.js';

export function parseRequestMessage(
    requestMessageBytes: Uint8Array,
    serializer: Serializer,
    telepactSchema: TelepactSchema,
    onError: (error: TelepactError) => void,
): Message {
    try {
        return serializer.deserialize(requestMessageBytes);
    } catch (e) {
        onError(new TelepactError('telepact request parsing failed while decoding the incoming message', 'parse', e));

        let reason: string;
        if (e instanceof BinaryEncoderUnavailableError) {
            reason = 'IncompatibleBinaryEncoding';
        } else if (e instanceof BinaryEncodingMissing) {
            reason = 'BinaryDecodeFailure';
        } else if (e instanceof InvalidMessage) {
            reason = 'ExpectedJsonArrayOfTwoObjects';
        } else if (e instanceof InvalidMessageBody) {
            reason = 'ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject';
        } else {
            reason = 'ExpectedJsonArrayOfTwoObjects';
        }

        return new Message({ _parseFailures: [{ [reason]: {} }] }, { _unknown: {} });
    }
}
