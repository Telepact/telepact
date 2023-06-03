package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;

public class BinaryEncoder {

    public static class IncorrectBinaryHash extends Exception {}
    public final Map<String, Long> encodeMap;
    public final Map<Long, String> decodeMap;
    public final Object binaryHash;

    public BinaryEncoder(Map<String, Long> binaryEncoding, Object binaryHash) {
        this.encodeMap = binaryEncoding;
        this.decodeMap = binaryEncoding.entrySet().stream().collect(Collectors.toMap(e -> Long.valueOf(e.getValue()), e -> e.getKey()));
        this.binaryHash = binaryHash;
    }

    public List<Object> encode(List<Object> japiMessage) {
        var encodedMessageType = get(encodeMap, japiMessage.get(0));
        var headers = japiMessage.get(1);
        var encodedBody = encodeKeys(japiMessage.get(2));
        return List.of(encodedMessageType, headers, encodedBody);
    }

    public List<Object> decode(List<Object> japiMessage) throws IncorrectBinaryHash {
        var encodedMessageType = japiMessage.get(0);
        if (encodedMessageType instanceof Integer i) {
            encodedMessageType = Long.valueOf(i);
        }
        var decodedMessageType = get(decodeMap, encodedMessageType);
        var headers = (Map<String, Object>) japiMessage.get(1);
        var givenHash = (Long) headers.get("_bin");
        var decodedBody = decodeKeys(japiMessage.get(2));
        if (binaryHash != null && !Objects.equals(givenHash, binaryHash)) {
            throw new IncorrectBinaryHash();
        }
        return List.of(decodedMessageType, headers, decodedBody);
    }

    private Object encodeKeys(Object given) {
        if (given instanceof Map<?,?> m) {
            return m.entrySet().stream().collect(Collectors.toMap(e -> get(encodeMap, e.getKey()), e -> encodeKeys(e.getValue())));
        } else if (given instanceof List<?> l) {
            return l.stream().map(e -> encodeKeys(e)).toList();
        } else {
            return given;
        }
    }

    private Object decodeKeys(Object given) {
        if (given instanceof Map<?,?> m) {
            return m.entrySet().stream().collect(Collectors.toMap(e -> {
                var key = e.getKey();
                // TODO: Update the msgpack library to not coerce these ints to strings
                //       because now we have to coerce it back.
                if (key instanceof String s) {
                    key = Long.valueOf(s);
                }
                return get(decodeMap, key);
            }, e -> decodeKeys(e.getValue())));
        } else if (given instanceof List<?> l) {
            return l.stream().map(e -> decodeKeys(e)).toList();
        } else {
            return given;
        }
    }

    private Object get(Map<?,?> map, Object key) {
        var value = map.get(key);
        if (value == null) {
            throw new RuntimeException("Missing encoding for " + String.valueOf(key));
        }
        return value;
    }
}
