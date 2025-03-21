package io.github.telepact.internal.binary;

import static io.github.telepact.internal.binary.EncodeKeys.encodeKeys;

import java.util.Map;

public class EncodeBody {
    static Map<Object, Object> encodeBody(Map<String, Object> messageBody, BinaryEncoding binaryEncoder) {
        return (Map<Object, Object>) encodeKeys(messageBody, binaryEncoder);
    }
}
