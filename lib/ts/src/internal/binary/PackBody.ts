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
import { MsgpackPacked, MSGPACK_PACKED_VALUE } from './PackList.js';
import { MSGPACK_UNDEFINED_VALUE } from './PackMap.js';

function packRow(value: Map<any, any>, header: BinaryPackHeader): any[] | undefined {
    const row = new Array<any>(header.length - 1).fill(MSGPACK_UNDEFINED_VALUE);
    const allowedKeys = new Set<any>();
    for (let index = 1; index < header.length; index += 1) {
        const headerEntry = header[index];
        if (Array.isArray(headerEntry)) {
            const nestedKey = headerEntry[0];
            allowedKeys.add(nestedKey);
            if (!value.has(nestedKey)) {
                continue;
            }
            const nestedValue = value.get(nestedKey);
            if (nestedValue === null) {
                row[index - 1] = null;
                continue;
            }
            if (!(nestedValue instanceof Map)) {
                return undefined;
            }
            const packedNestedValue = packRow(nestedValue, headerEntry as BinaryPackHeader);
            if (packedNestedValue === undefined) {
                return undefined;
            }
            row[index - 1] = packedNestedValue;
            continue;
        }
        allowedKeys.add(headerEntry);
        if (value.has(headerEntry)) {
            row[index - 1] = value.get(headerEntry);
        }
    }
    for (const key of value.keys()) {
        if (!allowedKeys.has(key)) {
            return undefined;
        }
    }
    return row;
}

function packSite(value: any, header: BinaryPackHeader): any {
    if (!Array.isArray(value) || value.length === 0) {
        return value;
    }
    const packedRows: any[] = [MSGPACK_PACKED_VALUE, header];
    for (const item of value) {
        if (!(item instanceof Map)) {
            return value;
        }
        const packedRow = packRow(item, header);
        if (packedRow === undefined) {
            return value;
        }
        packedRows.push(packedRow);
    }
    return packedRows;
}

export function packBody(body: Map<any, any>, binaryEncoding: BinaryEncoding): Map<any, any> {
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
        current.set(finalKey, packSite(current.get(finalKey), header));
    }
    return result;
}
