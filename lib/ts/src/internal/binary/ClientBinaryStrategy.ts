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

import { BinaryEncodingCache } from "./BinaryEncodingCache";

export class Checksum {
    constructor(
        public value: number,
        public expiration: number,
    ) {}
}

export class ClientBinaryStrategy {
    private primary: Checksum | null = null;
    private secondary: Checksum | null = null;
    private lastUpdate: Date = new Date();
    private binaryEncodingCache: BinaryEncodingCache;

    constructor(binaryEncodingCache: BinaryEncodingCache) {
        this.binaryEncodingCache = binaryEncodingCache;
    }

    updateChecksum(newChecksum: number): void {
        if (!this.primary) {
            this.primary = new Checksum(newChecksum, 0);
            return;
        }

        if (this.primary.value !== newChecksum) {
            let expiredChecksum = this.secondary;
            this.secondary = this.primary;
            this.primary = new Checksum(newChecksum, 0);
            if (this.secondary) {
                this.secondary.expiration += 1;
            }

            if (expiredChecksum) {
                this.binaryEncodingCache.remove(expiredChecksum.value);
            }

            return;
        }

        this.lastUpdate = new Date();
    }

    getCurrentChecksums(): number[] {
        if (!this.primary) {
            return [];
        } else if (!this.secondary) {
            return [this.primary.value];
        } else {
            const minutesSinceLastUpdate = (Date.now() - this.lastUpdate.getTime()) / (1000 * 60);

            // Every 10 minute interval of non-use is a penalty point
            const penalty = Math.floor(minutesSinceLastUpdate / 10) + 1;

            if (this.secondary) {
                this.secondary.expiration += 1 * penalty;
            }

            if (this.secondary && this.secondary.expiration > 5) {
                this.secondary = null;
                return [this.primary.value];
            } else {
                return [this.primary.value, this.secondary.value];
            }
        }
    }
}
