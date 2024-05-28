package uapi.internal.binary;

import static uapi.internal.binary.Pack.pack;

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
