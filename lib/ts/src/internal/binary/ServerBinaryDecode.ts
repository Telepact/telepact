import { BinaryEncoding } from 'uapi/internal/binary/BinaryEncoding';
import { BinaryEncoderUnavailableError } from 'uapi/internal/binary/BinaryEncoderUnavailableError';
import { decodeBody } from 'uapi/internal/binary/DecodeBody';
import { unpackBody } from 'uapi/internal/binary/UnpackBody';
import { convertMapsToObjects } from './ConvertMapsToObjects';

export function serverBinaryDecode(message: any[], binaryEncoder: BinaryEncoding): any[] {
    const headers = message[0] as Map<string, any>;
    const encodedMessageBody = message[1] as Map<any, any>;
    const clientKnownBinaryChecksums = headers.get('bin_') as number[];
    const binaryChecksumUsedByClientOnThisMessage = clientKnownBinaryChecksums[0];

    if (binaryChecksumUsedByClientOnThisMessage !== binaryEncoder.checksum) {
        throw new BinaryEncoderUnavailableError();
    }

    let finalEncodedMessageBody: Map<any, any>;
    if (headers.get('_pac') === true) {
        finalEncodedMessageBody = unpackBody(encodedMessageBody);
    } else {
        finalEncodedMessageBody = encodedMessageBody;
    }

    const messageHeader = convertMapsToObjects(headers);
    const messageBody = decodeBody(finalEncodedMessageBody, binaryEncoder);
    return [messageHeader, messageBody];
}
