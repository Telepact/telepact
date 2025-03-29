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

import { BinaryEncodingCache } from "../../internal/binary/BinaryEncodingCache";
import { BinaryEncoding } from "./BinaryEncoding";

export class DefaultBinaryEncodingCache extends BinaryEncodingCache {
    private recentBinaryEncoders: Map<number, BinaryEncoding>;

    constructor() {
        super();
        this.recentBinaryEncoders = new Map<number, BinaryEncoding>();
    }

    add(checksum: number, binaryEncodingMap: Map<string, number>): void {
        const binaryEncoding = new BinaryEncoding(binaryEncodingMap, checksum);
        this.recentBinaryEncoders.set(checksum, binaryEncoding);
    }

    get(checksum: number): BinaryEncoding | undefined {
        return this.recentBinaryEncoders.get(checksum);
    }

    remove(checksum: number): void {
        this.recentBinaryEncoders.delete(checksum);
    }

    getChecksums(): number[] {
        return this.recentBinaryEncoders.keys().toArray();;
    }
}
