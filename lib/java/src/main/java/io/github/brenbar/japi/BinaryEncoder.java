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
        this.decodeMap = binaryEncoding.entrySet().stream().collect(Collectors.toMap(e -> e.getValue(), e -> e.getKey()));
        this.binaryHash = binaryHash;
    }

    public List<Object> encode(List<Object> japiMessage) {
        var encodedMessageType = encodeValue(japiMessage.get(0), encodeMap);
        var headers = japiMessage.get(1);
        var encodedBody = encodeValue(japiMessage.get(2), encodeMap);
        return List.of(encodedMessageType, headers, encodedBody);
    }

    public List<Object> decode(List<Object> japiMessage) throws IncorrectBinaryHash {
        var decodedMessageType = decodeValue(japiMessage.get(0), decodeMap);
        var headers = (Map<String, Object>) japiMessage.get(1);
        var givenHash = (Long) headers.get("_bin");
        var decodedBody = decodeValue(japiMessage.get(2), decodeMap);
        if (binaryHash != null && !Objects.equals(givenHash, binaryHash)) {
            throw new IncorrectBinaryHash();
        }
        return List.of(decodedMessageType, headers, decodedBody);
    }

    private Object encodeValue(Object given, Map<String, Long> encodeMap) {
        if (given instanceof Map<?,?> m) {
            return m.entrySet().stream().collect(Collectors.toMap(e -> encodeMap.get(e.getKey()), e -> encodeValue(e.getValue(), encodeMap)));
        } else if (given instanceof List<?> l) {
            return l.stream().map(e -> encodeValue(e, encodeMap));
        } else {
            return given;
        }
    }

    private Object decodeValue(Object given, Map<Long, String> decodeMap) {
        if (given instanceof Map<?,?> m) {
            return m.entrySet().stream().collect(Collectors.toMap(e -> decodeMap.get(e.getKey()), e -> decodeValue(e.getValue(), decodeMap)));
        } else if (given instanceof List<?> l) {
            return l.stream().map(e -> decodeValue(e, decodeMap));
        } else {
            return given;
        }
    }
}
