package io.github.telepact.internal.binary;

import java.util.ArrayList;
import java.util.Base64;
import java.util.List;
import java.util.Map;

public class ServerBase64Decode {

    public static void serverBase64Decode(Map<String, Object> body, Map<String, Object> bytesPaths) {
        travelBase64Decode(body, bytesPaths);
    }

    private static Object travelBase64Decode(Object value, Object bytesPaths) {
        if (bytesPaths instanceof Map) {
            Map<String, Object> bytesPathsMap = (Map<String, Object>) bytesPaths;
            for (Map.Entry<String, Object> entry : bytesPathsMap.entrySet()) {
                String key = entry.getKey();
                Object val = entry.getValue();

                if (Boolean.TRUE.equals(val)) {
                     if ("*".equals(key) && value instanceof List) {
                        final var newList = new ArrayList<>();
                        List<Object> valueList = (List<Object>) value;
                        for (int i = 0; i < valueList.size(); i++) {
                            Object nv = travelBase64Decode(valueList.get(i), val);
                            newList.add(nv);
                        }
                        return newList;
                    } else if ("*".equals(key) && value instanceof Map) {
                        Map<String, Object> valueMap = (Map<String, Object>) value;
                        for (Map.Entry<String, Object> valueEntry : valueMap.entrySet()) {
                            Object nv = travelBase64Decode(valueEntry.getValue(), val);
                            valueMap.put(valueEntry.getKey(), nv);
                        }
                    } else if (value instanceof Map) {
                        Map<String, Object> valueMap = (Map<String, Object>) value;
                        Object nv = travelBase64Decode(valueMap.get(key), val);
                        valueMap.put(key, nv);
                    } else {
                        throw new IllegalArgumentException("Invalid bytes path: " + key + " for value: " + value);
                    }
                } else {
                    if ("*".equals(key) && value instanceof List) {
                        final var newList = new ArrayList<>();
                        List<Object> valueList = (List<Object>) value;
                        for (Object v : valueList) {
                            final var result = travelBase64Decode(v, val);
                            newList.add(result);
                        }
                        return newList;
                    } else if ("*".equals(key) && value instanceof Map) {
                        Map<String, Object> valueMap = (Map<String, Object>) value;
                        for (var e : valueMap.entrySet()) {
                            final var result = travelBase64Decode(e.getValue(), val);
                            if (result != null) {
                                valueMap.put(e.getKey(), result);
                            }
                        }
                    } else if (value instanceof Map) {
                        Map<String, Object> valueMap = (Map<String, Object>) value;
                        final var result = travelBase64Decode(valueMap.get(key), val);
                        if (result != null) {
                            valueMap.put(key, result);
                        }
                    } else {
                        throw new IllegalArgumentException("Invalid bytes path: " + key + " for value: " + value);
                    }
                }
            }
            return null;
        } else if (Boolean.TRUE.equals(bytesPaths) && (value instanceof String || value == null)) {
            if (value == null) {
                return null;
            }
            byte[] decodedValue = Base64.getDecoder().decode(((String) value).getBytes());
            return decodedValue;
        } else {
            throw new IllegalArgumentException("Invalid bytes path: " + bytesPaths + " for value: " + value + " of type " + value.getClass());
        }
    }
}