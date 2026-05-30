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

import { decodeBody } from "../../internal/binary/DecodeBody.js";
import { convertMapsToObjects } from "./ConvertMapsToObjects.js";
import { BinaryEncodingCache } from "./BinaryEncodingCache.js";
import { ClientBinaryStrategy } from "./ClientBinaryStrategy.js";

export function clientBinaryDecode(
    message: any[],
    binaryEncodingCache: BinaryEncodingCache,
    binaryChecksumStrategy: ClientBinaryStrategy,
): any[] {
    const headers = message[0] as Map<string, any> | Record<string, any>;
    const encodedMessageBody = message[1] as Map<any, any> | Record<string, any>;
    const binaryChecksums = getHeader(headers, "@bin_") as number[];
    const binaryChecksum = binaryChecksums[0]!;

    if (hasHeader(headers, "@enc_")) {
        const binaryEncoding = getHeader(headers, "@enc_") as Map<string, number> | Record<string, number>;
        binaryEncodingCache.add(binaryChecksum, binaryEncoding);
    }

    binaryChecksumStrategy.updateChecksum(binaryChecksum);
    const newCurrentChecksumStrategy = binaryChecksumStrategy.getCurrentChecksums();

    const binaryEncoder = binaryEncodingCache.get(newCurrentChecksumStrategy[0]);

    const messageHeader = convertMapsToObjects(headers);
    const messageBody = decodeBody(encodedMessageBody, binaryEncoder);
    return [messageHeader, messageBody];
}

function getHeader(headers: Map<string, any> | Record<string, any>, key: string): any {
    return headers instanceof Map ? headers.get(key) : headers[key];
}

function hasHeader(headers: Map<string, any> | Record<string, any>, key: string): boolean {
    return headers instanceof Map ? headers.has(key) : Object.prototype.hasOwnProperty.call(headers, key);
}
