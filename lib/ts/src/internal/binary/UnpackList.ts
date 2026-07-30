//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { MsgpackPacked } from './PackList.js';
import { unpack } from './Unpack.js';
import { unpackMap } from './UnpackMap.js';

export function unpackList(list: any[]): any[] {
    if (list.length === 0) {
        return list;
    }

    if (!(list[0] instanceof MsgpackPacked)) {
        const newList = new Array(list.length);
        for (let index = 0; index < list.length; index += 1) {
            newList[index] = unpack(list[index]);
        }
        return newList;
    }

    const unpackedList = new Array(list.length - 2);
    const headers: any[] = list[1];

    for (let i = 2; i < list.length; i += 1) {
        const row: any[] = list[i];
        unpackedList[i - 2] = unpackMap(row, headers);
    }

    return unpackedList;
}
