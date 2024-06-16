import { BinaryEncoding } from 'uapi/internal/binary/BinaryEncoding';
import { BinaryEncoderUnavailableError } from 'uapi/internal/binary/BinaryEncoderUnavailableError';
import { ClientBinaryStrategy } from 'uapi/ClientBinaryStrategy';
import { encodeBody } from 'uapi/internal/binary/EncodeBody';
import { packBody } from 'uapi/internal/binary/PackBody';

export function clientBinaryEncode(
    message: any[],
    recentBinaryEncoders: { [key: number]: BinaryEncoding },
    binaryChecksumStrategy: ClientBinaryStrategy,
): any[] {
    const headers: { [key: string]: any } = message[0];
    const messageBody: { [key: string]: any } = message[1];
    const forceSendJson: boolean | null | undefined = headers._forceSendJson;
    delete headers._forceSendJson;

    headers.bin_ = binaryChecksumStrategy.getCurrentChecksums();

    if (forceSendJson === true) {
        throw new BinaryEncoderUnavailableError();
    }

    if (Object.keys(recentBinaryEncoders).length > 1) {
        throw new BinaryEncoderUnavailableError();
    }

    const binaryEncoderOptional = Object.values(recentBinaryEncoders)[0] || null;
    if (!binaryEncoderOptional) {
        throw new BinaryEncoderUnavailableError();
    }
    const binaryEncoder = binaryEncoderOptional;

    const encodedMessageBody = encodeBody(messageBody, binaryEncoder);

    const finalEncodedMessageBody = headers._pac === true ? packBody(encodedMessageBody) : encodedMessageBody;

    return [headers, finalEncodedMessageBody];
}
