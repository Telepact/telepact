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