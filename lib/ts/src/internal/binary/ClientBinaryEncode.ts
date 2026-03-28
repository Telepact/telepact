//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import { BinaryEncoderUnavailableError } from "../../internal/binary/BinaryEncoderUnavailableError";
import { encodeBody } from "../../internal/binary/EncodeBody";
import { packBody } from "../../internal/binary/PackBody";
import { BinaryEncodingCache } from "./BinaryEncodingCache";
import { ClientBinaryStrategy } from "./ClientBinaryStrategy";

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
