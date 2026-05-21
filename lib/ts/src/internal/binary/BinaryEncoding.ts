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

export type BinaryPackHeaderEntry = number | null | BinaryPackHeader;
export type BinaryPackHeader = BinaryPackHeaderEntry[];
export type BinaryPackSite = [string[], any[]];

function compilePackHeader(header: any[], encodeMap: Map<string, number>): BinaryPackHeader {
    const compiledHeader: BinaryPackHeader = [header[0] === null ? null : encodeMap.get(header[0])!];
    for (const entry of header.slice(1)) {
        if (Array.isArray(entry)) {
            compiledHeader.push(compilePackHeader(entry, encodeMap));
        } else {
            compiledHeader.push(encodeMap.get(entry)!);
        }
    }
    return compiledHeader;
}

export class BinaryEncoding {
    public readonly encodeMap: Map<string, number>;
    public readonly decodeTable: string[];
    public readonly checksum: number;
    public readonly packSites: BinaryPackSite[];
    public readonly encodedPackSites: Array<[number[], BinaryPackHeader]>;

    constructor(binaryEncodingMap: Map<string, number>, checksum: number, packSites: BinaryPackSite[] = []) {
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
        this.packSites = packSites.map(([path, header]) => [[...path], header] as BinaryPackSite);
        this.encodedPackSites = this.packSites.map(([path, header]) => [
            path.map((key) => this.encodeMap.get(key)!),
            compilePackHeader(header, this.encodeMap),
        ]);
    }
}
