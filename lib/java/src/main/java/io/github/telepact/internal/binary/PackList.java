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

import static io.github.telepact.internal.binary.PackMap.UNDEFINED_BYTE;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import org.msgpack.jackson.dataformat.MessagePackExtensionType;

public class PackList {

    public static final byte PACKED_BYTE = (byte) 17;

    static List<Object> packList(List<Object> list, List<Object> header) {
        if (list.isEmpty()) {
            return list;
        }

        final var packedList = new ArrayList<Object>();
        packedList.add(new MessagePackExtensionType(PACKED_BYTE, new byte[0]));

        for (final var entry : list) {
            if (!(entry instanceof final Map<?, ?> mapValue)) {
                return list;
            }
            packedList.add(packRow((Map<Object, Object>) mapValue, header));
        }

        return packedList;
    }

    private static List<Object> packRow(Map<Object, Object> mapValue, List<Object> header) {
        final var row = new ArrayList<Object>(Collections.nCopies(header.size() - 1,
                new MessagePackExtensionType(UNDEFINED_BYTE, new byte[0])));

        for (int index = 1; index < header.size(); index += 1) {
            final var headerEntry = header.get(index);
            final var key = headerEntry instanceof final List<?> nestedHeader && !nestedHeader.isEmpty()
                    ? nestedHeader.get(0)
                    : headerEntry;

            if (!mapValue.containsKey(key)) {
                continue;
            }

            final var value = mapValue.get(key);
            if (headerEntry instanceof final List<?> nestedHeader && value instanceof final Map<?, ?> nestedMap) {
                row.set(index - 1, packRow((Map<Object, Object>) nestedMap, (List<Object>) nestedHeader));
            } else {
                row.set(index - 1, value);
            }
        }

        while (!row.isEmpty()
                && row.get(row.size() - 1) instanceof final MessagePackExtensionType t
                && t.getType() == UNDEFINED_BYTE) {
            row.remove(row.size() - 1);
        }

        return row;
    }
}
