package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.msgpack.jackson.dataformat.MessagePackExtensionType;

import static io.github.brenbar.uapi.internal.PackMap.packMap;
import static io.github.brenbar.uapi.internal.Pack.pack;

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

        final var keyIndexMap = new HashMap<Integer, _BinaryPackNode>();
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
