package io.github.brenbar.uapi.internal.mock;

import java.util.List;
import java.util.Map;
import java.util.Objects;

import static io.github.brenbar.uapi.internal.mock.IsSubMap.isSubMap;
import static io.github.brenbar.uapi.internal.mock.PartiallyMatches.partiallyMatches;

public class IsSubMapEntryEqual {
    public static boolean isSubMapEntryEqual(Object partValue, Object wholeValue) {
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
