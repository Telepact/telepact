import { BinaryEncoding } from 'uapi/internal/binary/BinaryEncoding';
import { encodeBody } from 'uapi/internal/binary/EncodeBody';
import { packBody } from 'uapi/internal/binary/PackBody';

export function serverBinaryEncode(message: any[], binaryEncoder: BinaryEncoding): any[] {
    const headers: { [key: string]: any } = message[0];
    const messageBody: { [key: string]: any } = message[1];
    const clientKnownBinaryChecksums: number[] | undefined = headers['_clientKnownBinaryChecksums'];

    if (clientKnownBinaryChecksums === undefined || !clientKnownBinaryChecksums.includes(binaryEncoder.checksum)) {
        headers['enc_'] = binaryEncoder.encodeMap;
    }

    headers['bin_'] = [binaryEncoder.checksum];
    const encodedMessageBody = encodeBody(messageBody, binaryEncoder);

    let finalEncodedMessageBody: { [key: string]: any };
    if (headers['_pac'] === true) {
        finalEncodedMessageBody = packBody(encodedMessageBody);
    } else {
        finalEncodedMessageBody = encodedMessageBody;
    }

    return [headers, finalEncodedMessageBody];
}
