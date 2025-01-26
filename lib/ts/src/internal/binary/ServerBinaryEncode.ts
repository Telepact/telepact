import { BinaryEncoding } from '../../internal/binary/BinaryEncoding';
import { encodeBody } from '../../internal/binary/EncodeBody';
import { packBody } from '../../internal/binary/PackBody';
import { BinaryEncoderUnavailableError } from '../../internal/binary/BinaryEncoderUnavailableError';

export function serverBinaryEncode(message: any[], binaryEncoder: BinaryEncoding): any[] {
    const headers: { [key: string]: any } = message[0];
    const messageBody: { [key: string]: any } = message[1];
    const clientKnownBinaryChecksums: number[] | undefined = headers['_clientKnownBinaryChecksums'];
    delete headers['_clientKnownBinaryChecksums'];

    const resultTag = Object.keys(messageBody)[0];

    if (resultTag !== 'Ok_') {
        throw new BinaryEncoderUnavailableError();
    }

    if (clientKnownBinaryChecksums === undefined || !clientKnownBinaryChecksums.includes(binaryEncoder.checksum)) {
        headers['enc_'] = binaryEncoder.encodeMap;
    }

    headers['bin_'] = [binaryEncoder.checksum];
    const encodedMessageBody = encodeBody(messageBody, binaryEncoder);

    let finalEncodedMessageBody: { [key: string]: any };
    if (headers['pac_'] === true) {
        finalEncodedMessageBody = packBody(encodedMessageBody);
    } else {
        finalEncodedMessageBody = encodedMessageBody;
    }

    return [headers, finalEncodedMessageBody];
}
