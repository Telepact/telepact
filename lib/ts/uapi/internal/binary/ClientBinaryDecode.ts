import { BinaryEncoding } from 'uapi/internal/binary/BinaryEncoding';
import { ClientBinaryStrategy } from 'uapi/ClientBinaryStrategy';
import { decodeBody } from 'uapi/internal/binary/DecodeBody';
import { unpackBody } from 'uapi/internal/binary/UnpackBody';

export function clientBinaryDecode(
    message: any[],
    recentBinaryEncoders: Record<number, BinaryEncoding>,
    binaryChecksumStrategy: ClientBinaryStrategy,
): any[] {
    const headers = message[0];
    const encodedMessageBody = message[1];
    const binaryChecksums: number[] = headers['bin_'] || [];
    const binaryChecksum = binaryChecksums[0];

    // If there is a binary encoding included on this message, cache it
    if ('enc_' in headers) {
        const binaryEncoding = headers['enc_'];
        const newBinaryEncoder = new BinaryEncoding(binaryEncoding, binaryChecksum);

        recentBinaryEncoders[binaryChecksum] = newBinaryEncoder;
    }

    binaryChecksumStrategy.updateChecksum(binaryChecksum);
    const newCurrentChecksumStrategy = binaryChecksumStrategy.getCurrentChecksums();

    for (const key in recentBinaryEncoders) {
        if (!(key in newCurrentChecksumStrategy)) {
            delete recentBinaryEncoders[key];
        }
    }

    const binaryEncoder = recentBinaryEncoders[binaryChecksum];

    let finalEncodedMessageBody: Record<any, any>;
    if (headers['_pac'] === true) {
        finalEncodedMessageBody = unpackBody(encodedMessageBody);
    } else {
        finalEncodedMessageBody = encodedMessageBody;
    }

    const messageBody = decodeBody(finalEncodedMessageBody, binaryEncoder);
    return [headers, messageBody];
}
