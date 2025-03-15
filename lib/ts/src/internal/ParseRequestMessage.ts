import { Serializer } from '../Serializer';
import { MsgPactSchema } from '../MsgPactSchema';
import { Message } from '../Message';
import { BinaryEncoderUnavailableError } from '../internal/binary/BinaryEncoderUnavailableError';
import { BinaryEncodingMissing } from '../internal/binary/BinaryEncodingMissing';
import { InvalidMessage } from '../internal/validation/InvalidMessage';
import { InvalidMessageBody } from '../internal/validation/InvalidMessageBody';

export function parseRequestMessage(
    requestMessageBytes: Uint8Array,
    serializer: Serializer,
    msgpactSchema: MsgPactSchema,
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
