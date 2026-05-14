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

import { addExtension } from 'msgpackr';
import { BinaryPackHeader } from './BinaryEncoding.js';
import { MSGPACK_UNDEFINED_VALUE } from './PackMap.js';

const PACKED_BYTE = 17;
const EMPTY_BUFFER = new Uint8Array(0);

export class MsgpackPacked {
    toString() {
        return 'PACKED';
    }
}
const MSGPACK_PACKED_VALUE = new MsgpackPacked();
const MSGPACK_PACKED_EXT = {
    Class: MsgpackPacked,
    type: PACKED_BYTE,
    pack(instance: MsgpackPacked) {
        return EMPTY_BUFFER;
    },
    unpack(buffer: Uint8Array) {
        return MSGPACK_PACKED_VALUE;
    },
};
addExtension(MSGPACK_PACKED_EXT);

function packRow(m: Map<any, any>, header: BinaryPackHeader): any[] | undefined {
    const row = new Array<any>(header.length - 1);
    const expectedKeys = new Set<any>();

    for (let index = 1; index < header.length; index += 1) {
        const headerEntry = header[index]!;
        const key = Array.isArray(headerEntry) ? headerEntry[0] : headerEntry;
        expectedKeys.add(key);

        if (!m.has(key)) {
            row[index - 1] = MSGPACK_UNDEFINED_VALUE;
            continue;
        }

        const value = m.get(key);
        if (Array.isArray(headerEntry)) {
            if (!(value instanceof Map)) {
                return undefined;
            }
            const nestedRow = packRow(value, headerEntry);
            if (nestedRow === undefined) {
                return undefined;
            }
            row[index - 1] = nestedRow;
        } else {
            row[index - 1] = value;
        }
    }

    for (const key of m.keys()) {
        if (!expectedKeys.has(key)) {
            return undefined;
        }
    }

    while (row.length > 0 && row[row.length - 1] === MSGPACK_UNDEFINED_VALUE) {
        row.pop();
    }

    return row;
}

export function packList(list: any[], header?: BinaryPackHeader): any[] {
    if (list.length === 0 || header === undefined) {
        return list;
    }

    const packedList: any[] = [MSGPACK_PACKED_VALUE];
    for (const entry of list) {
        if (!(entry instanceof Map)) {
            return list;
        }
        const packedRow = packRow(entry, header);
        if (packedRow === undefined) {
            return list;
        }
        packedList.push(packedRow);
    }

    return packedList;
}
