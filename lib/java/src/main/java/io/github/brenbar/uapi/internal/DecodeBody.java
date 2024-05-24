package io.github.brenbar.uapi.internal;

import java.util.Map;

import static io.github.brenbar.uapi.internal.DecodeKeys.decodeKeys;

public class DecodeBody {
    static Map<String, Object> decodeBody(Map<Object, Object> encodedMessageBody, _BinaryEncoding binaryEncoder) {
        return (Map<String, Object>) decodeKeys(encodedMessageBody, binaryEncoder);
    }
}
