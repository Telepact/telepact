//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { isSubMapEntryEqual } from './IsSubMapEntryEqual.js';

export function partiallyMatches(wholeList: any[], partElement: any): boolean {
    for (const wholeElement of wholeList) {
        if (isSubMapEntryEqual(partElement, wholeElement)) {
            return true;
        }
    }
    return false;
}
