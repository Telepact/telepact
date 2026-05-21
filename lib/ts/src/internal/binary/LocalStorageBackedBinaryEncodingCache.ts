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

import { BinaryEncoding, BinaryPackSiteData } from "./BinaryEncoding.js";
import { BinaryEncodingCache } from "../../internal/binary/BinaryEncodingCache.js";

type StoredBinaryEncoding = {
    encodeMap: Record<string, number>;
    packedSites: BinaryPackSiteData[];
};

type LegacyStoredBinaryEncoding = Record<string, number>;

export class LocalStorageBackedBinaryEncodingCache extends BinaryEncodingCache {
    private recentBinaryEncoders: Map<number, BinaryEncoding>;
    private recentBinaryEncodersJson: Record<string, StoredBinaryEncoding | LegacyStoredBinaryEncoding>;
    private namespace: string;

    constructor(namespace: string) {
        super();

        this.namespace = 'telepact-api-encoding:' + namespace

        const storedJson = localStorage.getItem(this.namespace);

        console.log(`Binary Encoding loaded from local storage for ${this.namespace}: ${storedJson}`);

        const jsonFromLocalStorage = storedJson
            ? JSON.parse(storedJson) as Record<string, StoredBinaryEncoding | LegacyStoredBinaryEncoding>
            : {};

        this.recentBinaryEncodersJson = jsonFromLocalStorage;
        this.recentBinaryEncoders = this.mapJsonToObject(jsonFromLocalStorage);
    }

    add(checksum: number, binaryEncodingMap: Map<string, number>, packedSites: BinaryPackSiteData[] = []): void {
        const binaryEncodingJson = Object.fromEntries(binaryEncodingMap);
        this.recentBinaryEncodersJson[`${checksum}`] = {
            encodeMap: binaryEncodingJson,
            packedSites,
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

    private mapJsonToObject(json: Record<string, StoredBinaryEncoding | LegacyStoredBinaryEncoding>): Map<number, BinaryEncoding> {
        const newMap = new Map<number, BinaryEncoding>();

        for (const [key, value] of Object.entries(json)) {
            const checksum = parseInt(key, 10);
            const { encodeMap, packedSites } = this.normalizeStoredBinaryEncoding(value);
            const binaryEncodingMap = new Map(Object.entries(encodeMap));
            const binaryEncoding = new BinaryEncoding(binaryEncodingMap, checksum, packedSites);
            newMap.set(checksum, binaryEncoding);
        }

        return newMap;
    }

    private normalizeStoredBinaryEncoding(value: StoredBinaryEncoding | LegacyStoredBinaryEncoding): StoredBinaryEncoding {
        if ('encodeMap' in value) {
            const storedValue = value as StoredBinaryEncoding;
            return {
                encodeMap: storedValue.encodeMap,
                packedSites: storedValue.packedSites ?? [],
            };
        }

        return {
            encodeMap: value,
            packedSites: [],
        };
    }
}
