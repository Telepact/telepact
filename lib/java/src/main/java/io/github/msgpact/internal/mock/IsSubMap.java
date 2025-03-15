package io.github.msgpact.internal.mock;

import static io.github.msgpact.internal.mock.IsSubMapEntryEqual.isSubMapEntryEqual;

import java.util.Map;

public class IsSubMap {
    static boolean isSubMap(Map<String, Object> part, Map<String, Object> whole) {
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
