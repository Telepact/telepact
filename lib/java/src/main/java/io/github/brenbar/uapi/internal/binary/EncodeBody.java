package io.github.brenbar.uapi.internal.binary;

import static io.github.brenbar.uapi.internal.binary.EncodeKeys.encodeKeys;

import java.util.Map;

public class EncodeBody {
    static Map<Object, Object> encodeBody(Map<String, Object> messageBody, BinaryEncoding binaryEncoder) {
        return (Map<Object, Object>) encodeKeys(messageBody, binaryEncoder);
    }
}
