package io.github.brenbar.uapi.internal.binary;

import static io.github.brenbar.uapi.internal.binary.Unpack.unpack;

import java.util.HashMap;
import java.util.Map;

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
