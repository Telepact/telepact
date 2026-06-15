//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { MsgpackUndefined } from './PackMap.js';
import { unpack } from './Unpack.js';

export function unpackMap(row: any[], header: any[]): Map<any, any> {
    const finalMap = new Map<any, any>();

    for (let j = 0; j < row.length; j += 1) {
        const key = header[j + 1];
        const value = row[j];

        if (value instanceof MsgpackUndefined) {
            continue;
        }

        if (Array.isArray(key)) {
            const nestedHeader = key as any[];
            const nestedRow = value as any[];
            const m = unpackMap(nestedRow, nestedHeader);
            const i = nestedHeader[0] as number;
            finalMap.set(i, m);
        } else {
            finalMap.set(key, unpack(value));
        }
    }

    return finalMap;
}
