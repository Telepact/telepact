//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package io.github.telepact.internal.binary;

import java.util.Base64;
import java.util.List;
import java.util.Map;

public class ServerBase64Encode {

    public static void serverBase64Encode(List<Object> message) {
        Map<String, Object> headers = (Map<String, Object>) message.get(0);
        Map<String, Object> body = (Map<String, Object>) message.get(1);

        Map<String, Object> base64Paths = (Map<String, Object>) headers.getOrDefault("@base64_", Map.of());

        travelBase64Encode(body, base64Paths);
    }

    private static Object travelBase64Encode(Object value, Object base64Paths) {
        if (base64Paths instanceof Map) {
            Map<String, Object> base64PathsMap = (Map<String, Object>) base64Paths;
            for (Map.Entry<String, Object> entry : base64PathsMap.entrySet()) {
                String key = entry.getKey();
                Object val = entry.getValue();

                if (Boolean.TRUE.equals(val)) {
                    if ("*".equals(key) && value instanceof List) {
                        List<Object> valueList = (List<Object>) value;
                        for (int i = 0; i < valueList.size(); i++) {
                            valueList.set(i, travelBase64Encode(valueList.get(i), val));
                        }
                    } else if ("*".equals(key) && value instanceof Map) {
                        Map<String, Object> valueMap = (Map<String, Object>) value;
                        for (Map.Entry<String, Object> valueEntry : valueMap.entrySet()) {
                            valueMap.put(valueEntry.getKey(), travelBase64Encode(valueEntry.getValue(), val));
                        }
                    } else if (value instanceof Map) {
                        Map<String, Object> valueMap = (Map<String, Object>) value;
                        valueMap.put(key, travelBase64Encode(valueMap.get(key), val));
                    } else {
                        throw new IllegalArgumentException("Invalid base64 path: " + key + " for value: " + value);
                    }
                } else {
                    if ("*".equals(key) && value instanceof List) {
                        List<Object> valueList = (List<Object>) value;
                        for (Object v : valueList) {
                            travelBase64Encode(v, val);
                        }
                    } else if ("*".equals(key) && value instanceof Map) {
                        Map<String, Object> valueMap = (Map<String, Object>) value;
                        for (Object v : valueMap.values()) {
                            travelBase64Encode(v, val);
                        }
                    } else if (value instanceof Map) {
                        Map<String, Object> valueMap = (Map<String, Object>) value;
                        travelBase64Encode(valueMap.get(key), val);
                    } else {
                        throw new IllegalArgumentException("Invalid base64 path: " + key + " for value: " + value);
                    }
                }
            }
            return null;
        } else if (Boolean.TRUE.equals(base64Paths) && (value instanceof byte[] || value == null)) {
            if (value == null) {
                return null;
            }
            return Base64.getEncoder().encodeToString((byte[]) value);
        } else {
            throw new IllegalArgumentException("Invalid base64 path: " + base64Paths + " for value: " + value);
        }
    }
}