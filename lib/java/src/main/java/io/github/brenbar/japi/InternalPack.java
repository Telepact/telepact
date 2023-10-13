package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class InternalPack {

    public static class Undefined {

    }

    public static Map<String, Object> packBody(Map<String, Object> body) {
        var result = new HashMap<String, Object>();

        for (var entry : body.entrySet()) {
            var packedValue = pack(entry.getValue());
            result.put(entry.getKey(), packedValue);
        }

        return result;
    }

    public static Object pack(Object value) {
        if (value instanceof List l) {
            return packList(l);
        } else {
            return value;
        }
    }

    public static List<Object> packList(List<Object> list) {
        var packedList = new ArrayList<Object>();
        packedList.add(new ArrayList<String>());
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
                    var headers = (List<String>) packedList.get(0);
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
}
