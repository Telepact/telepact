package io.github.telepact.internal.binary;

import java.util.Base64;
import java.util.List;
import java.util.Map;

public class ClientBase64Encode {

    public static void clientBase64Encode(List<Object> message) {
        if (message.size() > 1 && message.get(1) instanceof Map) {
            Map<String, Object> body = (Map<String, Object>) message.get(1);
            travelBase64Encode(body);
        }
    }

    private static void travelBase64Encode(Object value) {
        if (value instanceof Map) {
            Map<String, Object> map = (Map<String, Object>) value;
            for (Map.Entry<String, Object> entry : map.entrySet()) {
                Object val = entry.getValue();
                if (val instanceof byte[]) {
                    entry.setValue(Base64.getEncoder().encodeToString((byte[]) val));
                } else {
                    travelBase64Encode(val);
                }
            }
        } else if (value instanceof List) {
            List<Object> list = (List<Object>) value;
            for (int i = 0; i < list.size(); i++) {
                Object v = list.get(i);
                if (v instanceof byte[]) {
                    list.set(i, Base64.getEncoder().encodeToString((byte[]) v));
                } else {
                    travelBase64Encode(v);
                }
            }
        }
    }
}