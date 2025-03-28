package io.github.telepact.internal.binary;

import java.util.Base64;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public class ClientBase64Decode {

    public static void clientBase64Decode(List<Object> message) {
        Map<String, Object> headers = (Map<String, Object>) message.get(0);
        Map<String, Object> body = (Map<String, Object>) message.get(1);

        Map<String, Object> base64Paths = (Map<String, Object>) headers.get("@base64");

        base64Decode(body, base64Paths);
    }

    private static void base64Decode(Object given, Map<String, Object> base64Paths) {
        if (given instanceof Map) {
            Map<String, Object> givenMap = (Map<String, Object>) given;
            for (Map.Entry<String, Object> entry : givenMap.entrySet()) {
                String key = entry.getKey();
                Object value = entry.getValue();
                Object thisBase64Path = base64Paths.get(key);

                if (thisBase64Path == null) {
                    continue;
                }

                if (Objects.equals(thisBase64Path, true)) {
                    if (value instanceof String) {
                        byte[] decodedValue = Base64.getDecoder().decode((String) value);
                        givenMap.put(key, new String(decodedValue)); // Decoded value as String
                    }
                } else if (thisBase64Path instanceof Map) {
                    Map<String, Object> nestedBase64Paths = (Map<String, Object>) thisBase64Path;
                    base64Decode(value, nestedBase64Paths);
                }
            }
        } else if (given instanceof List) {
            List<Object> givenList = (List<Object>) given;
            for (Object item : givenList) {
                base64Decode(item, base64Paths);
            }
        }
    }
}