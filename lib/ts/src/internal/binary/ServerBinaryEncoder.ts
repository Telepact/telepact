//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { BinaryEncoder } from './BinaryEncoder.js';
import { BinaryEncoding } from './BinaryEncoding.js';
import { serverBinaryEncode } from './ServerBinaryEncode.js';
import { serverBinaryDecode } from './ServerBinaryDecode.js';

export class ServerBinaryEncoder implements BinaryEncoder {
    private binaryEncoder: BinaryEncoding;

    constructor(binaryEncoder: BinaryEncoding) {
        this.binaryEncoder = binaryEncoder;
    }

    encode(message: any[]): any[] {
        return serverBinaryEncode(message, this.binaryEncoder);
    }

    decode(message: any[]): any[] {
        return serverBinaryDecode(message, this.binaryEncoder);
    }
}
