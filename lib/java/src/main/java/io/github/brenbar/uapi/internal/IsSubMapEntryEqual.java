package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;
import java.util.Objects;

import static io.github.brenbar.uapi.internal.PartiallyMatches.partiallyMatches;
import static io.github.brenbar.uapi.internal.IsSubMap.isSubMap;

public class IsSubMapEntryEqual {
    static boolean isSubMapEntryEqual(Object partValue, Object wholeValue) {
        if (partValue instanceof final Map m1 && wholeValue instanceof final Map m2) {
            return isSubMap(m1, m2);
        } else if (partValue instanceof final List partList && wholeValue instanceof final List wholeList) {
            for (int i = 0; i < partList.size(); i += 1) {
                final var partElement = partList.get(i);
                final var partMatches = partiallyMatches(wholeList, partElement);
                if (!partMatches) {
                    return false;
                }
            }

            return true;
        } else {
            return Objects.equals(partValue, wholeValue);
        }
    }
}
