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

import static io.github.telepact.internal.binary.PackList.PACKED_BYTE;
import static io.github.telepact.internal.binary.PackMap.UNDEFINED_BYTE;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.msgpack.jackson.dataformat.MessagePackExtensionType;

public class UnpackList {
    static List<Object> unpackList(List<Object> list, List<Object> header) {
        if (list.isEmpty()) {
            return list;
        }

        if (!(list.get(0) instanceof final MessagePackExtensionType t && t.getType() == PACKED_BYTE)) {
            return list;
        }

        final var unpackedList = new ArrayList<Object>();
        for (int i = 1; i < list.size(); i += 1) {
            final var row = list.get(i);
            if (row instanceof final List<?> rowList) {
                unpackedList.add(unpackRow((List<Object>) rowList, header));
            } else {
                unpackedList.add(row);
            }
        }

        return unpackedList;
    }

    private static Map<Object, Object> unpackRow(List<Object> row, List<Object> header) {
        final var finalMap = new LinkedHashMap<Object, Object>();

        for (int index = 0; index < row.size(); index += 1) {
            if (index + 1 >= header.size()) {
                continue;
            }

            final var headerEntry = header.get(index + 1);
            final var value = row.get(index);

            if (value instanceof final MessagePackExtensionType t && t.getType() == UNDEFINED_BYTE) {
                continue;
            }

            if (headerEntry instanceof final List<?> nestedHeader && value instanceof final List<?> nestedRow) {
                if (!nestedHeader.isEmpty()) {
                    finalMap.put(nestedHeader.get(0), unpackRow((List<Object>) nestedRow, (List<Object>) nestedHeader));
                }
            } else {
                finalMap.put(headerEntry, value);
            }
        }

        return finalMap;
    }
}
