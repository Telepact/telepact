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

import { ClientBinaryStrategy } from './ClientBinaryStrategy.js';
import { clientBinaryEncode } from '../../internal/binary/ClientBinaryEncode.js';
import { clientBinaryDecode } from '../../internal/binary/ClientBinaryDecode.js';
import { BinaryEncoder } from './BinaryEncoder.js';
import { BinaryEncodingCache } from './BinaryEncodingCache.js';
import { Serialization } from '../../Serialization.js';
import { isBinaryMsgpackSerialization } from './BinaryMsgpackSerialization.js';
import { BinaryEncoderUnavailableError } from './BinaryEncoderUnavailableError.js';

export class ClientBinaryEncoder extends BinaryEncoder {
    private readonly binaryEncodingCache: BinaryEncodingCache;
    private readonly binaryChecksumStrategy: ClientBinaryStrategy;

    constructor(binaryEncodingCache: BinaryEncodingCache) {
        super();
        this.binaryEncodingCache = binaryEncodingCache;
        this.binaryChecksumStrategy = new ClientBinaryStrategy(binaryEncodingCache);
    }

    encode(message: any[]): any[] {
        return clientBinaryEncode(message, this.binaryEncodingCache, this.binaryChecksumStrategy);
    }

    decode(message: any[]): any[] {
        return clientBinaryDecode(message, this.binaryEncodingCache, this.binaryChecksumStrategy);
    }

    encodeToMsgpack(message: any[], serializer: Serialization): Uint8Array {
        if (!isBinaryMsgpackSerialization(serializer)) {
            return super.encodeToMsgpack(message, serializer);
        }

        const headers = message[0] as Record<string, any>;
        const body = message[1] as Record<string, any>;
        const forceSendJson = headers['_forceSendJson'];
        if (forceSendJson !== undefined) {
            delete headers['_forceSendJson'];
        }

        const checksums = this.binaryChecksumStrategy.getCurrentChecksums();
        headers['@bin_'] = checksums;

        if (forceSendJson === true || checksums.length > 1) {
            throw new BinaryEncoderUnavailableError();
        }

        const binaryEncoding = checksums.length > 0 ? this.binaryEncodingCache.get(checksums[0]) : undefined;
        if (!binaryEncoding) {
            throw new BinaryEncoderUnavailableError();
        }

        return serializer.toBinaryMsgpack(headers, body, binaryEncoding);
    }

    decodeMsgpack(messageBytes: Uint8Array, serializer: Serialization): any[] {
        if (!isBinaryMsgpackSerialization(serializer)) {
            return super.decodeMsgpack(messageBytes, serializer);
        }

        const headers = serializer.fromMsgpackHeaders(messageBytes);
        const binaryChecksums = headers.headers['@bin_'] as number[];
        const binaryChecksum = binaryChecksums[0]!;

        if (Object.prototype.hasOwnProperty.call(headers.headers, '@enc_')) {
            const binaryEncoding = headers.headers['@enc_'] as Record<string, number>;
            this.binaryEncodingCache.add(binaryChecksum, binaryEncoding);
        }

        this.binaryChecksumStrategy.updateChecksum(binaryChecksum);
        const newCurrentChecksumStrategy = this.binaryChecksumStrategy.getCurrentChecksums();

        const binaryEncoder = this.binaryEncodingCache.get(newCurrentChecksumStrategy[0]);
        if (!binaryEncoder) {
            throw new BinaryEncoderUnavailableError();
        }

        const body = serializer.fromMsgpackBody(messageBytes, headers.bodyOffset, binaryEncoder);
        return [headers.headers, body];
    }
}
