package io.github.brenbar.uapi.internal;

import java.util.List;

import static io.github.brenbar.uapi.internal.IsSubMapEntryEqual.isSubMapEntryEqual;

public class PartiallyMatches {
    static boolean partiallyMatches(List<Object> wholeList, Object partElement) {
        for (final var wholeElement : wholeList) {
            if (isSubMapEntryEqual(partElement, wholeElement)) {
                return true;
            }
        }

        return false;
    }
}
