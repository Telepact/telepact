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

export class BinaryEncoding {
    public readonly encodeMap: Map<string, number>;
    public readonly decodeTable: string[];
    public readonly checksum: number;

    constructor(binaryEncodingMap: Map<string, number>, checksum: number) {
        this.encodeMap = binaryEncodingMap;
        let maxId = -1;
        for (const value of binaryEncodingMap.values()) {
            if (value > maxId) {
                maxId = value;
            }
        }
        this.decodeTable = new Array<string>(maxId + 1);
        for (const [key, value] of binaryEncodingMap.entries()) {
            this.decodeTable[value] = key;
        }
        this.checksum = checksum;
    }
}
