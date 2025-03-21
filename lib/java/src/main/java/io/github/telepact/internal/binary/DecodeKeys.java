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

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class DecodeKeys {
    static Object decodeKeys(Object given, BinaryEncoding binaryEncoder) {
        if (given instanceof Map<?, ?> m) {
            final var newMap = new HashMap<String, Object>();

            for (final var e : m.entrySet()) {
                final String key;
                if (e.getKey() instanceof final String s) {
                    key = s;
                } else {
                    key = (String) binaryEncoder.decodeMap.get(e.getKey());

                    if (key == null) {
                        throw new BinaryEncodingMissing(key);
                    }
                }
                final var encodedValue = decodeKeys(e.getValue(), binaryEncoder);

                newMap.put(key, encodedValue);
            }

            return newMap;
        } else if (given instanceof final List<?> l) {
            return l.stream().map(e -> decodeKeys(e, binaryEncoder)).toList();
        } else {
            return given;
        }
    }
}
