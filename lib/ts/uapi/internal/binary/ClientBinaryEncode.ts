import { BinaryEncoding } from 'uapi/internal/binary/BinaryEncoding';
import { BinaryEncoderUnavailableError } from 'uapi/internal/binary/BinaryEncoderUnavailableError';
import { ClientBinaryStrategy } from 'uapi/ClientBinaryStrategy';
import { encodeBody } from 'uapi/internal/binary/EncodeBody';
import { packBody } from 'uapi/internal/binary/PackBody';

export function clientBinaryEncode(
    message: any[],
    recentBinaryEncoders: Map<number, BinaryEncoding>,
    binaryChecksumStrategy: ClientBinaryStrategy,
): any[] {
    const headers = message[0] as Record<string, any>;
    const messageBody = message[1] as Record<string, any>;
    const forceSendJson = headers['_forceSendJson'];

    headers['bin_'] = binaryChecksumStrategy.getCurrentChecksums();

    if (forceSendJson === true) {
        throw new BinaryEncoderUnavailableError();
    }

    if (recentBinaryEncoders.size > 1) {
        throw new BinaryEncoderUnavailableError();
    }

    const binaryEncoder = [...recentBinaryEncoders.values()][0];

    if (!binaryEncoder) {
        throw new BinaryEncoderUnavailableError();
    }

    const encodedMessageBody = encodeBody(messageBody, binaryEncoder);

    let finalEncodedMessageBody: Map<any, any>;
    if (headers['_pac'] === true) {
        finalEncodedMessageBody = packBody(encodedMessageBody);
    } else {
        finalEncodedMessageBody = encodedMessageBody;
    }

    return [headers, finalEncodedMessageBody];
}
