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

import { BinaryEncoding } from "../../internal/binary/BinaryEncoding";
import { ClientBinaryStrategy } from "../../ClientBinaryStrategy";
import { decodeBody } from "../../internal/binary/DecodeBody";
import { unpackBody } from "../../internal/binary/UnpackBody";
import { convertMapsToObjects } from "./ConvertMapsToObjects";

export function clientBinaryDecode(
    message: any[],
    recentBinaryEncoders: Map<number, BinaryEncoding>,
    binaryChecksumStrategy: ClientBinaryStrategy,
): any[] {
    const headers = message[0] as Map<string, any>;
    const encodedMessageBody = message[1] as Map<any, any>;
    const binaryChecksums = headers.get("@bin_") as number[];
    const binaryChecksum = binaryChecksums[0]!;

    if (headers.has("@enc_")) {
        const binaryEncoding = headers.get("@enc_") as Map<string, number>;
        const newBinaryEncoder = new BinaryEncoding(binaryEncoding, binaryChecksum);
        recentBinaryEncoders.set(binaryChecksum, newBinaryEncoder);
    }

    binaryChecksumStrategy.updateChecksum(binaryChecksum);
    const newCurrentChecksumStrategy = binaryChecksumStrategy.getCurrentChecksums();

    for (const [key, value] of recentBinaryEncoders) {
        if (!newCurrentChecksumStrategy.includes(key)) {
            recentBinaryEncoders.delete(key);
        }
    }

    const binaryEncoder = recentBinaryEncoders.get(binaryChecksum)!;

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
