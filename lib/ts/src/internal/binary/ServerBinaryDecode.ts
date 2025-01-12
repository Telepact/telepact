import { BinaryEncoding } from "../../internal/binary/BinaryEncoding";
import { BinaryEncoderUnavailableError } from "../../internal/binary/BinaryEncoderUnavailableError";
import { decodeBody } from "../../internal/binary/DecodeBody";
import { unpackBody } from "../../internal/binary/UnpackBody";
import { convertMapsToObjects } from "./ConvertMapsToObjects";

export function serverBinaryDecode(message: any[], binaryEncoder: BinaryEncoding): any[] {
    const headers = message[0] as Map<string, any>;
    const encodedMessageBody = message[1] as Map<any, any>;
    const clientKnownBinaryChecksums = headers.get("bin_") as number[];
    const binaryChecksumUsedByClientOnThisMessage = clientKnownBinaryChecksums[0];

    if (binaryChecksumUsedByClientOnThisMessage !== binaryEncoder.checksum) {
        throw new BinaryEncoderUnavailableError();
    }

    let finalEncodedMessageBody: Map<any, any>;
    if (headers.get("pac_") === true) {
        finalEncodedMessageBody = unpackBody(encodedMessageBody);
    } else {
        finalEncodedMessageBody = encodedMessageBody;
    }

    const messageHeader = convertMapsToObjects(headers);
    const messageBody = decodeBody(finalEncodedMessageBody, binaryEncoder);
    return [messageHeader, messageBody];
}
