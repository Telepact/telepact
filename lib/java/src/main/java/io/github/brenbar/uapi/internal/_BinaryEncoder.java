package io.github.brenbar.uapi.internal;

import java.util.List;

public interface _BinaryEncoder {
    List<Object> encode(List<Object> message);

    List<Object> decode(List<Object> message);
}