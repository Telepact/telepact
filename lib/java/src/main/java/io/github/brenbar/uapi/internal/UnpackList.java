package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.List;

import org.msgpack.jackson.dataformat.MessagePackExtensionType;

import static io.github.brenbar.uapi.internal.Unpack.unpack;
import static io.github.brenbar.uapi.internal.UnpackMap.unpackMap;
import static io.github.brenbar.uapi.internal.PackList.PACKED_BYTE;

public class UnpackList {
    static List<Object> unpackList(List<Object> list) {
        if (list.isEmpty()) {
            return list;
        }

        if (!(list.get(0) instanceof final MessagePackExtensionType t && t.getType() == PACKED_BYTE)) {
            final var newList = new ArrayList<Object>();
            for (final var e : list) {
                newList.add(unpack(e));
            }
            return newList;
        }

        final var unpackedList = new ArrayList<Object>();
        final var headers = (List<Object>) list.get(1);

        for (int i = 2; i < list.size(); i += 1) {
            final var row = (List<Object>) list.get(i);
            final var m = unpackMap(row, headers);

            unpackedList.add(m);
        }

        return unpackedList;
    }
}
