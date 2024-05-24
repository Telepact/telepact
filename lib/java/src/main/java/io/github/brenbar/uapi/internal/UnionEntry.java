package io.github.brenbar.uapi.internal;

import java.util.Map;

public class UnionEntry {
    public static Map.Entry<String, Object> unionEntry(Map<String, Object> union) {
        return union.entrySet().stream().findAny().orElse(null);
    }
}
