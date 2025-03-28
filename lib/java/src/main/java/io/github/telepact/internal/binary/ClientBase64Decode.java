package io.github.telepact.internal.binary;

import java.util.Base64;
import java.util.List;
import java.util.Map;

public class ClientBase64Decode {

    public static void clientBase64Decode(List<Object> message) {
        System.out.println("Starting clientBase64Decode with message: " + message);
        Map<String, Object> headers = (Map<String, Object>) message.get(0);
        Map<String, Object> body = (Map<String, Object>) message.get(1);

        System.out.println("Extracted headers: " + headers);
        System.out.println("Extracted body: " + body);

        Map<String, Object> base64Paths = (Map<String, Object>) headers.getOrDefault("@base64_", Map.of());
        System.out.println("Base64 paths: " + base64Paths);

        travelBase64Decode(body, base64Paths);
    }

    private static Object travelBase64Decode(Object value, Object base64Paths) {
        System.out.println("travelBase64Decode called with value: " + value + ", base64Paths: " + base64Paths);

        if (base64Paths instanceof Map) {
            Map<String, Object> base64PathsMap = (Map<String, Object>) base64Paths;
            for (Map.Entry<String, Object> entry : base64PathsMap.entrySet()) {
                String key = entry.getKey();
                Object val = entry.getValue();

                System.out.println("Processing key: " + key + ", value: " + val);

                if (Boolean.TRUE.equals(val)) {
                    if ("*".equals(key) && value instanceof List) {
                        List<Object> valueList = (List<Object>) value;
                        for (int i = 0; i < valueList.size(); i++) {
                            System.out.println("Decoding list element at index " + i);
                            valueList.set(i, travelBase64Decode(valueList.get(i), val));
                        }
                    } else if ("*".equals(key) && value instanceof Map) {
                        Map<String, Object> valueMap = (Map<String, Object>) value;
                        for (Map.Entry<String, Object> subEntry : valueMap.entrySet()) {
                            System.out.println("Decoding map entry with key: " + subEntry.getKey());
                            valueMap.put(subEntry.getKey(), travelBase64Decode(subEntry.getValue(), val));
                        }
                    } else if (value instanceof Map) {
                        Map<String, Object> valueMap = (Map<String, Object>) value;
                        System.out.println("Decoding map value for key: " + key);
                        valueMap.put(key, travelBase64Decode(valueMap.get(key), val));
                    } else {
                        throw new IllegalArgumentException("Invalid base64 path: " + key + " for value: " + value);
                    }
                } else {
                    if ("*".equals(key) && value instanceof List) {
                        List<Object> valueList = (List<Object>) value;
                        for (Object v : valueList) {
                            System.out.println("Traversing list element: " + v);
                            travelBase64Decode(v, val);
                        }
                    } else if ("*".equals(key) && value instanceof Map) {
                        Map<String, Object> valueMap = (Map<String, Object>) value;
                        for (Object v : valueMap.values()) {
                            System.out.println("Traversing map value: " + v);
                            travelBase64Decode(v, val);
                        }
                    } else if (value instanceof Map) {
                        Map<String, Object> valueMap = (Map<String, Object>) value;
                        System.out.println("Traversing map value for key: " + key);
                        travelBase64Decode(valueMap.get(key), val);
                    } else {
                        throw new IllegalArgumentException("Invalid base64 path: " + key + " for value: " + value);
                    }
                }
            }
            return null;
        } else if (Boolean.TRUE.equals(base64Paths) && (value instanceof String || value == null)) {
            if (value == null) {
                System.out.println("Value is null, returning null");
                return null;
            }
            System.out.println("Decoding base64 string: " + value);
            final var result = Base64.getDecoder().decode(((String) value).getBytes());
            return result;
        } else {
            throw new IllegalArgumentException("Invalid base64 path: " + base64Paths + " for value: " + value);
        }
    }
}