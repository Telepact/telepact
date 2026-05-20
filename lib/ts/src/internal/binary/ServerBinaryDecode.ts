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

import { BinaryEncoding } from "../../internal/binary/BinaryEncoding.js";
import { BinaryEncoderUnavailableError } from "../../internal/binary/BinaryEncoderUnavailableError.js";
import { decodeBody } from "../../internal/binary/DecodeBody.js";
import { convertMapsToObjects } from "./ConvertMapsToObjects.js";

export function serverBinaryDecode(message: any[], binaryEncoder: BinaryEncoding): any[] {
    const headers = message[0] as Map<string, any>;
    const encodedMessageBody = message[1] as Map<any, any>;
    const clientKnownBinaryChecksums = headers.get("@bin_") as number[];
    const binaryChecksumUsedByClientOnThisMessage = clientKnownBinaryChecksums[0];

    if (binaryChecksumUsedByClientOnThisMessage !== binaryEncoder.checksum) {
        throw new BinaryEncoderUnavailableError();
    }

    const messageHeader = convertMapsToObjects(headers);
    const messageBody = decodeBody(encodedMessageBody, binaryEncoder);
    return [messageHeader, messageBody];
}
