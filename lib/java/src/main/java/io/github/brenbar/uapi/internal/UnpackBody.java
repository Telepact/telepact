package io.github.brenbar.uapi.internal;

import java.util.HashMap;
import java.util.Map;

import static io.github.brenbar.uapi.internal.Unpack.unpack;

public class UnpackBody {
    static Map<Object, Object> unpackBody(Map<Object, Object> body) {
        final var result = new HashMap<Object, Object>();

        for (final var entry : body.entrySet()) {
            final var unpackedValue = unpack(entry.getValue());
            result.put(entry.getKey(), unpackedValue);
        }

        return result;
    }
}
