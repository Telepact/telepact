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

function packRow(m: Map<any, any>, header: BinaryPackHeader): any[] {
    const row = new Array<any>(header.length - 1);

    for (let index = 1; index < header.length; index += 1) {
        const headerEntry = header[index]!;
        const key = Array.isArray(headerEntry) ? headerEntry[0] : headerEntry;

        if (m.has(key)) {
            const value = m.get(key);
            row[index - 1] = Array.isArray(headerEntry) && value instanceof Map
                ? packRow(value, headerEntry)
                : value;
        } else {
            row[index - 1] = MSGPACK_UNDEFINED_VALUE;
        }
    }

    while (row.length > 0 && row[row.length - 1] === MSGPACK_UNDEFINED_VALUE) {
        row.pop();
    }

    return row;
}

export function packList(list: any[], header: BinaryPackHeader): any[] {
    if (list.length === 0) {
        return list;
    }

    const packedList: any[] = [MSGPACK_PACKED_VALUE];
    for (const entry of list) {
        if (!(entry instanceof Map)) {
            return list;
        }
        packedList.push(packRow(entry, header));
    }

    return packedList;
}
