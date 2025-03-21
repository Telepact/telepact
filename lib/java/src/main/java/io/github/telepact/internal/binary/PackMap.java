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

import static io.github.telepact.internal.binary.Pack.pack;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.msgpack.jackson.dataformat.MessagePackExtensionType;

public class PackMap {

    public static final byte UNDEFINED_BYTE = (byte) 18;

    static List<Object> packMap(Map<?, ?> m, List<Object> header,
            Map<Integer, BinaryPackNode> keyIndexMap) throws CannotPack {
        final var row = new ArrayList<Object>();
        for (final var entry : m.entrySet()) {
            if (entry.getKey() instanceof final String s) {
                throw new CannotPack();
            }

            final var key = (Integer) entry.getKey();
            final var keyIndex = keyIndexMap.get(key);

            final BinaryPackNode finalKeyIndex;
            if (keyIndex == null) {
                finalKeyIndex = new BinaryPackNode(header.size() - 1, new HashMap<>());

                if (entry.getValue() instanceof Map<?, ?>) {
                    header.add(new ArrayList<>(List.of(key)));
                } else {
                    header.add(key);
                }

                keyIndexMap.put(key, finalKeyIndex);
            } else {
                finalKeyIndex = keyIndex;
            }

            final Integer keyIndexValue = finalKeyIndex.value;
            final Map<Integer, BinaryPackNode> keyIndexNested = finalKeyIndex.nested;

            final Object packedValue;
            if (entry.getValue() instanceof Map<?, ?> m2) {
                final List<Object> nestedHeader;
                try {
                    nestedHeader = (List<Object>) header.get(keyIndexValue + 1);
                } catch (ClassCastException e) {
                    // No nesting available, so the data structure is inconsistent
                    throw new CannotPack();
                }

                packedValue = packMap(m2, nestedHeader, keyIndexNested);
            } else {
                if (header.get(keyIndexValue + 1) instanceof List) {
                    throw new CannotPack();
                }

                packedValue = pack(entry.getValue());
            }

            while (row.size() < keyIndexValue) {
                row.add(new MessagePackExtensionType(UNDEFINED_BYTE, new byte[0]));
            }

            if (row.size() == keyIndexValue) {
                row.add(packedValue);
            } else {
                row.set(keyIndexValue, packedValue);
            }
        }
        return row;
    }
}
