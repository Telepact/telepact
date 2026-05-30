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
        const uniformResult = tryDecodeUniformMapArray(given, binaryEncoder);
        if (uniformResult !== undefined) {
            return uniformResult;
        }

        const result = new Array(given.length);
        for (let index = 0; index < given.length; index += 1) {
            const value = given[index];
            result[index] = value !== null && typeof value === 'object'
                ? decodeKeys(value, binaryEncoder)
                : value;
        }
        return result;
    }

    if (given instanceof Map) {
        const newMap: { [key: string]: any } = {};
        for (const [key, value] of given.entries()) {
            const finalKey = typeof key === 'string' ? key : decodeIntegerKey(key, binaryEncoder);
            newMap[finalKey] = value !== null && typeof value === 'object'
                ? decodeKeys(value, binaryEncoder)
                : value;
        }
        return newMap;
    }

    if (typeof given === 'object' && given !== null) {
        const newMap: { [key: string]: any } = {};
        for (const key in given) {
            if (Object.prototype.hasOwnProperty.call(given, key)) {
                const finalKey = isIntegerKey(key) ? decodeIntegerKey(Number(key), binaryEncoder) : key;
                const value = given[key];
                newMap[finalKey] = value !== null && typeof value === 'object'
                    ? decodeKeys(value, binaryEncoder)
                    : value;
            }
        }
        return newMap;
    }

    return given;
}

function tryDecodeUniformMapArray(given: any[], binaryEncoder: BinaryEncoding): any[] | undefined {
    if (given.length < 16) {
        return undefined;
    }

    const first = given[0];
    if (!(first instanceof Map) || first.size === 0) {
        return undefined;
    }

    const rawKeys = new Array(first.size);
    const finalKeys = new Array(first.size);
    let keyIndex = 0;
    for (const key of first.keys()) {
        rawKeys[keyIndex] = key;
        finalKeys[keyIndex] = typeof key === 'string' ? key : decodeIntegerKey(key, binaryEncoder);
        keyIndex += 1;
    }
    const canTrustOrder = rawKeys.every((key) => typeof key === 'number');

    const result = new Array(given.length);
    for (let rowIndex = 0; rowIndex < given.length; rowIndex += 1) {
        const row = given[rowIndex];
        if (!(row instanceof Map) || row.size !== finalKeys.length) {
            return undefined;
        }

        const decodedRow: { [key: string]: any } = {};
        if (canTrustOrder) {
            let valueIndex = 0;
            for (const value of row.values()) {
                decodedRow[finalKeys[valueIndex]] = value !== null && typeof value === 'object'
                    ? decodeKeys(value, binaryEncoder)
                    : value;
                valueIndex += 1;
            }
        } else {
            let valueIndex = 0;
            for (const [key, value] of row.entries()) {
                const finalKey = key === rawKeys[valueIndex]
                    ? finalKeys[valueIndex]
                    : (typeof key === 'string' ? key : decodeIntegerKey(key, binaryEncoder));
                decodedRow[finalKey] = value !== null && typeof value === 'object'
                    ? decodeKeys(value, binaryEncoder)
                    : value;
                valueIndex += 1;
            }
        }
        result[rowIndex] = decodedRow;
    }

    return result;
}

function isIntegerKey(key: string): boolean {
    if (key.length === 0) {
        return false;
    }
    let start = 0;
    if (key[0] === '-') {
        if (key.length === 1) {
            return false;
        }
        start = 1;
    }
    for (let index = start; index < key.length; index += 1) {
        const code = key.charCodeAt(index);
        if (code < 48 || code > 57) {
            return false;
        }
    }
    return true;
}

function decodeIntegerKey(key: unknown, binaryEncoder: BinaryEncoding): string {
    try {
        const decoded = binaryEncoder.decodeTable[key as number];
        if (decoded === undefined) {
            throw new Error();
        }
        return decoded.toString();
    } catch {
        throw new BinaryEncodingMissing(key as object);
    }
}
