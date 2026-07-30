//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { isSubMapEntryEqual } from '../../internal/mock/IsSubMapEntryEqual.js';

export function isSubMap(part: Record<string, any>, whole: Record<string, any>): boolean {
    for (const partKey in part) {
        const wholeValue = whole[partKey] as Record<string, any>;
        const partValue = part[partKey] as Record<string, any>;
        const entryIsEqual = isSubMapEntryEqual(partValue, wholeValue);
        if (!entryIsEqual) {
            return false;
        }
    }
    return true;
}
