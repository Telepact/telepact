import { BinaryEncoding } from 'uapi/internal/binary/BinaryEncoding';
import { BinaryEncoderUnavailableError } from 'uapi/internal/binary/BinaryEncoderUnavailableError';
import { decodeBody } from 'uapi/internal/binary/DecodeBody';
import { unpackBody } from 'uapi/internal/binary/UnpackBody';

export function serverBinaryDecode(message: any[], binaryEncoder: BinaryEncoding): any[] {
    const headers: { [key: string]: any } = message[0];
    const encodedMessageBody: { [key: string]: any } = message[1];
    const clientKnownBinaryChecksums: number[] = headers['bin_'] || [];
    const binaryChecksumUsedByClientOnThisMessage: number = clientKnownBinaryChecksums[0];

    if (binaryChecksumUsedByClientOnThisMessage !== binaryEncoder.checksum) {
        throw new BinaryEncoderUnavailableError();
    }

    let finalEncodedMessageBody: { [key: string]: any };
    if (headers['_pac'] === true) {
        finalEncodedMessageBody = unpackBody(encodedMessageBody);
    } else {
        finalEncodedMessageBody = encodedMessageBody;
    }

    const messageBody: { [key: string]: any } = decodeBody(finalEncodedMessageBody, binaryEncoder);
    return [headers, messageBody];
}
