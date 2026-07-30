//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
                } else if (e.getKey() instanceof final Number n) {
                    try {
                        key = binaryEncoder.decodeTable[n.intValue()];
                    } catch (RuntimeException ex) {
                        throw new BinaryEncodingMissing(e.getKey());
                    }
                } else {
                    throw new BinaryEncodingMissing(e.getKey());
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
