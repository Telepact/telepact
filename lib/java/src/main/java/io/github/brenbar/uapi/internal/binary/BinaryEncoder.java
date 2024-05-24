package io.github.brenbar.uapi.internal.binary;

import java.util.List;

public interface BinaryEncoder {
    List<Object> encode(List<Object> message);

    List<Object> decode(List<Object> message);
}