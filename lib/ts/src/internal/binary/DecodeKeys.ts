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

import { BinaryEncoding } from '../../internal/binary/BinaryEncoding.js';
import { BinaryEncodingMissing } from '../../internal/binary/BinaryEncodingMissing.js';

export function decodeKeys(given: any, binaryEncoder: BinaryEncoding): any {
    if (Array.isArray(given)) {
        const result = new Array(given.length);
        for (let index = 0; index < given.length; index += 1) {
            result[index] = decodeKeys(given[index], binaryEncoder);
        }
        return result;
    }

    if (given instanceof Map) {
        const newMap: { [key: string]: any } = {};
        for (const [key, value] of given.entries()) {
            const finalKey = typeof key === 'string' ? key : decodeIntegerKey(key, binaryEncoder);
            if (finalKey === undefined) {
                throw new BinaryEncodingMissing(key);
            }
            newMap[finalKey] = decodeKeys(value, binaryEncoder);
        }
        return newMap;
    }

    return given;
}

function decodeIntegerKey(key: unknown, binaryEncoder: BinaryEncoding): string | undefined {
    if (!Number.isInteger(key)) {
        return undefined;
    }
    const keyId = key as number;
    if (keyId < 0 || keyId >= binaryEncoder.decodeTable.length) {
        return undefined;
    }
    return binaryEncoder.decodeTable[keyId];
}
