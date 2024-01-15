package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.msgpack.jackson.dataformat.MessagePackExtensionType;

class _BinaryPackUtil {

    private static final MessagePackExtensionType PACKED = new MessagePackExtensionType((byte) 17, new byte[0]);
    private static final MessagePackExtensionType UNDEFINED = new MessagePackExtensionType((byte) 18, new byte[0]);

    static class Node {
        public final Integer value;
        public final Map<Integer, Node> nested;

        public Node(Integer value, Map<Integer, Node> nested) {
            this.value = value;
            this.nested = nested;
        }
    }

    static Map<Object, Object> packBody(Map<Object, Object> body) {
        final var result = new HashMap<Object, Object>();

        for (final var entry : body.entrySet()) {
            final var packedValue = pack(entry.getValue());
            result.put(entry.getKey(), packedValue);
        }

        return result;
    }

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

    static class CannotPack extends Exception {
    }

    static List<Object> packList(List<Object> list) {
        final var packedList = new ArrayList<Object>();
        final var header = new ArrayList<Object>();

        packedList.add(PACKED);

        header.add(null);

        packedList.add(header);

        final var keyIndexMap = new HashMap<Integer, Node>();
        try {
            for (final var e : list) {
                if (e instanceof final Map<?, ?> m) {
                    final var row = packMap(m, header, keyIndexMap);

                    packedList.add(row);
                } else {
                    // This list cannot be packed, abort
                    throw new CannotPack();
                }
            }
            return packedList;
        } catch (final CannotPack ex) {
            final var newList = new ArrayList<Object>();
            for (final var e : list) {
                newList.add(pack(e));
            }
            return newList;
        }
    }

    static List<Object> packMap(Map<?, ?> m, List<Object> header,
            Map<Integer, Node> keyIndexMap) throws CannotPack {
        final var row = new ArrayList<Object>();
        for (final var entry : m.entrySet()) {
            if (entry.getKey() instanceof final String s) {
                throw new CannotPack();
            }

            final var key = (Integer) entry.getKey();
            final var keyIndex = keyIndexMap.get(key);

            final Node finalKeyIndex;
            if (keyIndex == null) {
                finalKeyIndex = new Node(header.size() - 1, new HashMap<>());

                if (entry.getValue() instanceof Map<?, ?>) {
                    header.add(new ArrayList<>(List.of(key)));
                } else {
                    header.add(key);
                }

                keyIndexMap.put(key, finalKeyIndex);
            } else {
                finalKeyIndex = keyIndex;
            }

            final Object packedValue;
            if (entry.getValue() instanceof Map<?, ?> m2) {
                final List<Object> nestedHeader;
                try {
                    nestedHeader = (List<Object>) header.get(finalKeyIndex.value + 1);
                } catch (ClassCastException e) {
                    throw new CannotPack();
                }

                packedValue = packMap(m2, nestedHeader, finalKeyIndex.nested);
            } else {
                if (header.get(finalKeyIndex.value + 1) instanceof List) {
                    throw new CannotPack();
                }

                packedValue = pack(entry.getValue());
            }

            while (row.size() < finalKeyIndex.value) {
                row.add(UNDEFINED);
            }

            if (row.size() == finalKeyIndex.value) {
                row.add(packedValue);
            } else {
                row.set(finalKeyIndex.value, packedValue);
            }
        }
        return row;
    }

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

        if (!(list.get(0) instanceof final MessagePackExtensionType t && t.getType() == PACKED.getType())) {
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

            if (value instanceof final MessagePackExtensionType t && t.getType() == UNDEFINED.getType()) {
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
