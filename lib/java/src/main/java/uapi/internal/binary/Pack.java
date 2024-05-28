package uapi.internal.binary;

import static uapi.internal.binary.PackList.packList;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Pack {
    static Object pack(Object value) {
        if (value instanceof final List l) {
            return packList(l);
        } else if (value instanceof final Map<?, ?> m) {
            final var newMap = new HashMap<Object, Object>();

            for (final var entry : m.entrySet()) {
                newMap.put(entry.getKey(), pack(entry.getValue()));
            }

            return newMap;
        } else {
            return value;
        }
    }
}
