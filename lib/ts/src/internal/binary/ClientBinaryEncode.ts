//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { BinaryEncoderUnavailableError } from "../../internal/binary/BinaryEncoderUnavailableError.js";
import { encodeBody } from "../../internal/binary/EncodeBody.js";
import { packBody } from "../../internal/binary/PackBody.js";
import { BinaryEncodingCache } from "./BinaryEncodingCache.js";
import { ClientBinaryStrategy } from "./ClientBinaryStrategy.js";

export function clientBinaryEncode(
    message: any[],
    binaryEncodingCache: BinaryEncodingCache,
    binaryChecksumStrategy: ClientBinaryStrategy,
): any[] {
    const headers = message[0] as Record<string, any>;
    const messageBody = message[1] as Record<string, any>;
    const forceSendJson = headers["_forceSendJson"];
    delete headers["_forceSendJson"];

    const checksums = binaryChecksumStrategy.getCurrentChecksums()
    headers["@bin_"] = checksums;

    if (forceSendJson === true) {
        throw new BinaryEncoderUnavailableError();
    }

    if (checksums.length > 1) {
        throw new BinaryEncoderUnavailableError();
    }

    const binaryEncoding = checksums.length > 0 ? binaryEncodingCache.get(checksums[0]) : undefined;

    if (!binaryEncoding) {
        throw new BinaryEncoderUnavailableError();
    }

    const encodedMessageBody = encodeBody(messageBody, binaryEncoding);

    let finalEncodedMessageBody: Map<any, any>;
    if (headers["@pac_"] === true) {
        finalEncodedMessageBody = packBody(encodedMessageBody);
    } else {
        finalEncodedMessageBody = encodedMessageBody;
    }

    return [headers, finalEncodedMessageBody];
}
