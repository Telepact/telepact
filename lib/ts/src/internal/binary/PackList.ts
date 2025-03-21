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
import { pack } from './Pack';
import { packMap } from './PackMap';
import { CannotPack } from './CannotPack';
import { addExtension } from 'msgpackr';

const PACKED_BYTE = 17;

export class MsgpackPacked {
    toString() {
        return 'PACKED';
    }
}
const MSGPACK_PACKED_EXT = {
    Class: MsgpackPacked,
    type: PACKED_BYTE,
    pack(instance: MsgpackPacked) {
        return Buffer.from([]);
    },
    unpack(buffer: Buffer) {
        return new MsgpackPacked();
    },
};
addExtension(MSGPACK_PACKED_EXT);

export function packList(list: any[]): any[] {
    if (list.length === 0) {
        return list;
    }

    const packedList: any[] = [];
    const header: any[] = [];

    packedList.push(new MsgpackPacked());

    header.push(null);

    packedList.push(header);

    const keyIndexMap: Map<number, BinaryPackNode> = new Map();
    try {
        for (const e of list) {
            if (e instanceof Map) {
                const row = packMap(e, header, keyIndexMap);

                packedList.push(row);
            } else {
                // This list cannot be packed, abort
                throw new CannotPack();
            }
        }
        return packedList;
    } catch (ex) {
        const newList: any[] = [];
        for (const e of list) {
            newList.push(pack(e));
        }
        return newList;
    }
}
