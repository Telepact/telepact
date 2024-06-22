import { Serializer } from 'uapi/Serializer';
import { UApiSchema } from 'uapi/UApiSchema';
import { Message } from 'uapi/Message';
import { BinaryEncoderUnavailableError } from 'uapi/internal/binary/BinaryEncoderUnavailableError';
import { BinaryEncodingMissing } from 'uapi/internal/binary/BinaryEncodingMissing';
import { InvalidMessage } from 'uapi/internal/validation/InvalidMessage';
import { InvalidMessageBody } from 'uapi/internal/validation/InvalidMessageBody';

export function parseRequestMessage(
    requestMessageBytes: Uint8Array,
    serializer: Serializer,
    uapiSchema: UApiSchema,
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
