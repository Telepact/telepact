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

import { BinaryEncoder } from './BinaryEncoder.js';
import { BinaryEncoding } from './BinaryEncoding.js';
import { Serialization } from '../../Serialization.js';
import { isBinaryMsgpackSerialization } from './BinaryMsgpackSerialization.js';
import { BinaryEncoderUnavailableError } from './BinaryEncoderUnavailableError.js';

export class ServerBinaryEncoder extends BinaryEncoder {
    private binaryEncoder: BinaryEncoding;

    constructor(binaryEncoder: BinaryEncoding) {
        super();
        this.binaryEncoder = binaryEncoder;
    }

    encodeToMsgpack(message: any[], serializer: Serialization): Uint8Array {
        if (!isBinaryMsgpackSerialization(serializer)) {
            throw new Error('binary MsgPack serialization is required');
        }

        const inputHeaders = message[0] as Record<string, any>;
        const body = message[1] as Record<string, any>;
        const clientKnownBinaryChecksums = inputHeaders['@clientKnownBinaryChecksums_'] as number[] | undefined;
        delete inputHeaders['@clientKnownBinaryChecksums_'];
        const headers: Record<string, any> = {};
        for (const key in inputHeaders) {
            if (Object.prototype.hasOwnProperty.call(inputHeaders, key)) {
                headers[key] = inputHeaders[key];
            }
        }

        if (!Object.prototype.hasOwnProperty.call(body, 'Ok_')) {
            throw new BinaryEncoderUnavailableError();
        }

        if (clientKnownBinaryChecksums === undefined || !clientKnownBinaryChecksums.includes(this.binaryEncoder.checksum)) {
            headers['@enc_'] = this.binaryEncoder.encodeMap;
        }

        headers['@bin_'] = [this.binaryEncoder.checksum];
        return serializer.toBinaryMsgpack(headers, body, this.binaryEncoder);
    }

    decodeMsgpack(messageBytes: Uint8Array, serializer: Serialization): any[] {
        if (!isBinaryMsgpackSerialization(serializer)) {
            throw new Error('binary MsgPack serialization is required');
        }

        const headers = serializer.fromMsgpackHeaders(messageBytes);
        const clientKnownBinaryChecksums = headers.headers['@bin_'] as number[];
        const binaryChecksumUsedByClientOnThisMessage = clientKnownBinaryChecksums[0];

        if (binaryChecksumUsedByClientOnThisMessage !== this.binaryEncoder.checksum) {
            throw new BinaryEncoderUnavailableError();
        }

        const body = serializer.fromMsgpackBody(messageBytes, headers.bodyOffset, this.binaryEncoder);
        return [headers.headers, body];
    }
}
