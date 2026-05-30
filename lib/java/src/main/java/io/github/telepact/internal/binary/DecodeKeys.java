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
            final var newMap = new HashMap<String, Object>(m.size());

            for (final var e : m.entrySet()) {
                final String key;
                if (e.getKey() instanceof final String s) {
                    key = s;
                } else if (e.getKey() instanceof final Number n) {
                    try {
                        key = binaryEncoder.decodeTable[n.intValue()];
                    } catch (RuntimeException ex) {
                        throw new BinaryEncodingMissing(e.getKey());
                    }
                } else {
                    throw new BinaryEncodingMissing(e.getKey());
                }
                final var value = e.getValue();
                final var encodedValue = value instanceof Map<?, ?> || value instanceof List<?> ? decodeKeys(value, binaryEncoder) : value;

                newMap.put(key, encodedValue);
            }

            return newMap;
        } else if (given instanceof final List<?> l) {
            final var newList = new java.util.ArrayList<Object>(l.size());
            for (final var item : l) {
                newList.add(item instanceof Map<?, ?> || item instanceof List<?> ? decodeKeys(item, binaryEncoder) : item);
            }
            return newList;
        } else {
            return given;
        }
    }
}
