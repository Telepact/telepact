package io.github.brenbar.uapi.internal.binary;

import static io.github.brenbar.uapi.internal.binary.DecodeKeys.decodeKeys;

import java.util.Map;

public class DecodeBody {
    static Map<String, Object> decodeBody(Map<Object, Object> encodedMessageBody, BinaryEncoding binaryEncoder) {
        return (Map<String, Object>) decodeKeys(encodedMessageBody, binaryEncoder);
    }
}
