package io.github.brenbar.uapi.internal;

import java.util.Map;

import static io.github.brenbar.uapi.internal.EncodeKeys.encodeKeys;

public class EncodeBody {
    static Map<Object, Object> encodeBody(Map<String, Object> messageBody, _BinaryEncoding binaryEncoder) {
        return (Map<Object, Object>) encodeKeys(messageBody, binaryEncoder);
    }
}
