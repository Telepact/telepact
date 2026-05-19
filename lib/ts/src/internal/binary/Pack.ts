//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { packList } from '../../internal/binary/PackList.js';

export function pack(value: any): any {
    if (Array.isArray(value)) {
        return packList(value);
    } else if (value instanceof Map) {
        const newMap: Map<any, any> = new Map();

        for (const [key, val] of value.entries()) {
            newMap.set(key, pack(val));
        }

        return newMap;
    } else {
        return value;
    }
}
