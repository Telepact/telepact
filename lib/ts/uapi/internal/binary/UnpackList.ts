import { MsgpackPacked } from './PackList';
import { unpack } from './Unpack';
import { unpackMap } from './UnpackMap';

export function unpackList(list: any[]): any[] {
    if (list.length === 0) {
        return list;
    }

    if (!(list[0] instanceof MsgpackPacked)) {
        const newList: any[] = [];
        for (const e of list) {
            newList.push(unpack(e));
        }
        return newList;
    }

    const unpackedList: any[] = [];
    const headers: any[] = list[1];

    for (let i = 2; i < list.length; i += 1) {
        const row: any[] = list[i];
        const m = unpackMap(row, headers);

        unpackedList.push(m);
    }

    return unpackedList;
}
