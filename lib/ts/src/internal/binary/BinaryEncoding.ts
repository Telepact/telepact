//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

export class BinaryEncoding {
    public readonly encodeMap: Map<string, number>;
    public readonly decodeTable: string[];
    public readonly checksum: number;

    constructor(binaryEncodingMap: Map<string, number>, checksum: number) {
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
    }
}
