import { ExtType } from 'msgpack';
import { PACKED_BYTE } from './PackList';
import { unpack } from './Unpack';
import { unpackMap } from './UnpackMap';

export function unpackList(lst: any[]): any[] {
    if (!lst.length) {
        return lst;
    }

    if (!(lst[0] instanceof ExtType) || lst[0].code !== PACKED_BYTE) {
        const newLst: any[] = [];
        for (const item of lst) {
            newLst.push(unpack(item));
        }
        return newLst;
    }

    const unpackedLst: any[] = [];
    const headers = lst[1] as any[];

    for (let i = 2; i < lst.length; i++) {
        const row = lst[i] as any[];
        const m = unpackMap(row, headers);

        unpackedLst.push(m);
    }

    return unpackedLst;
}
