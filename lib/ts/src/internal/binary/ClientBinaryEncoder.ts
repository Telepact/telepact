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

import { ClientBinaryStrategy } from './ClientBinaryStrategy';
import { clientBinaryEncode } from '../../internal/binary/ClientBinaryEncode';
import { clientBinaryDecode } from '../../internal/binary/ClientBinaryDecode';
import { BinaryEncoder } from './BinaryEncoder';
import { BinaryEncoding } from './BinaryEncoding';
import { BinaryEncodingCache } from './BinaryEncodingCache';

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
