package io.github.brenbar.uapi.internal;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static io.github.brenbar.uapi.internal.UnpackList.unpackList;

public class Unpack {

    static Object unpack(Object value) {
        if (value instanceof final List l) {
            return unpackList(l);
        } else if (value instanceof final Map<?, ?> m) {
            final var newMap = new HashMap<Object, Object>();

            for (Map.Entry<?, ?> entry : m.entrySet()) {
                newMap.put(entry.getKey(), unpack(entry.getValue()));
            }

            return newMap;
        } else {
            return value;
        }
    }
}
