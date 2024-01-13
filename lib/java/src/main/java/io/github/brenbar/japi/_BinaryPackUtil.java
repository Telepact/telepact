package io.github.brenbar.japi;

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
        var result = new HashMap<Object, Object>();

        for (var entry : body.entrySet()) {
            var packedValue = pack(entry.getValue());
            result.put(entry.getKey(), packedValue);
        }

        return result;
    }

    static Object pack(Object value) {
        if (value instanceof List l) {
            return packList(l);
        } else if (value instanceof Map<?, ?> m) {
            var newMap = new HashMap();
            for (Map.Entry<?, ?> entry : m.entrySet()) {
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
        var packedList = new ArrayList<Object>();
        packedList.add(PACKED);
        var headers = new ArrayList<Object>();
        packedList.add(headers);
        var keyIndexMap = new HashMap<Integer, Node>();
        try {
            for (var e : list) {
                if (e instanceof Map<?, ?> m) {
                    var row = packMap(m, headers, keyIndexMap);
                    packedList.add(row);
                } else {
                    // This list cannot be packed, abort
                    throw new CannotPack();
                }
            }
            return packedList;
        } catch (CannotPack ex) {
            var newList = new ArrayList<Object>();
            for (var e : list) {
                newList.add(pack(e));
            }
            return newList;
        }
    }

    static List<Object> packMap(Map<?, ?> m, List<Object> header,
            Map<Integer, Node> keyIndexMap) throws CannotPack {
        var row = new ArrayList<Object>();
        for (var entry : m.entrySet()) {
            if (entry.getKey() instanceof String s) {
                throw new CannotPack();
            }

            var key = (Integer) entry.getKey();

            var keyIndex = keyIndexMap.get(key);

            if (keyIndex == null) {
                keyIndex = new Node(header.size(), new HashMap<>());
                if (entry.getValue() instanceof Map<?, ?>) {
                    header.add(new ArrayList<>(List.of(key)));
                } else {
                    header.add(key);
                }

                keyIndexMap.put(key, keyIndex);
            }

            Object packedValue;
            if (entry.getValue() instanceof Map<?, ?> m2) {
                var nestedHeader = (List<Object>) header.get(keyIndex.value);
                packedValue = packMap(m2, nestedHeader, keyIndex.nested);
            } else {
                packedValue = pack(entry.getValue());
            }

            while (row.size() < keyIndex.value) {
                row.add(UNDEFINED);
            }

            if (row.size() == keyIndex.value) {
                row.add(packedValue);
            } else {
                row.set(keyIndex.value, packedValue);
            }
        }
        return row;
    }

    static Map<Object, Object> unpackBody(Map<Object, Object> body) {
        var result = new HashMap<Object, Object>();

        for (var entry : body.entrySet()) {
            var unpackedValue = unpack(entry.getValue());
            result.put(entry.getKey(), unpackedValue);
        }

        return result;
    }

    static Object unpack(Object value) {
        if (value instanceof List l) {
            return unpackList(l);
        } else if (value instanceof Map<?, ?> m) {
            var newMap = new HashMap<Object, Object>();
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

        if (!(list.get(0) instanceof MessagePackExtensionType t && t.getType() == PACKED.getType())) {
            var newList = new ArrayList<Object>();
            for (var e : list) {
                newList.add(unpack(e));
            }
            return newList;
        }

        var unpackedList = new ArrayList<Object>();

        var headers = (List<Object>) list.get(1);
        for (int i = 2; i < list.size(); i += 1) {
            var row = (List<Object>) list.get(i);
            var m = unpackMap(row, headers);
            unpackedList.add(m);
        }

        return unpackedList;
    }

    static Map<Integer, Object> unpackMap(List<Object> row, List<Object> header) {
        var finalMap = new HashMap<Integer, Object>();
        for (int j = 0; j < row.size(); j += 1) {
            var key = header.get(j);
            var value = row.get(j);
            if (value instanceof MessagePackExtensionType t && t.getType() == UNDEFINED.getType()) {
                continue;
            }
            if (key instanceof Integer i) {
                var unpackedValue = unpack(value);
                finalMap.put(i, unpackedValue);
            } else {
                var nestedHeader = (List<Object>) key;
                var nestedRow = (List<Object>) value;
                var m = unpackMap(nestedRow, nestedHeader);
                var i = (Integer) nestedHeader.get(0);
                finalMap.put(i, m);
            }
        }
        return finalMap;
    }
}
