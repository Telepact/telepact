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
import static io.github.telepact.internal.binary.PackMap.packMap;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.msgpack.jackson.dataformat.MessagePackExtensionType;

public class PackList {

    public static final byte PACKED_BYTE = (byte) 17;

    static List<Object> packList(List<Object> list) {
        if (list.isEmpty()) {
            return list;
        }

        final var packedList = new ArrayList<Object>();
        final var header = new ArrayList<Object>();

        packedList.add(new MessagePackExtensionType(PACKED_BYTE, new byte[0]));

        header.add(null);

        packedList.add(header);

        final var keyIndexMap = new HashMap<Integer, BinaryPackNode>();
        try {
            for (final var e : list) {
                if (e instanceof final Map<?, ?> m) {
                    final var row = packMap(m, header, keyIndexMap);

                    packedList.add(row);
                } else {
                    // This list cannot be packed, abort
                    throw new CannotPack();
                }
            }
            return packedList;
        } catch (final CannotPack ex) {
            final var newList = new ArrayList<Object>();
            for (final var e : list) {
                newList.add(pack(e));
            }
            return newList;
        }
    }
}
