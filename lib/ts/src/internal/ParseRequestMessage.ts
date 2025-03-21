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

import { Serializer } from '../Serializer';
import { TelepactSchema } from '../TelepactSchema';
import { Message } from '../Message';
import { BinaryEncoderUnavailableError } from '../internal/binary/BinaryEncoderUnavailableError';
import { BinaryEncodingMissing } from '../internal/binary/BinaryEncodingMissing';
import { InvalidMessage } from '../internal/validation/InvalidMessage';
import { InvalidMessageBody } from '../internal/validation/InvalidMessageBody';

export function parseRequestMessage(
    requestMessageBytes: Uint8Array,
    serializer: Serializer,
    telepactSchema: TelepactSchema,
    onError: (error: Error) => void,
): Message {
    try {
        return serializer.deserialize(requestMessageBytes);
    } catch (e) {
        onError(e);

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
