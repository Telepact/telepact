//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.mock;

import static io.github.telepact.internal.mock.IsSubMapEntryEqual.isSubMapEntryEqual;

import java.util.Map;

public class IsSubMap {
    public static boolean isSubMap(Map<String, Object> part, Map<String, Object> whole) {
        for (final var partKey : part.keySet()) {
            final var wholeValue = whole.get(partKey);
            final var partValue = part.get(partKey);
            final var entryIsEqual = isSubMapEntryEqual(partValue, wholeValue);
            if (!entryIsEqual) {
                return false;
            }
        }
        return true;
    }
}
