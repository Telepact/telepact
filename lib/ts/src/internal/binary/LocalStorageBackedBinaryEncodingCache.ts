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

import { BinaryEncodingCache } from "../../internal/binary/BinaryEncodingCache.js";
import { BinaryEncoding, BinaryPackSiteHeader } from "./BinaryEncoding.js";

type StoredBinaryEncoding = {
    "@enc_": Record<string, number>;
    "@encp_": BinaryPackSiteHeader[];
};

type StoredBinaryEncodingCacheEntry = Record<string, number> | StoredBinaryEncoding;

function isStoredBinaryEncoding(value: StoredBinaryEncodingCacheEntry): value is StoredBinaryEncoding {
    return Object.prototype.hasOwnProperty.call(value, '@enc_');
}

export class LocalStorageBackedBinaryEncodingCache extends BinaryEncodingCache {
    private recentBinaryEncoders: Map<number, BinaryEncoding>;
    private recentBinaryEncodersJson: Record<string, StoredBinaryEncodingCacheEntry>;
    private namespace: string;

    constructor(namespace: string) {
        super();

        this.namespace = 'telepact-api-encoding:' + namespace;

        const storedJson = localStorage.getItem(this.namespace);

        console.log(`Binary Encoding loaded from local storage for ${this.namespace}: ${storedJson}`);

        const jsonFromLocalStorage = storedJson
            ? JSON.parse(storedJson) as Record<string, StoredBinaryEncodingCacheEntry>
            : {};

        this.recentBinaryEncodersJson = jsonFromLocalStorage;
        this.recentBinaryEncoders = this.mapJsonToObject(jsonFromLocalStorage);
    }

    add(checksum: number, binaryEncodingMap: Map<string, number>, packSitesHeader: BinaryPackSiteHeader[] = []): void {
        const binaryEncodingJson = Object.fromEntries(binaryEncodingMap);
        this.recentBinaryEncodersJson[`${checksum}`] = {
            '@enc_': binaryEncodingJson,
            '@encp_': packSitesHeader,
        };

        this.recentBinaryEncoders = this.mapJsonToObject(this.recentBinaryEncodersJson);
        localStorage.setItem(this.namespace, JSON.stringify(this.recentBinaryEncodersJson));
    }

    get(checksum: number): BinaryEncoding | undefined {
        return this.recentBinaryEncoders.get(checksum);
    }

    remove(checksum: number): void {
        delete this.recentBinaryEncodersJson[checksum];

        this.recentBinaryEncoders = this.mapJsonToObject(this.recentBinaryEncodersJson);
        localStorage.setItem(this.namespace, JSON.stringify(this.recentBinaryEncodersJson));
    }

    getChecksums(): number[] {
        return Array.from(this.recentBinaryEncoders.keys());
    }

    private mapJsonToObject(json: Record<string, StoredBinaryEncodingCacheEntry>): Map<number, BinaryEncoding> {
        const newMap = new Map<number, BinaryEncoding>();

        for (const [checksumKey, entry] of Object.entries(json)) {
            const checksum = parseInt(checksumKey, 10);
            const storedEncoding = isStoredBinaryEncoding(entry)
                ? entry
                : { '@enc_': entry, '@encp_': [] };
            const binaryEncodingMap = new Map<string, number>(Object.entries(storedEncoding['@enc_']));
            const binaryEncoding = new BinaryEncoding(binaryEncodingMap, checksum, storedEncoding['@encp_'] || []);
            newMap.set(checksum, binaryEncoding);
        }

        return newMap;
    }
}
