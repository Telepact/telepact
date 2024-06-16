import { BinaryPackNode } from './BinaryPackNode';
import { pack } from './Pack';
import { packMap } from './PackMap';
import { CannotPack } from './CannotPack';
import { addExtension } from 'msgpackr';

export const PACKED_BYTE = 17;

class MsgpackPacked {
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
