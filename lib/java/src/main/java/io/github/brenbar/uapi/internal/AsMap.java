package io.github.brenbar.uapi.internal;

import java.util.Map;

public class AsMap {

    public static Map<String, Object> asMap(Object object) {
        if (object == null) {
            throw new ClassCastException();
        }

        return (Map<String, Object>) object;
    }
}
