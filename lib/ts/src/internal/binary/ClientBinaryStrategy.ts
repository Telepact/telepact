//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { BinaryEncodingCache } from "./BinaryEncodingCache.js";

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

        const initialChecksums = binaryEncodingCache.getChecksums();

        const randomPrimary = initialChecksums[0];
        const randomSecondary = initialChecksums[1];

        if (randomPrimary) {
            this.primary = new Checksum(randomPrimary, 0);
        }

        if (randomSecondary) {
            this.secondary = new Checksum(randomSecondary, 0);
        }
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
