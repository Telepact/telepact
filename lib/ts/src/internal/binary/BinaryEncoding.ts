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

export type BinaryPackHeaderValue = null | string | number | BinaryPackHeaderValue[];
export type BinaryPackSiteHeader = [string[], BinaryPackHeaderValue[]];

function clonePackHeaderValue(value: BinaryPackHeaderValue): BinaryPackHeaderValue {
    if (Array.isArray(value)) {
        return value.map((item) => clonePackHeaderValue(item));
    }
    return value;
}

function encodePackHeaderValue(value: BinaryPackHeaderValue, encodeMap: Map<string, number>): BinaryPackHeaderValue {
    if (Array.isArray(value)) {
        return value.map((item) => encodePackHeaderValue(item, encodeMap));
    }
    if (value === null || typeof value === 'number') {
        return value;
    }
    const encodedValue = encodeMap.get(value);
    if (encodedValue === undefined) {
        throw new Error(`Missing binary encoding for pack header key ${value}`);
    }
    return encodedValue;
}

function pathKey(path: readonly (string | number)[]): string {
    return JSON.stringify(path);
}

export class BinaryPackSite {
    public readonly path: string[];
    public readonly header: BinaryPackHeaderValue[];
    public readonly encodedPath: number[];
    public readonly encodedHeader: BinaryPackHeaderValue[];

    constructor(
        path: string[],
        header: BinaryPackHeaderValue[],
        encodedPath: number[],
        encodedHeader: BinaryPackHeaderValue[],
    ) {
        this.path = path;
        this.header = header;
        this.encodedPath = encodedPath;
        this.encodedHeader = encodedHeader;
    }
}

export class BinaryEncoding {
    public readonly encodeMap: Map<string, number>;
    public readonly decodeTable: string[];
    public readonly checksum: number;
    public readonly packSitesHeader: BinaryPackSiteHeader[];
    public readonly packSites: BinaryPackSite[];
    public readonly packSitesByPath: Map<string, BinaryPackSite>;
    public readonly packSitesByEncodedPath: Map<string, BinaryPackSite>;

    constructor(binaryEncodingMap: Map<string, number>, checksum: number, packSitesHeader: BinaryPackSiteHeader[] = []) {
        this.encodeMap = binaryEncodingMap;
        const decodeTable = new Array<string | undefined>(binaryEncodingMap.size);
        for (const [key, value] of binaryEncodingMap.entries()) {
            if (value < 0 || value >= decodeTable.length) {
                throw new Error('Binary encoding ids must be dense sequential integers');
            }
            if (decodeTable[value] !== undefined) {
                throw new Error('Binary encoding ids must be unique');
            }
            decodeTable[value] = key;
        }
        if (decodeTable.some((key) => key === undefined)) {
            throw new Error('Binary encoding ids must be dense sequential integers');
        }
        this.decodeTable = decodeTable as string[];
        this.checksum = checksum;
        this.packSitesHeader = [];
        this.packSites = [];
        this.packSitesByPath = new Map<string, BinaryPackSite>();
        this.packSitesByEncodedPath = new Map<string, BinaryPackSite>();

        for (const packSite of packSitesHeader) {
            if (!Array.isArray(packSite) || packSite.length !== 2) {
                throw new Error('Pack sites must be [path, header] pairs');
            }
            const rawPath = packSite[0];
            const rawHeader = packSite[1];
            if (!Array.isArray(rawPath) || !Array.isArray(rawHeader)) {
                throw new Error('Pack site path and header must be arrays');
            }

            const path = rawPath.map((key) => String(key));
            const header = rawHeader.map((value) => clonePackHeaderValue(value));
            const encodedPath = path.map((key) => {
                const encodedKey = this.encodeMap.get(key);
                if (encodedKey === undefined) {
                    throw new Error(`Missing binary encoding for pack site path key ${key}`);
                }
                return encodedKey;
            });
            const encodedHeader = header.map((value) => encodePackHeaderValue(value, this.encodeMap));
            const site = new BinaryPackSite(path, header, encodedPath, encodedHeader);

            this.packSitesHeader.push([path.slice(), header.map((value) => clonePackHeaderValue(value))]);
            this.packSites.push(site);
            this.packSitesByPath.set(pathKey(path), site);
            this.packSitesByEncodedPath.set(pathKey(encodedPath), site);
        }
    }
}

export function getBinaryPackSitePathKey(path: readonly (string | number)[]): string {
    return pathKey(path);
}
