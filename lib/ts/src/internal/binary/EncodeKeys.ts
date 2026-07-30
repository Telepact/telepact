//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { BinaryEncoding } from '../../internal/binary/BinaryEncoding.js';

export function encodeKeys(given: any, binaryEncoder: BinaryEncoding): any {
    if (given === null || given === undefined) {
        return given;
    }

    if (Array.isArray(given)) {
        const result = new Array(given.length);
        for (let index = 0; index < given.length; index += 1) {
            result[index] = encodeKeys(given[index], binaryEncoder);
        }
        return result;
    }

    if (typeof given === 'object') {
        const newMap = new Map<any, any>();
        for (const key in given) {
            if (Object.prototype.hasOwnProperty.call(given, key)) {
                const finalKey = binaryEncoder.encodeMap.get(key) ?? key;
                newMap.set(finalKey, encodeKeys(given[key], binaryEncoder));
            }
        }
        return newMap;
    }

    return given;
}
