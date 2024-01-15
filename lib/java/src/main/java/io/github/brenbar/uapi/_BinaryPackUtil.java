package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.msgpack.jackson.dataformat.MessagePackExtensionType;

class _BinaryPackUtil {

    public static final MessagePackExtensionType PACKED = new MessagePackExtensionType((byte) 17, new byte[0]);
    public static final MessagePackExtensionType UNDEFINED = new MessagePackExtensionType((byte) 18, new byte[0]);

    private static class _BinaryPackNode {
        public final Integer value;
        public final Map<Integer, _BinaryPackNode> nested;

        public _BinaryPackNode(Integer value, Map<Integer, _BinaryPackNode> nested) {
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

        final var keyIndexMap = new HashMap<Integer, _BinaryPackNode>();
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
            Map<Integer, _BinaryPackNode> keyIndexMap) throws CannotPack {
        final var row = new ArrayList<Object>();
        for (final var entry : m.entrySet()) {
            if (entry.getKey() instanceof final String s) {
                throw new CannotPack();
            }

            final var key = (Integer) entry.getKey();
            final var keyIndex = keyIndexMap.get(key);

            final _BinaryPackNode finalKeyIndex;
            if (keyIndex == null) {
                finalKeyIndex = new _BinaryPackNode(header.size() - 1, new HashMap<>());

                if (entry.getValue() instanceof Map<?, ?>) {
                    header.add(new ArrayList<>(List.of(key)));
                } else {
                    header.add(key);
                }

                keyIndexMap.put(key, finalKeyIndex);
            } else {
                finalKeyIndex = keyIndex;
            }

            final Integer keyIndexValue = finalKeyIndex.value;
            final Map<Integer, _BinaryPackNode> keyIndexNested = finalKeyIndex.nested;

            final Object packedValue;
            if (entry.getValue() instanceof Map<?, ?> m2) {
                final List<Object> nestedHeader;
                try {
                    nestedHeader = (List<Object>) header.get(keyIndexValue + 1);
                } catch (ClassCastException e) {
                    throw new CannotPack();
                }

                packedValue = packMap(m2, nestedHeader, keyIndexNested);
            } else {
                if (header.get(keyIndexValue + 1) instanceof List) {
                    throw new CannotPack();
                }

                packedValue = pack(entry.getValue());
            }

            while (row.size() < keyIndexValue) {
                row.add(UNDEFINED);
            }

            if (row.size() == keyIndexValue) {
                row.add(packedValue);
            } else {
                row.set(keyIndexValue, packedValue);
            }
        }
        return row;
    }
}
