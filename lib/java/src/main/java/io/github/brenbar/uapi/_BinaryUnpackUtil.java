package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.msgpack.jackson.dataformat.MessagePackExtensionType;

import static io.github.brenbar.uapi._BinaryPackUtil.PACKED_BYTE;
import static io.github.brenbar.uapi._BinaryPackUtil.UNDEFINED_BYTE;

class _BinaryUnpackUtil {
    static Map<Object, Object> unpackBody(Map<Object, Object> body) {
        final var result = new HashMap<Object, Object>();

        for (final var entry : body.entrySet()) {
            final var unpackedValue = unpack(entry.getValue());
            result.put(entry.getKey(), unpackedValue);
        }

        return result;
    }

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

    static List<Object> unpackList(List<Object> list) {
        if (list.size() == 0) {
            return list;
        }

        if (!(list.get(0) instanceof final MessagePackExtensionType t && t.getType() == PACKED_BYTE)) {
            final var newList = new ArrayList<Object>();
            for (final var e : list) {
                newList.add(unpack(e));
            }
            return newList;
        }

        final var unpackedList = new ArrayList<Object>();
        final var headers = (List<Object>) list.get(1);

        for (int i = 2; i < list.size(); i += 1) {
            final var row = (List<Object>) list.get(i);
            final var m = unpackMap(row, headers);

            unpackedList.add(m);
        }

        return unpackedList;
    }

    static Map<Integer, Object> unpackMap(List<Object> row, List<Object> header) {
        final var finalMap = new HashMap<Integer, Object>();

        for (int j = 0; j < row.size(); j += 1) {
            final var key = header.get(j + 1);
            final var value = row.get(j);

            if (value instanceof final MessagePackExtensionType t && t.getType() == UNDEFINED_BYTE) {
                continue;
            }

            if (key instanceof final Integer i) {
                final var unpackedValue = unpack(value);

                finalMap.put(i, unpackedValue);
            } else {
                final var nestedHeader = (List<Object>) key;
                final var nestedRow = (List<Object>) value;
                final var m = unpackMap(nestedRow, nestedHeader);
                final var i = (Integer) nestedHeader.get(0);

                finalMap.put(i, m);
            }
        }

        return finalMap;
    }
}
