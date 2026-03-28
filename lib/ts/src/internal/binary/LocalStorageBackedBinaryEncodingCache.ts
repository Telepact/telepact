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

export class LocalStorageBackedBinaryEncodingCache extends BinaryEncodingCache {
    private recentBinaryEncoders: Map<number, BinaryEncoding>;
    private recentBinaryEncodersJson: Record<string, Record<string, number>>;
    private namespace: string;

    constructor(namespace: string) {
        super();

        this.namespace = 'telepact-api-encoding:' + namespace

        // Load initial state of recentBinaryEncodersJson from local storage
        const storedJson = localStorage.getItem(this.namespace);

        console.log(`Binary Encoding loaded from local storage for ${this.namespace}: ${storedJson}`);

        let jsonFromLocalStorage: Record<string, Record<string, number>> = storedJson 
            ? JSON.parse(storedJson) 
            : {};

        this.recentBinaryEncodersJson = jsonFromLocalStorage;
        this.recentBinaryEncoders = this.mapJsonToObject(jsonFromLocalStorage);
    }

    add(checksum: number, binaryEncodingMap: Map<string, number>): void {
        const binaryEncodingJson = Object.fromEntries(binaryEncodingMap);
        this.recentBinaryEncodersJson[`${checksum}`] = binaryEncodingJson;

        this.recentBinaryEncoders = this.mapJsonToObject(this.recentBinaryEncodersJson);

        // Save recentBinaryEncodersJson to local storage
        localStorage.setItem(this.namespace, JSON.stringify(this.recentBinaryEncodersJson));
    }

    get(checksum: number): BinaryEncoding | undefined {
        return this.recentBinaryEncoders.get(checksum);
    }

    remove(checksum: number): void {
        delete this.recentBinaryEncodersJson[checksum];

        this.recentBinaryEncoders = this.mapJsonToObject(this.recentBinaryEncodersJson);

        // Save recentBinaryEncodersJson to local storage
        localStorage.setItem(this.namespace, JSON.stringify(this.recentBinaryEncodersJson));
    }

    getChecksums(): number[] {
        return Array.from(this.recentBinaryEncoders.keys());
    }

    private mapJsonToObject(json: Record<string, Record<string, number>>): Map<number, BinaryEncoding> {
        let newMap = new Map<number, BinaryEncoding>();

        for (var [k, v] of Object.entries(json)) {
            let checksum = parseInt(k);
            let binaryEncodingRecord = v as Record<string, number>;
            let binaryEncodingMap = new Map(Object.entries(binaryEncodingRecord));
            let binaryEncoding = new BinaryEncoding(binaryEncodingMap, checksum);
            newMap.set(checksum, binaryEncoding);
        }

        return newMap;
    }
}
