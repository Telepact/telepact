package uapi.internal.binary;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class EncodeKeys {
    static Object encodeKeys(Object given, BinaryEncoding binaryEncoder) {
        if (given == null) {
            return given;
        } else if (given instanceof final Map<?, ?> m) {
            final var newMap = new HashMap<Object, Object>();

            for (final var e : m.entrySet()) {
                final var key = e.getKey();

                final Object finalKey;
                if (binaryEncoder.encodeMap.containsKey(key)) {
                    finalKey = binaryEncoder.encodeMap.get(key);
                } else {
                    finalKey = key;
                }

                final var encodedValue = encodeKeys(e.getValue(), binaryEncoder);

                newMap.put(finalKey, encodedValue);
            }

            return newMap;
        } else if (given instanceof List<?> l) {
            return l.stream().map(e -> encodeKeys(e, binaryEncoder)).toList();
        } else {
            return given;
        }
    }
}
