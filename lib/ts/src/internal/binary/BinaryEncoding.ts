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

export type BinaryPackHeader = Array<number | null | BinaryPackHeader>;
export type BinaryPackSiteData = [string[], BinaryPackHeader];

function cloneBinaryPackHeader(header: BinaryPackHeader): BinaryPackHeader {
    return header.map((entry) => Array.isArray(entry)
        ? cloneBinaryPackHeader(entry)
        : entry) as BinaryPackHeader;
}

function cloneBinaryPackSiteData(site: BinaryPackSiteData): BinaryPackSiteData {
    return [[...site[0]], cloneBinaryPackHeader(site[1])];
}

export class BinaryPackSite {
    public readonly path: string[];
    public readonly encodedPath: number[];
    public readonly header: BinaryPackHeader;

    constructor(site: BinaryPackSiteData, binaryEncodingMap: Map<string, number>) {
        this.path = [...site[0]];
        this.encodedPath = this.path.map((segment) => {
            const encodedSegment = binaryEncodingMap.get(segment);
            if (encodedSegment === undefined) {
                throw new Error(`Missing binary encoding for packed path segment ${segment}`);
            }
            return encodedSegment;
        });
        this.header = cloneBinaryPackHeader(site[1]);
    }

    toData(): BinaryPackSiteData {
        return [[...this.path], cloneBinaryPackHeader(this.header)];
    }
}

export class BinaryEncoding {
    public readonly encodeMap: Map<string, number>;
    public readonly decodeTable: string[];
    public readonly checksum: number;
    public readonly packedSites: BinaryPackSite[];

    constructor(binaryEncodingMap: Map<string, number>, checksum: number, packedSites: BinaryPackSiteData[] = []) {
        this.encodeMap = new Map(binaryEncodingMap);
        const decodeTable = new Array<string | undefined>(this.encodeMap.size);
        for (const [key, value] of this.encodeMap.entries()) {
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
        this.packedSites = packedSites.map((site) => new BinaryPackSite(site, this.encodeMap));
    }

    toPackedSiteData(): BinaryPackSiteData[] {
        return this.packedSites.map((site) => site.toData());
    }
}
