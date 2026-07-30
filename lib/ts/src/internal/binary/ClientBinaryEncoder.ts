//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { ClientBinaryStrategy } from './ClientBinaryStrategy.js';
import { clientBinaryEncode } from '../../internal/binary/ClientBinaryEncode.js';
import { clientBinaryDecode } from '../../internal/binary/ClientBinaryDecode.js';
import { BinaryEncoder } from './BinaryEncoder.js';
import { BinaryEncoding } from './BinaryEncoding.js';
import { BinaryEncodingCache } from './BinaryEncodingCache.js';

export class ClientBinaryEncoder implements BinaryEncoder {
    private readonly binaryEncodingCache: BinaryEncodingCache;
    private readonly binaryChecksumStrategy: ClientBinaryStrategy;

    constructor(binaryEncodingCache: BinaryEncodingCache) {
        this.binaryEncodingCache = binaryEncodingCache;
        this.binaryChecksumStrategy = new ClientBinaryStrategy(binaryEncodingCache);
    }

    encode(message: any[]): any[] {
        return clientBinaryEncode(message, this.binaryEncodingCache, this.binaryChecksumStrategy);
    }

    decode(message: any[]): any[] {
        return clientBinaryDecode(message, this.binaryEncodingCache, this.binaryChecksumStrategy);
    }
}
