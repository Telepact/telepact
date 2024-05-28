package uapi.internal.mock;

import static uapi.internal.mock.IsSubMapEntryEqual.isSubMapEntryEqual;

import java.util.List;

public class PartiallyMatches {
    public static boolean partiallyMatches(List<Object> wholeList, Object partElement) {
        for (final var wholeElement : wholeList) {
            if (isSubMapEntryEqual(partElement, wholeElement)) {
                return true;
            }
        }

        return false;
    }
}
