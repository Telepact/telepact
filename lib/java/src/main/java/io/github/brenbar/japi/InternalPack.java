package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class InternalPack {

    static class Undefined {

    }

    static class Packed {
    }

    static Map<String, Object> packBody(Map<String, Object> body) {
        var result = new HashMap<String, Object>();

        for (var entry : body.entrySet()) {
            var packedValue = pack(entry.getValue());
            result.put(entry.getKey(), packedValue);
        }

        return result;
    }

    static Map<String, Object> unpackBody(Map<String, Object> body) {
        var result = new HashMap<String, Object>();

        for (var entry : body.entrySet()) {
            var unpackedValue = pack(entry.getValue());
            result.put(entry.getKey(), unpackedValue);
        }

        return result;
    }

    static Object pack(Object value) {
        if (value instanceof List l) {
            return packList(l);
        } else {
            return value;
        }
    }

    static Object unpack(Object value) {
        if (value instanceof List l) {
            return unpackList(l);
        } else {
            return value;
        }
    }

    static List<Object> packList(List<Object> list) {
        var packedList = new ArrayList<Object>();
        packedList.add(new Packed());
        var headers = new ArrayList<String>();
        packedList.add(headers);
        var keyIndexMap = new HashMap<String, Integer>();
        var index = 0;
        for (var e : list) {
            if (e instanceof Map<?, ?> m) {
                var row = new ArrayList<Object>();
                for (var entry : m.entrySet()) {
                    var key = (String) entry.getKey();
                    if (key.startsWith(".")) {
                        // This is an untyped map, abort
                        return list;
                    }
                    var keyIndex = keyIndexMap.get(key);
                    if (keyIndex == null) {
                        headers.add(key);
                        keyIndexMap.put(key, index);
                        index += 1;
                    }
                    while (row.size() < keyIndex) {
                        row.add(new Undefined());
                    }
                    var packedValue = pack(entry.getValue());
                    row.set(keyIndex, packedValue);
                }
                packedList.add(row);
            } else {
                // This list cannot be packed, abort
                return list;
            }
        }
        return packedList;
    }

    static List<Object> unpackList(List<Object> list) {
        if (list.size() == 0) {
            return list;
        }

        if (!(list.get(0) instanceof Packed)) {
            return list;
        }

        var unpackedList = new ArrayList<Object>();

        var headers = (List<String>) list.get(1);
        for (int i = 2; i < list.size(); i += 1) {
            var row = (List<Object>) list.get(i);
            var m = new HashMap<String, Object>();
            for (int j = 0; j < row.size(); j += 1) {
                var key = headers.get(j);
                var value = row.get(j);
                m.put(key, value);
            }
            unpackedList.add(m);
        }

        return unpackedList;
    }
}
