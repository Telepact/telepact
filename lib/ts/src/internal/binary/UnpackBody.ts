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

import { BinaryEncoding, BinaryPackHeader } from './BinaryEncoding.js';
import { MsgpackPacked } from './PackList.js';
import { MsgpackUndefined } from './PackMap.js';

function headersMatch(actual: any, expected: any): boolean {
    if (Array.isArray(actual) && Array.isArray(expected)) {
        if (actual.length !== expected.length) {
            return false;
        }
        for (let index = 0; index < actual.length; index += 1) {
            if (!headersMatch(actual[index], expected[index])) {
                return false;
            }
        }
        return true;
    }
    return actual === expected;
}

function unpackRow(row: any[], header: BinaryPackHeader): Map<any, any> {
    const unpackedRow = new Map<any, any>();
    for (let index = 1; index < header.length; index += 1) {
        if (index - 1 >= row.length) {
            break;
        }
        const value = row[index - 1];
        if (value instanceof MsgpackUndefined) {
            continue;
        }
        const headerEntry = header[index];
        if (Array.isArray(headerEntry)) {
            const nestedKey = headerEntry[0];
            if (value === null) {
                unpackedRow.set(nestedKey, null);
                continue;
            }
            if (!Array.isArray(value)) {
                continue;
            }
            unpackedRow.set(nestedKey, unpackRow(value, headerEntry as BinaryPackHeader));
            continue;
        }
        unpackedRow.set(headerEntry, value);
    }
    return unpackedRow;
}

function unpackSite(value: any, header: BinaryPackHeader): any {
    if (!Array.isArray(value) || value.length < 2 || !(value[0] instanceof MsgpackPacked)) {
        return value;
    }
    if (!headersMatch(value[1], header)) {
        return value;
    }
    return value.slice(2).filter(Array.isArray).map((row) => unpackRow(row, header));
}

export function unpackBody(body: Map<any, any>, binaryEncoding: BinaryEncoding): Map<any, any> {
    const result: Map<any, any> = new Map(body);
    for (const [path, header] of binaryEncoding.encodedPackSites) {
        let current: any = result;
        for (const key of path.slice(0, -1)) {
            if (!(current instanceof Map) || !current.has(key)) {
                current = undefined;
                break;
            }
            current = current.get(key);
        }
        if (!(current instanceof Map)) {
            continue;
        }
        const finalKey = path[path.length - 1]!;
        if (!current.has(finalKey)) {
            continue;
        }
        current.set(finalKey, unpackSite(current.get(finalKey), header));
    }
    return result;
}
