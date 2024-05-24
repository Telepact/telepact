package io.github.brenbar.uapi.internal;

import java.util.HashMap;
import java.util.Map;

import static io.github.brenbar.uapi.internal.Pack.pack;

public class PackBody {
    static Map<Object, Object> packBody(Map<Object, Object> body) {
        final var result = new HashMap<Object, Object>();

        for (final var entry : body.entrySet()) {
            final var packedValue = pack(entry.getValue());
            result.put(entry.getKey(), packedValue);
        }

        return result;
    }
}
