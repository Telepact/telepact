package io.github.brenbar.uapi.internal;

import java.util.Map;

import static io.github.brenbar.uapi.internal.IsSubMapEntryEqual.isSubMapEntryEqual;

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
