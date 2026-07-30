//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
            newMap[finalKey] = decodeKeys(value, binaryEncoder);
        }
        return newMap;
    }

    return given;
}

function decodeIntegerKey(key: unknown, binaryEncoder: BinaryEncoding): string {
    try {
        return binaryEncoder.decodeTable[key as number].toString();
    } catch {
        throw new BinaryEncodingMissing(key as object);
    }
}
