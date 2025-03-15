package io.github.msgpact.internal.binary;

import java.util.List;

public interface BinaryEncoder {
    List<Object> encode(List<Object> message);

    List<Object> decode(List<Object> message);
}