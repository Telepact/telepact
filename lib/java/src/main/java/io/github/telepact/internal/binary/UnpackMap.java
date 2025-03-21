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
import static io.github.telepact.internal.binary.Unpack.unpack;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.msgpack.jackson.dataformat.MessagePackExtensionType;

public class UnpackMap {
    static Map<Integer, Object> unpackMap(List<Object> row, List<Object> header) {
        final var finalMap = new HashMap<Integer, Object>();

        for (int j = 0; j < row.size(); j += 1) {
            final var key = header.get(j + 1);
            final var value = row.get(j);

            if (value instanceof final MessagePackExtensionType t && t.getType() == UNDEFINED_BYTE) {
                continue;
            }

            if (key instanceof final List l) {
                final var nestedHeader = (List<Object>) l;
                final var nestedRow = (List<Object>) value;
                final var m = unpackMap(nestedRow, nestedHeader);
                final var i = (Integer) nestedHeader.get(0);

                finalMap.put(i, m);
            } else {
                final Integer i = (Integer) key;
                final var unpackedValue = unpack(value);

                finalMap.put(i, unpackedValue);
            }
        }

        return finalMap;
    }
}
