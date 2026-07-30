//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { decodeBody } from "../../internal/binary/DecodeBody.js";
import { unpackBody } from "../../internal/binary/UnpackBody.js";
import { convertMapsToObjects } from "./ConvertMapsToObjects.js";
import { BinaryEncodingCache } from "./BinaryEncodingCache.js";
import { ClientBinaryStrategy } from "./ClientBinaryStrategy.js";

export function clientBinaryDecode(
    message: any[],
    binaryEncodingCache: BinaryEncodingCache,
    binaryChecksumStrategy: ClientBinaryStrategy,
): any[] {
    const headers = message[0] as Map<string, any>;
    const encodedMessageBody = message[1] as Map<any, any>;
    const binaryChecksums = headers.get("@bin_") as number[];
    const binaryChecksum = binaryChecksums[0]!;

    if (headers.has("@enc_")) {
        const binaryEncoding = headers.get("@enc_") as Map<string, number>;
        binaryEncodingCache.add(binaryChecksum, binaryEncoding);
    }

    binaryChecksumStrategy.updateChecksum(binaryChecksum);
    const newCurrentChecksumStrategy = binaryChecksumStrategy.getCurrentChecksums();

    const binaryEncoder = binaryEncodingCache.get(newCurrentChecksumStrategy[0]);

    let finalEncodedMessageBody: Map<any, any>;
    if (headers.get("@pac_") === true) {
        finalEncodedMessageBody = unpackBody(encodedMessageBody);
    } else {
        finalEncodedMessageBody = encodedMessageBody;
    }

    const messageHeader = convertMapsToObjects(headers);
    const messageBody = decodeBody(finalEncodedMessageBody, binaryEncoder);
    return [messageHeader, messageBody];
}
