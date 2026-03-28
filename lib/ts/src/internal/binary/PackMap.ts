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

import { BinaryPackNode } from './BinaryPackNode';
import { CannotPack } from './CannotPack';
import { pack } from './Pack';
import { addExtension } from 'msgpackr';

const UNDEFINED_BYTE = 18;
export class MsgpackUndefined {
    toString() {
        return 'UNDEFINED';
    }
}
const MSGPACK_UNDEFINED_EXT = {
    Class: MsgpackUndefined,
    type: UNDEFINED_BYTE,
    pack(instance: MsgpackUndefined) {
        return Buffer.from([]);
    },
    unpack(buffer: Buffer) {
        return new MsgpackUndefined();
    },
};
addExtension(MSGPACK_UNDEFINED_EXT);

export function packMap(m: Map<any, any>, header: any[], keyIndexMap: Map<number, BinaryPackNode>): any[] {
    const row: any[] = [];
    for (const [key, value] of m.entries()) {
        if (typeof key === 'string') {
            throw new CannotPack();
        }

        const keyIndex = keyIndexMap.get(key);

        let finalKeyIndex: BinaryPackNode;
        if (keyIndex === undefined) {
            finalKeyIndex = new BinaryPackNode(header.length - 1, new Map());

            if (value instanceof Map) {
                header.push([key]);
            } else {
                header.push(key);
            }

            keyIndexMap.set(key, finalKeyIndex);
        } else {
            finalKeyIndex = keyIndex;
        }

        const keyIndexValue: number = finalKeyIndex.value;
        const keyIndexNested: Map<number, BinaryPackNode> = finalKeyIndex.nested;

        let packedValue: any;
        if (value instanceof Map && value !== null) {
            const nestedHeader: any[] = header[keyIndexValue + 1];
            if (!Array.isArray(nestedHeader)) {
                // No nesting available, so the data structure is inconsistent
                throw new CannotPack();
            }
            packedValue = packMap(value, nestedHeader, keyIndexNested);
        } else {
            if (Array.isArray(header[keyIndexValue + 1])) {
                throw new CannotPack();
            }

            packedValue = pack(value);
        }

        while (row.length < keyIndexValue) {
            row.push(new MsgpackUndefined());
        }

        if (row.length === keyIndexValue) {
            row.push(packedValue);
        } else {
            row[keyIndexValue] = packedValue;
        }
    }
    return row;
}
