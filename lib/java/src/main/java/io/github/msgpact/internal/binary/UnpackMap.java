package io.github.msgpact.internal.binary;

import static io.github.msgpact.internal.binary.PackMap.UNDEFINED_BYTE;
import static io.github.msgpact.internal.binary.Unpack.unpack;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.msgpack.jackson.dataformat.MessagePackExtensionType;

public class UnpackMap {
    static Map<Integer, Object> unpackMap(List<Object> row, List<Object> header) {
        final var finalMap = new HashMap<Integer, Object>();

        for (int j = 0; j < row.size(); j += 1) {
            final var key = header.get(j + 1);
            final var value = row.get(j);

            if (value instanceof final MessagePackExtensionType t && t.getType() == UNDEFINED_BYTE) {
                continue;
            }

            if (key instanceof final List l) {
                final var nestedHeader = (List<Object>) l;
                final var nestedRow = (List<Object>) value;
                final var m = unpackMap(nestedRow, nestedHeader);
                final var i = (Integer) nestedHeader.get(0);

                finalMap.put(i, m);
            } else {
                final Integer i = (Integer) key;
                final var unpackedValue = unpack(value);

                finalMap.put(i, unpackedValue);
            }
        }

        return finalMap;
    }
}
